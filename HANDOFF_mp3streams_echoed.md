# MP3 Streams Echoed — Full Handoff Document
## For next chat session continuation

---

## Project Identity

| Field | Value |
|---|---|
| Plugin name | MP3 Streams Echoed |
| Addon ID | `plugin.audio.m3sr2019` |
| Current version | **2026.3.7** |
| Authors | Echostorm / Claude |
| Original author | L2501 (v0.0.7 base) |
| Source site | https://musicmp3.ru/ |
| Platform | Kodi (Nexus / Matrix, Python 3) |
| User's Kodi path | `C:\Users\Echostorm\AppData\Roaming\Kodi\addons\plugin.audio.m3sr2019\` |
| User's archive path | `E:\Archive\` |

Latest deliverable: `plugin_audio_m3sr2019-2026_3_7.zip`

Previous transcript references:
- `/mnt/transcripts/2026-03-02-07-33-02-kodi-plugin-audit-2026-3-3.txt` — audit through v2026.3.3
- `/mnt/transcripts/2026-03-02-07-46-36-kodi-plugin-audit-fixes-2026-3-4-to-3-6.txt` — v2026.3.4 through v2026.3.6

---

## What This Plugin Is

A Kodi audio plugin that browses and streams music from musicmp3.ru. It started as a dead Python 2 plugin (v0.0.7) and was fully rebuilt across many sessions. It browses artists and albums by genre, supports search, saves favourites, plays or shuffles full albums directly from the listing, and streams tracks with CDN token authentication.

---

## File Structure

```
plugin.audio.m3sr2019/
├── addon.xml                          # Kodi metadata, version, dependencies
├── default.py                         # All routes / UI
├── resources/
│   ├── settings.xml                   # User-configurable settings
│   ├── media/                         # Icons, fanart, genre artwork
│   │   ├── fanart.jpg
│   │   ├── icon.png
│   │   ├── artists.jpg / topalbums.jpg / newalbums.jpg
│   │   ├── favouritealbums.jpg / favouriteartists.jpg / favouritesongs.jpg
│   │   ├── mixfavouritesongs.jpg      # Shuffle Favourite Songs
│   │   ├── nextpage.jpg               # More... pagination items
│   │   ├── searchartists/albums/songs.jpg
│   │   ├── clearplaylist.jpg
│   │   └── genre/                     # Per-genre and per-subgenre icons
│   └── lib/
│       ├── musicmp3.py                # All scraping, session, DB logic
│       ├── peewee.py                  # Bundled ORM (do not edit)
│       ├── isodate/                   # Bundled ISO 8601 duration parser
│       └── routing.py                 # Bundled URL router
```

---

## Dependencies (declared in addon.xml)

- `xbmc.python` >= 3.0.0
- `script.module.beautifulsoup4`
- `script.module.requests`
- `script.module.routing`

All other libraries (peewee, isodate) are bundled inside `resources/lib/`. Note: `routing` is **not** bundled — it is loaded from the Kodi addon `script.module.routing` declared in `addon.xml`.

---

## Settings (resources/settings.xml)

| ID | Type | Default | Description |
|---|---|---|---|
| `fixed_view_mode` | boolean | false | Force a specific Kodi view mode number |
| `albums_view_mode` | string | 513 | View mode number for album listings |
| `songs_view_mode` | string | 506 | View mode number for song/track listings |
| `page_size` | integer | 40 | Results per page (10–100) |
| `request_timeout` | integer | 15 | HTTP timeout in seconds (5–60) |
| `cache_hours` | integer | 6 | Page cache lifetime in hours (0 = disabled) |

---

## Architecture Overview

### default.py — Routes

All routing via the `routing` library. Query-string params used for all dynamic data (not path segments) to avoid slash-encoding issues.

| Route | Function | Description |
|---|---|---|
| `/` | `index()` | Home screen |
| `/favourites/<kind>` | `favourites(kind)` | Browse saved favourites (album/artist/song) |
| `/fav/add` | `fav_add()` | Context menu: save to favourites |
| `/fav/remove` | `fav_remove()` | Context menu: remove from favourites |
| `/favourites/shuffle_songs` | `shuffle_favourites()` | Play all favourite songs shuffled |
| `/viz/toggle` | `viz_toggle()` | Toggle Kodi visualizer on/off |
| `/musicmp3/play_album` | `play_album()` | Build playlist and play album immediately |
| `/musicmp3/clear_cache` | `musicmp3_clear_cache()` | Wipe PageCache table |
| `/musicmp3/albums_main/<sort>` | `musicmp3_albums_main(sort)` | Genre picker for album browse |
| `/musicmp3/albums_gnr/<sort>/<gnr>` | `musicmp3_albums_gnr(sort, gnr)` | Sub-genre picker |
| `/musicmp3/artists_main` | `musicmp3_artist_main()` | Genre picker for artist browse |
| `/musicmp3/artists_gnr/<gnr>` | `musicmp3_artists_gnr(gnr)` | Sub-genre picker for artists |
| `/musicmp3/main_albums/<section>/<gnr_id>/<sort>/<index>/dir` | `musicmp3_main_albums(...)` | Paginated album listing |
| `/musicmp3/main_artists/<gnr_id>/<index>/dir` | `musicmp3_main_artists(...)` | Paginated artist listing |
| `/musicmp3/artists_albums` | `artists_albums()` | All albums for one artist |
| `/musicmp3/search/<cat>` | `musicmp3_search(cat)` | Search (artists/albums/songs) |
| `/musicmp3/album` | `musicmp3_album()` | Track listing for one album |
| `/musicmp3/play` | `musicmp3_play()` | Resolve and play one track |

### Key helpers in default.py

- `_make_musicmp3()` — constructs `musicMp3` from settings, used by every route
- `_set_music_tag(li, ...)` — sets all MusicInfoTag fields via Kodi 19+ API (no deprecated `setInfo`)
- `_fav_context(api, kind, url, ...)` — returns Add/Remove favourites context menu entry
- `_album_context(album_url, label)` — returns Play Album + Shuffle Album context menu entries
- `_notify_error(msg)` — shows Kodi error toast and logs; called in every route's except block
- `_link_url(route_func, link)` — builds plugin URL with `?link=` query param
- `_get_link()` — reads `link` query param from current request
- `_page_size()` — reads `page_size` from addon settings

### Context menus present on:

- **Album items** (all listing views): ▶ Play Album, 🔀 Shuffle Album, Add/Remove Favourites
- **Artist items**: Add/Remove Favourites
- **Track items** (album view + song search): 🎬 Toggle Visualizer, 🔀 Shuffle Album, Add/Remove Favourites
- **Favourite items**: Remove from Favourites

---

## musicmp3.py — Library

### Database Models (SQLite via peewee, file: `tracks.db`)

**Track** — cached per-track metadata
Fields: `rel` (unique key, the hex ID), `track_id`, `image`, `duration`, `album`, `artist`, `title`, `album_url`

**Favourite** — user-saved items
Fields: `kind` (album/artist/song), `url` (unique), `label`, `thumb`, `artist`, `album`, `added_at`

**PageCache** — cached listing HTML
Fields: `url`, `params_hash`, `html`, `expires_at`
Composite unique index on `(url, params_hash)`

### Key Internal Methods

**`_has_valid_session()`** — checks cookie jar for non-empty SessionId. This is a local cookie-jar check only — it cannot detect a server-side session rejection. It is NOT called in any hot path for this reason. All listing fetches and searches call `_ensure_session()` unconditionally instead. Retained as a diagnostic/utility helper.

**`_ensure_session(referer_url=None)`** — GETs the base URL (or referer_url) to establish a fresh SessionId cookie, then saves cookies to disk. Called unconditionally before every listing fetch, search, and album_tracks call.

**`_page_has_content(soup)`** — validates that a parsed page is real content, not a login wall or redirect. Checks for:
- `class=album_report` — album grids on any listing or artist page
- `class=artist_preview` — search artist results
- `tr.song` — song rows in search results or album track pages
- `a[href^=/artist_]` — artist listing pages (URLs are `/artist_name.html`, note underscore prefix, NOT `/artist/name/` with slashes — **confirmed from live Kodi debug log 2026-03-02**)
- `a[href*=__album_]` — album links on artist pages (URLs are `/artist_name__album_title.html`, double underscore — **confirmed from live Kodi debug log 2026-03-02**)

Does NOT use bare `soup.find("a")` as fallback — login walls have anchor tags and that caused cache poisoning in earlier versions. Does NOT use a loose "any relative href" fallback — that was added in 2026.3.6 as a stopgap and removed in 2026.3.7 once the correct URL patterns were confirmed.

**`_fetch_live(url, params, headers)`** — executes HTTP GET with up to 3 retries and exponential backoff (1.5s, 3s). Does not retry on 4xx errors. Returns `(response, soup)`.

**`_cached_get(url, params, referer)`** — full caching layer:
1. Check PageCache; if hit, validate content before returning (detects poisoned cache)
2. Call `_ensure_session()` unconditionally
3. `_fetch_live()`
4. If empty page, refresh session and retry once
5. Only cache if `_page_has_content()` passes
6. Save cookies after every successful fetch

**`_parse_album_report(album_el)`** — CRITICAL: `name`/`image`/`link` are searched within `album_el` (inside the `div.album_report`). `artist`/`date`/`details` are searched on `album_el.parent` because they are **siblings** of the album_report div on the parent `<li>`. **Only `name`, `image`, and `link` are required** — `artist`, `date`, and `details` are optional and absent on artist pages (where the artist is the page owner). `artist_albums()` overrides the `artist` field with the page H1 anyway.

**`boo(track_id)`** — CDN token algorithm. Returns 16-char hex token (format: `format(a,'08x') + format(b,'08x')`). Old version used `[-4:]` trick giving 8-char tokens — site now requires 16. SessionId[8:] is used in the hash input.

**`play_url(track_id, rel, referer_url)`** — calls `_ensure_session()`, calls `boo()`, returns piped stream URL: `https://listen.musicmp3.ru/{token}/{rel}|seekable=0&verifypeer=false&User-Agent=...&Referer=https://musicmp3.ru/`

### Public API Methods

| Method | Description |
|---|---|
| `search(text, cat, limit=None)` | cat: "artists"/"albums"/"songs". `limit` caps song results (see Song Search Notes). Not cached. Refreshes session first. |
| `main_artists(gnr_id, start, count)` | Paginated artist list for a genre |
| `main_albums(section, gnr_id, sort, start, count)` | Paginated album list. section: ""/compilations/soundtracks |
| `artist_albums(url)` | All albums for an artist page URL |
| `album_tracks(url)` | Returns `(tracks, album_info)`. Always live (never cached). Saves cookies after fetch. |
| `get_track(rel)` | Retrieve Track from DB by rel key. Returns empty Track() if not found. |
| `add_favourite(kind, url, label, ...)` | Save to Favourite table |
| `remove_favourite(url)` | Delete from Favourite table |
| `is_favourite(url)` | Boolean check |
| `get_favourites(kind=None)` | Returns list of dicts, newest first. Pass kind to filter. |
| `clear_cache()` | Wipes PageCache table only. Does not touch Track or Favourite. |

---

## Song Search — Important Notes

The song search endpoint (`/search.html?text=QUERY&all=songs`) returns **all matching tracks in a single unaginated HTML response**. There is no server-side pagination for songs. A search for "blue" returned 9,832 `tr.song` rows in one page (confirmed in debug log 2026-03-02).

Without a cap, the plugin handed Kodi ~10,000 ListItems and Kodi silently rendered nothing. This was the cause of "search songs returns nothing."

**Current fix (v2026.3.7):** `search()` accepts a `limit` parameter. `musicmp3_search()` in default.py passes `_page_size()` as the limit when `cat == "songs"` and `None` for artists/albums (which already return bounded sets). The DB write is also capped — only the rows that will actually be displayed are written to Track.

**Still unknown:** Whether the top-N results returned by the site are the best matches or just arbitrary. The site appears to sort by relevance but this was not verified.

---

## CDN Authentication

The site at musicmp3.ru serves audio via CDN at `listen.musicmp3.ru`. Each stream URL requires a 16-char hex token computed from `track_id` and the `SessionId` cookie using the `boo()` algorithm.

- Session is established by GETting any musicmp3.ru page
- SessionId cookie is saved to `lwp_cookies.dat` in the plugin's user data dir
- Token format: `format(a, '08x') + format(b, '08x')` — 8+8 = 16 hex chars
- Referer header sent to CDN must be `https://musicmp3.ru/` (site root)
- Album art URLs are piped with `|User-Agent=...&Referer=...` for Kodi HTTP injection

---

## Site URL Patterns (confirmed from live Kodi debug log, 2026-03-02)

These were assumed and wrong until the debug log was analysed. They affect scraping logic throughout.

| Page type | URL pattern | Example |
|---|---|---|
| Artist profile page | `/artist_name.html` | `/artist_the-beatles.html` |
| Artist's album page | `/artist_name__album_title.html` | `/artist_rosalia__album_motomami.html` |
| Artist list by genre | `/main_artists.html?type=artist&page=N&gnr_id=NNN` | — |
| Search | `/search.html?text=QUERY&all=CAT` | `all=songs`, `all=artists`, `all=albums` |

**Key confirmed fact:** Artist listing pages use `href="/artist_name.html"` — the URL starts with `/artist_` (underscore), **not** `/artist/` (slash as directory separator). Any code that looks for `/artist/` in hrefs will find zero matches on these pages. This was the root cause of multiple broken features across v2026.3.4–3.6.

---

## Known Bugs Fixed (complete history)

| Version | Bug | Fix |
|---|---|---|
| 2026.1 | Python 2 syntax throughout | Full Python 3 migration |
| 2026.1 | Double text in album listings | Removed redundant label append |
| 2026.1 | Routing crash on album URLs with slashes | Switched all dynamic params to query strings |
| 2026.1.7 | CDN 404 on all tracks | `boo()` returned 8-char token; site now requires 16-char. Fixed `[-4:]` → `format(x,'08x')` |
| 2026.3 | Empty results after session expiry | `_cached_get` was caching login-wall HTML (200 OK). Added cache validation and unconditional session refresh |
| 2026.3.1 | Session retry bypass | `soup.find("a")` in `_page_has_content` let login walls pass. Replaced with specific href pattern checks |
| 2026.3.2 | Missing artist names everywhere | `_parse_album_report` searched inside `album_report` div for artist, but artist is a sibling on the parent `<li>`. Fixed to search `album_el.parent` |
| 2026.3.3 | Artist not visible in Kodi UI | Added `li.setLabel2(artist)` to all album ListItems; MusicInfoTag alone isn't shown by all skins |
| 2026.3.4 | Duplicate `_ensure_session` definition | Second (bare) definition after `boo()` silently shadowed the documented one. Removed. |
| 2026.3.4 | `log` used before definition in default.py | `import logging` / `log =` were 7 lines below `_notify_error`. Moved to top of file. |
| 2026.3.4 | `main_artists` scraped all `<a>` tags | `soup.find_all("a")` caught nav/header anchors, corrupting index math. Filtered to href containing `/artist/` (later found to also be wrong — see 2026.3.7). |
| 2026.3.4 | `main_albums` loop didn't break on login-wall | `if not soup.li:` would pass on login-wall pages (nav has `<li>`). Replaced with `_page_has_content()`. |
| 2026.3.4 | Song search overwrote `album_url` with blank | `Track.replace_many` in search had no `album_url` field. Now reads existing value from DB if cached, preserving it. |
| 2026.3.5 | Artist pages return zero albums | `_parse_album_report` required `artist_el` and `date_el` which are absent on artist pages. Made both optional; only `name`, `image`, `link` are required. |
| 2026.3.6 | `main_artists` `/artist/` filter never matched | Artist listing hrefs use `/artist_` prefix (underscore) not `/artist/` (directory). Added fallback to all internal links when zero `/artist/` links found. Loose fallback also added to `_page_has_content`. (Stopgap — proper fix in 2026.3.7.) |
| 2026.3.7 | `main_artists` still used wrong URL pattern | Removed `/artist/` filter and fallback entirely. Now correctly filters `href.startswith("/artist_")`. |
| 2026.3.7 | `_page_has_content` had wrong/dead URL patterns | Removed loose internal-link fallback. Replaced dead `/album/` href check (no such URL pattern) with `__album_` (confirmed double-underscore pattern from debug log). |
| 2026.3.7 | Song search showed nothing despite 9,832 matching rows | Site returns all songs in one unaginated response. Kodi silently fails with ~10k ListItems. Capped at `_page_size()` via new `limit` param on `search()`. |

---

## Known Remaining Issues (as of 2026.3.7)

The user reported search is still producing errors and there are a few other unspecified errors. A fresh debug log is needed to investigate these.

### 1. Search songs — still producing errors after 2026.3.7

The 9,832-row flood is fixed. However the user confirmed errors remain. Possible causes:

- The song rows returned may have a different HTML structure than expected — the scraper looks for `song__name--search`, `song__artist--search`, `song__album--search` classes. If those class names changed on the site, all rows would parse as empty.
- The play URL for search-result songs may fail — search result tracks are written to the Track DB with `track_id` values like `track1`, `track2` (sequential within the page), not stable IDs. If those IDs don't match what the play route expects, playback will fail silently.
- `album_url` for search-result songs may still be wrong — the search page shows songs without album context, so `album_url` is either blank or pulled from wherever it was last seen in the DB. A blank `album_url` passed to `play_url` may cause issues.

### 2. Other unspecified errors

No details captured. Recommend:
1. Install 2026.3.7
2. Enable Kodi debug logging: Settings → System → Logging → Enable debug logging
3. Reproduce each error systematically
4. Capture `kodi.log` sections containing `plugin.audio.m3sr2019`

**Note on log reading:** Python `logging.DEBUG` messages from this plugin appear labelled `error <general>` in Kodi's log. This is a Kodi log-level mapping quirk — the content is correct, the label is misleading. Don't skip lines labelled `error` that contain `DEBUG:resources.lib.musicmp3:` or `DEBUG:peewee:` — those are normal debug output.

---

## What Was NOT Implemented (known gaps)

- **Billboard/Charts** — media assets exist (`billboard/` folder, `billboardcharts.jpg`) but the scraper was never built
- **Add ID3 Tags** — `addid3tags.jpg` asset exists, feature never implemented
- **Compilations top-level menu** — `compilations.jpg` exists, not wired to home screen (accessible via genre browse)
- **Mix Favourite Albums** — `mixfavouritealbums.jpg` exists but only "Mix Favourite Songs" is implemented

---

## Session / Cookie Notes

- Cookie file: `{USER_DATA_DIR}/musicmp3/lwp_cookies.dat` (LWP format)
- DB file: `{USER_DATA_DIR}/musicmp3/tracks.db`
- `reuselanguageinvoker=true` in addon.xml means the Python process is reused across route calls; `__del__` is NOT called reliably between invocations. Cookies are saved eagerly after every fetch.
- The Track table persists across sessions and is never cleared by "Clear Cache" (which only clears PageCache). This means favourite songs can be played without re-fetching their albums, as long as they were fetched at least once.

---

## Version History Summary

| Version | Summary |
|---|---|
| 0.0.7 | Original L2501 release (Python 2, broken) |
| 2026.1 | Python 3 migration, song search, page cache, configurable settings |
| 2026.1.7 | CDN token fix (8→16 char) |
| 2026.2.0 | InfoTagMusic migration, Favourite system, richer album metadata, fanart on Now Playing |
| 2026.2.1 | Play Album/Shuffle Album context menus, Shuffle Favourite Songs, visualizer toggle |
| 2026.2.2 | Visualizer toggle (true toggle via window state check) |
| 2026.3.0 | Stability pass: cache poison detection, unconditional session refresh, retry logic, error toasts |
| 2026.3.1 | Fix `_page_has_content` bypass |
| 2026.3.2 | Fix missing artist names in `_parse_album_report` |
| 2026.3.3 | Fix artist not visible in Kodi: `setLabel2(artist)` |
| 2026.3.4 | Audit pass: duplicate `_ensure_session` removed; log ordering fixed; `main_artists` link filter; `main_albums` content check; song search preserves `album_url` |
| 2026.3.5 | Fix artist pages returning zero albums: optional artist/date in `_parse_album_report` |
| 2026.3.6 | Diagnostic build: debug logging throughout; loose fallbacks added as stopgap |
| 2026.3.7 | Fix confirmed from live debug log: correct `/artist_` URL pattern throughout; correct `__album_` pattern; song search capped at page_size |

---

## How to Start the Next Session

Tell Claude:

> "I'm continuing work on the MP3 Streams Echoed Kodi plugin. Read the handoff document first, then read the current source before doing anything."

Then upload:
- `HANDOFF_mp3streams_echoed.md` (this file)
- The current plugin zip or the two main source files: `default.py` and `resources/lib/musicmp3.py`
- A fresh `kodi.log` from reproducing whichever errors you want to fix

Source files to read before making any changes:
- `default.py`
- `resources/lib/musicmp3.py`
