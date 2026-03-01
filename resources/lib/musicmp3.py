# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 L2501
# v2026.1: feature update and efficiency pass
#
# Changes in v2026.1 vs v0.1.0 (the bug-fix release):
#
# NEW FEATURES
# ------------
# 1. Song search: the site's search endpoint accepts `all=songs`, which the old
#    plugin never used. search() now handles cat="songs" and returns track dicts
#    that can be played directly.
#
# 2. HTTP response caching (optional, controlled by the cache_hours setting):
#    A simple SQLite-backed cache stores page HTML keyed by URL + params.
#    This avoids re-fetching the same genre listing every single time you open
#    it. Cache entries expire after `cache_hours` hours. Set to 0 to disable.
#    The album_tracks table bypasses the cache (track pages change rarely but
#    we want fresh play tokens, so we always fetch those live).
#    Note: the cache stores raw HTML text, not parsed data. If the site changes
#    its structure, clearing the cache is enough to pick up the new layout.
#
# 3. Configurable page size: `count` is now driven by the `page_size` setting
#    (default 40) instead of being hardcoded. Callers pass it in.
#
# 4. Configurable request timeout: driven by the `request_timeout` setting.
#
# EFFICIENCY / CODE QUALITY
# -------------------------
# 5. Removed duplicated album-report parsing that appeared in search(), search(),
#    artist_albums(), and main_albums(). Now all go through _parse_album_report().
#
# 6. _parse_album_report() is None-safe: if a CSS class isn't found on the page
#    (site layout change), it logs a warning and returns None so the caller can
#    skip it, rather than crashing with AttributeError.
#
# 7. Session is now constructed once and stored; boo() and play_url() unchanged.
#
# 8. Cache table uses a composite index on (url, params_hash) for fast lookup.

import hashlib
import json
import logging
import os
import time
from urllib.parse import urljoin, quote as url_quote

import requests
from bs4 import BeautifulSoup
from http.cookiejar import LWPCookieJar

from .peewee import (
    SqliteDatabase, Model, CharField, TextField, IntegerField, FloatField
)
from . import isodate

log = logging.getLogger(__name__)

db = SqliteDatabase(None)


# --------------------------------------------------------------------------- #
# Database models
# --------------------------------------------------------------------------- #

class BaseModel(Model):
    class Meta:
        database = db


class Track(BaseModel):
    """Cached track metadata. Written when an album page is fetched."""
    rel       = CharField(unique=True)
    track_id  = TextField()
    image     = TextField()
    duration  = TextField()
    album     = TextField()
    artist    = TextField()
    title     = TextField()


class PageCache(BaseModel):
    """
    Optional HTML cache for genre/artist listing pages.
    Keyed by url + a hash of the query params dict.
    expires_at is a Unix timestamp (float). 0 means never expires.
    Cache is skipped entirely when cache_hours setting is 0.
    """
    url         = TextField()
    params_hash = TextField()
    html        = TextField()
    expires_at  = FloatField()

    class Meta:
        indexes = ((("url", "params_hash"), True),)   # unique index


# --------------------------------------------------------------------------- #
# Main API class
# --------------------------------------------------------------------------- #

class musicMp3:
    def __init__(self, cache_dir, timeout=15, cache_hours=6):
        """
        cache_dir   : path to the plugin's user-data directory (writable)
        timeout     : HTTP request timeout in seconds (from settings)
        cache_hours : how long to cache listing pages; 0 = no cache (from settings)
        """
        if not os.path.exists(cache_dir):
            cache_dir = os.getcwd()

        self.timeout = timeout
        self.cache_hours = cache_hours

        tracks_db_path  = os.path.join(cache_dir, "tracks.db")
        cookie_file_path = os.path.join(cache_dir, "lwp_cookies.dat")

        db.init(tracks_db_path)
        db.connect(reuse_if_open=True)
        db.create_tables([Track, PageCache], safe=True)

        self.base_url   = "https://musicmp3.ru/"
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
            "Gecko/20100101 Firefox/121.0"
        )

        self.s = requests.Session()
        self.s.cookies = LWPCookieJar(filename=cookie_file_path)
        self.s.headers.update({"User-Agent": self.user_agent})

        if os.path.isfile(cookie_file_path):
            self.s.cookies.load(ignore_discard=True, ignore_expires=True)

    def __del__(self):
        try:
            db.close()
        except Exception:
            pass
        try:
            self.s.cookies.save(ignore_discard=True, ignore_expires=True)
        except Exception:
            pass
        try:
            self.s.close()
        except Exception:
            pass

    # ----------------------------------------------------------------------- #
    # Internal helpers
    # ----------------------------------------------------------------------- #

    def _quote(self, s):
        return url_quote(s, safe="")

    def image_url(self, url):
        """Append Kodi HTTP header injection for album art requests."""
        return "{0}|User-Agent={1}&Referer={2}".format(
            url, self._quote(self.user_agent), self._quote(self.base_url)
        )

    def _params_hash(self, params):
        """Stable hash of a params dict for use as a cache key."""
        serialised = json.dumps(params, sort_keys=True)
        return hashlib.md5(serialised.encode()).hexdigest()

    def _cached_get(self, url, params=None, referer=None):
        """
        Fetch a URL, returning BeautifulSoup.
        If cache_hours > 0, check the PageCache table first.
        Cache misses fetch live and store the result.
        Always fetches live if cache_hours == 0.
        """
        params = params or {}
        headers = {"Referer": referer or self.base_url}
        p_hash = self._params_hash(params)

        if self.cache_hours > 0:
            try:
                entry = PageCache.get(
                    (PageCache.url == url) & (PageCache.params_hash == p_hash)
                )
                if entry.expires_at == 0 or entry.expires_at > time.time():
                    return BeautifulSoup(entry.html, "html.parser")
                # Expired — fall through to live fetch
                entry.delete_instance()
            except PageCache.DoesNotExist:
                pass

        r = self.s.get(url, params=params, headers=headers, timeout=self.timeout)
        r.raise_for_status()

        if self.cache_hours > 0:
            expires = time.time() + self.cache_hours * 3600
            PageCache.replace(
                url=url, params_hash=p_hash, html=r.text, expires_at=expires
            ).execute()

        return BeautifulSoup(r.text, "html.parser")

    def _parse_album_report(self, album_el):
        """
        Parse a single album_report element into a dict.
        Returns None if any required field is missing (site layout guard).
        """
        try:
            name_el    = album_el.find(class_="album_report__name")
            image_el   = album_el.find(class_="album_report__image")
            link_el    = album_el.find(class_="album_report__link")
            artist_el  = album_el.find(class_="album_report__artist")
            date_el    = album_el.find(class_="album_report__date")

            if not all([name_el, image_el, link_el, artist_el, date_el]):
                log.warning("album_report element missing expected fields — skipping")
                return None

            entry = {
                "title":       name_el.get_text(strip=True),
                "image":       image_el.get("src", ""),
                "link":        urljoin(self.base_url, link_el.get("href", "")),
                "artist_link": urljoin(self.base_url, artist_el.get("href", "")),
                "artist":      artist_el.get_text(strip=True),
                "date":        date_el.get_text(strip=True),
                "details":     "",
            }
            details_el = album_el.find(class_="album_report__details_content")
            if details_el:
                entry["details"] = details_el.get_text(strip=True)
            return entry
        except Exception as exc:
            log.warning("Failed to parse album_report: %s", exc)
            return None

    def boo(self, track_id):
        """
        Compute the CDN authentication token from track_id + session cookie.
        Raises RuntimeError if SessionId cookie is absent.
        """
        cookies = requests.utils.dict_from_cookiejar(self.s.cookies)
        if "SessionId" not in cookies:
            raise RuntimeError(
                "SessionId cookie not found — the site may require login, "
                "or the cookie file is empty/corrupt."
            )

        def int32(x):
            if x > 0xFFFFFFFF:
                raise OverflowError
            if x > 0x7FFFFFFF:
                x = int(0x100000000 - x)
                if x < 2147483648:
                    return -x
                else:
                    return -2147483648
            return x

        _in = track_id[5:] + cookies["SessionId"][8:]
        a, c, b = 1234554321, 7, 305419896
        for f in _in:
            f = ord(f) & 255
            a = int(int32((a ^ ((a & 63) + c) * f + a << 8) & 0xFFFFFFFF))
            b = int(b + (int32(b << 8 & 0xFFFFFFFF) ^ a))
            c = c + f
        a = int(a & 0x7FFFFFFF)
        b = int(b & 0x7FFFFFFF)
        return ("0000" + hex(a)[2:])[-4:] + ("0000" + hex(b)[2:])[-4:]

    def play_url(self, track_id, rel):
        """Build the streamable audio URL with CDN token and Kodi HTTP headers."""
        return (
            "https://listen.musicmp3.ru/{0}/{1}"
            "|seekable=0&verifypeer=false&User-Agent={2}&Referer={3}"
        ).format(
            self.boo(track_id),
            rel,
            self._quote(self.user_agent),
            self._quote(self.base_url),
        )

    # ----------------------------------------------------------------------- #
    # Public API methods
    # ----------------------------------------------------------------------- #

    def search(self, text, cat):
        """
        Search musicmp3.ru for artists, albums, or songs.
        cat: "artists" | "albums" | "songs"

        NEW in v2026.1: cat="songs" is now supported.
        Song results are returned as track dicts compatible with album_tracks()
        output, so the same Kodi list-item builder in default.py works for both.
        Song results are also written to the Track cache table.
        """
        params = {"text": text, "all": cat}
        # Search results are never cached — they change constantly and the user
        # typed something specific, so freshness matters more than speed here.
        r = self.s.get(
            "https://musicmp3.ru/search.html",
            params=params,
            headers={"Referer": self.base_url},
            timeout=self.timeout,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []

        if cat == "artists":
            for artist in soup.find_all(class_="artist_preview"):
                if artist.a:
                    results.append({
                        "artist": artist.a.get_text(strip=True),
                        "link":   urljoin(self.base_url, artist.a.get("href", "")),
                    })

        elif cat == "albums":
            for album in soup.find_all(class_="album_report"):
                entry = self._parse_album_report(album)
                if entry:
                    results.append(entry)

        elif cat == "songs":
            # Song results appear as .song elements inside the search results page.
            # Each has the same structure as on an album page, so we reuse the
            # same parsing logic as album_tracks().
            image_fallback = ""
            tracks = []
            for song in soup.find_all(class_="song"):
                try:
                    name_el     = song.find(itemprop="name")
                    artist_el   = song.find(itemprop="byArtist")
                    album_el    = song.find(itemprop="inAlbum")
                    duration_el = song.find(itemprop="duration")
                    img_el      = song.find("img")

                    if not all([name_el, artist_el, album_el, duration_el, song.a]):
                        continue

                    image = self.image_url(img_el.get("src", "")) if img_el else image_fallback
                    track = {
                        "title":    name_el.get_text(strip=True),
                        "artist":   artist_el.get("content", ""),
                        "album":    album_el.get("content", ""),
                        "duration": str(
                            isodate.parse_duration(
                                duration_el.get("content", "PT0S")
                            ).total_seconds()
                        ),
                        "image":    image,
                        "track_id": song.get("id", ""),
                        "rel":      song.a.get("rel", [""])[0],
                    }
                    tracks.append(track)
                except Exception as exc:
                    log.warning("Skipping song search result: %s", exc)

            if tracks:
                with db.atomic():
                    Track.replace_many(tracks).execute()
            results = tracks

        return results

    def main_artists(self, gnr_id, start, count):
        """
        Fetch a paginated list of artists for a genre.
        start : 0-based index into the full artist list
        count : max results to return
        """
        _page = 1 + start // 80
        results = []

        while len(results) < count:
            params = {"type": "artist", "page": _page}
            if gnr_id != "0":
                params["gnr_id"] = gnr_id

            soup = self._cached_get(
                "https://musicmp3.ru/main_artists.html", params=params
            )
            if not soup.a:
                break

            page_offset = (_page - 1) * 80
            for index, a in enumerate(soup.find_all("a"), page_offset):
                if len(results) >= count:
                    break
                if index >= start:
                    results.append({
                        "artist": a.get_text(strip=True),
                        "link":   urljoin(self.base_url, a.get("href", "")),
                    })
            _page += 1

        return results

    def main_albums(self, section, gnr_id, sort, start, count):
        """
        Fetch a paginated list of albums for a genre.
        section : "" | "compilations" | "soundtracks"
        sort    : "top" | "new"
        """
        _page = 1 + start // 40
        results = []

        while len(results) < count:
            params = {"sort": sort, "type": "album", "page": _page}
            if gnr_id != "0":
                params["gnr_id"] = gnr_id
            if section:
                params["section"] = section

            soup = self._cached_get("https://musicmp3.ru/main_albums.html", params=params)
            if not soup.li:
                break

            page_offset = (_page - 1) * 40
            for index, album_el in enumerate(soup.find_all(class_="album_report"), page_offset):
                if len(results) >= count:
                    break
                if index >= start:
                    entry = self._parse_album_report(album_el)
                    if entry:
                        results.append(entry)
            _page += 1

        return results

    def artist_albums(self, url):
        """Fetch all albums for an artist page URL."""
        soup = self._cached_get(url)
        h1 = soup.find(class_="page_title__h1")
        _artist = h1.get_text(strip=True) if h1 else ""
        results = []
        for album_el in soup.find_all(class_="album_report"):
            entry = self._parse_album_report(album_el)
            if entry:
                entry["artist"]      = _artist
                entry["artist_link"] = url
                results.append(entry)
        return results

    def album_tracks(self, url):
        """
        Fetch and parse the track listing for an album page.
        Always fetches live (no cache) — we need fresh session state for play tokens.
        Writes results to the Track table.
        """
        r = self.s.get(url, headers={"Referer": self.base_url}, timeout=self.timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        image_tag = soup.find(class_="art_wrap__img")
        image = self.image_url(image_tag.get("src")) if image_tag and image_tag.get("src") else ""

        tracks = []
        for song in soup.find_all(class_="song"):
            try:
                track = {
                    "title":    song.find(itemprop="name").get_text(strip=True),
                    "artist":   song.find(itemprop="byArtist").get("content", ""),
                    "album":    song.find(itemprop="inAlbum").get("content", ""),
                    "duration": str(
                        isodate.parse_duration(
                            song.find(itemprop="duration").get("content", "PT0S")
                        ).total_seconds()
                    ),
                    "image":    image,
                    "track_id": song.get("id", ""),
                    "rel":      song.a.get("rel", [""])[0],
                }
                tracks.append(track)
            except Exception as exc:
                log.warning("Skipping track in album_tracks: %s", exc)

        if tracks:
            with db.atomic():
                Track.replace_many(tracks).execute()

        return tracks

    def get_track(self, rel):
        """Retrieve cached Track by rel key. Returns empty Track() if not found."""
        try:
            return Track.get(Track.rel == rel)
        except Track.DoesNotExist:
            return Track()

    def clear_cache(self):
        """Delete all cached page entries. Safe to call at any time."""
        PageCache.delete().execute()


# --------------------------------------------------------------------------- #
# Genre ID table
# --------------------------------------------------------------------------- #

gnr_ids = [
    (
        "World",
        [
            ("World", "0"),
            ("Celtic", "3"),
            ("Jewish", "14"),
            ("Polynesian", "20"),
            ("African", "23"),
            ("Arabic", "79"),
            ("Brazilian", "93"),
            ("Caribbean", "135"),
            ("Turkish", "164"),
            ("Chinese", "169"),
            ("Japanese", "179"),
            ("Korean", "194"),
            ("South Asian", "200"),
            ("Spanish Folk", "212"),
            ("South American Folk", "220"),
            ("Slavic Folk", "229"),
            ("Nordic Folk", "241"),
            ("Italian Folk", "249"),
            ("French Folk", "252"),
            ("Balkan Folk", "259"),
            ("Latin", "268"),
            ("Compilations", "2"),
        ],
    ),
    (
        "Classical",
        [
            ("Classical", "313"),
            ("Baroque Period", "314"),
            ("Chamber", "315"),
            ("Choral", "316"),
            ("Classical Period", "317"),
            ("Medieval", "318"),
            ("Modern Classical", "326"),
            ("Opera", "343"),
            ("Orchestral", "348"),
            ("Renaissance", "352"),
            ("Romantic Period", "353"),
            ("Classical Crossover", "354"),
            ("Compilations", "313"),
        ],
    ),
    (
        "Metal",
        [
            ("Metal", "355"),
            ("Alternative Metal", "356"),
            ("Black Metal", "360"),
            ("Death Metal", "365"),
            ("Doom Metal", "373"),
            ("Folk Metal", "378"),
            ("Gothic Metal", "382"),
            ("Grindcore", "383"),
            ("Groove Metal", "386"),
            ("Heavy Metal", "387"),
            ("Industrial Metal", "389"),
            ("Metalcore", "391"),
            ("Neo-Classical Metal", "395"),
            ("Power Metal", "396"),
            ("Progressive Metal", "397"),
            ("Symphonic Metal", "398"),
            ("Thrash & Speed Metal", "399"),
            ("Sludge Metal", "404"),
            ("Glam Metal", "407"),
            ("Compilations", "355"),
        ],
    ),
    (
        "Alternative",
        [
            ("Alternative", "408"),
            ("Britpop", "409"),
            ("Dream Pop", "410"),
            ("Grunge", "412"),
            ("Indie Rock", "414"),
            ("Industrial Rock", "419"),
            ("Rap Rock", "420"),
            ("Garage Rock", "421"),
            ("Latin Alternative", "286"),
            ("Post-Punk", "424"),
            ("Emo", "431"),
            ("Punk Rock", "436"),
            ("Compilations", "408"),
        ],
    ),
    (
        "Rock",
        [
            ("Rock", "473"),
            ("Art Rock", "474"),
            ("Christian Rock", "481"),
            ("Comedy Rock", "482"),
            ("Folk Rock", "483"),
            ("Glam Rock", "489"),
            ("Hard Rock", "491"),
            ("Latin Rock", "292"),
            ("Progressive Rock", "494"),
            ("Psychedelic Rock", "500"),
            ("Rock & Roll", "507"),
            ("Southern Rock", "515"),
            ("Rockabilly", "516"),
            ("Compilations", "473"),
        ],
    ),
    (
        "R&B",
        [
            ("R&B", "517"),
            ("Contemporary R&B", "518"),
            ("Funk", "520"),
            ("Soul", "525"),
            ("Early R&B", "534"),
            ("Pop Soul", "537"),
            ("Neo-Soul", "538"),
            ("Compilations", "517"),
        ],
    ),
    (
        "Dance",
        [
            ("Dance", "539"),
            ("Teen Pop", "540"),
            ("Hi-NRG", "542"),
            ("Dance Pop", "543"),
            ("Electropop", "547"),
            ("Alternative Dance", "549"),
            ("Disco", "551"),
            ("Eurodance", "557"),
            ("Compilations", "539"),
        ],
    ),
    (
        "Pop",
        [
            ("Pop", "558"),
            ("Adult Contemporary", "559"),
            ("CCM", "560"),
            ("Euro Pop", "562"),
            ("French Pop", "564"),
            ("Indie Pop", "567"),
            ("Latin Pop", "291"),
            ("Pop Rock", "571"),
            ("Traditional Pop", "579"),
            ("New Wave", "582"),
            ("Easy Listening", "589"),
            ("Blue Eyed Soul", "595"),
            ("Compilations", "558"),
        ],
    ),
    (
        "Jazz",
        [
            ("Jazz", "596"),
            ("Acid Jazz", "597"),
            ("Free Jazz", "599"),
            ("Bebop", "600"),
            ("Big Band", "603"),
            ("Cool Jazz", "606"),
            ("Jazz Fusion", "607"),
            ("Soul Jazz", "610"),
            ("Swing", "611"),
            ("Vocal Jazz", "613"),
            ("Early Jazz", "614"),
            ("World Jazz", "622"),
            ("Compilations", "596"),
        ],
    ),
    (
        "Hip Hop",
        [
            ("Hip Hop", "623"),
            ("Alternative Hip Hop", "624"),
            ("Comedy Rap", "629"),
            ("East Coast Hip Hop", "630"),
            ("French Hip Hop", "631"),
            ("Hardcore Hip Hop", "632"),
            ("Instrumental Hip Hop", "637"),
            ("Political Hip Hop", "638"),
            ("Pop Rap", "639"),
            ("Religious Hip Hop", "640"),
            ("Southern Hip Hop", "644"),
            ("UK Hip Hop", "652"),
            ("West Coast Hip Hop", "653"),
            ("Compilations", "623"),
        ],
    ),
    (
        "Electronic",
        [
            ("Electronic", "654"),
            ("Breakbeat", "655"),
            ("Downtempo", "661"),
            ("Drum and Bass", "664"),
            ("EBM", "678"),
            ("Electro", "681"),
            ("Hardcore Techno", "686"),
            ("House", "698"),
            ("IDM", "717"),
            ("Indie Electronic", "718"),
            ("Techno", "720"),
            ("Trance", "728"),
            ("UK Garage", "737"),
            ("Ambient", "744"),
            ("Dubstep", "749"),
            ("Compilations", "654"),
        ],
    ),
    (
        "Country",
        [
            ("Country", "750"),
            ("Alternative Country", "751"),
            ("Contemporary Country", "755"),
            ("Country Pop", "756"),
            ("Traditional Country", "759"),
            ("Country Rock", "770"),
            ("Compilations", "750"),
        ],
    ),
    (
        "Blues",
        [
            ("Blues", "774"),
            ("Acoustic Blues", "775"),
            ("Electric Blues", "780"),
            ("Piano Blues", "784"),
            ("Blues Rock", "786"),
            ("Compilations", "774"),
        ],
    ),
    (
        "Soundtracks",
        [
            ("Soundtracks", "0"),
            ("Movie Soundtracks", "789"),
            ("TV Soundtracks", "792"),
            ("Game Soundtracks", "794"),
            ("Show Tunes", "796"),
            ("Spoken Word", "797"),
        ],
    ),
]
