<p align="center">
  <img src="title.png" alt="MP3 Streams Echoed" width="700">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Kodi-21%20Omega-1E8A70?style=flat-square&logo=kodi&logoColor=white" alt="Kodi 21">
  <img src="https://img.shields.io/badge/Python-3.8%2B-1E8A70?style=flat-square&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/version-2026.1.0-1E8A70?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-GPL--3.0-1E8A70?style=flat-square" alt="GPL-3.0">
</p>

<p align="center">
  <strong>A modern, fully Python-3-native rebuild of the classic MP3 Streams Reloaded.</strong><br>
  Browse and stream music from musicmp3.ru — rebuilt from scratch for Kodi 19+.
</p>

---

## What Is This

MP3 Streams Echoed preserves the original browsing and playback experience of MP3 Streams Reloaded while replacing every internal subsystem with a stable, maintainable, Kodi-19+ architecture. What began as a compatibility repair became a full modernisation: all Python 2/3 bridge code removed, session and request handling rebuilt, long-standing crashes fixed, and the UX expanded with playlists, favourites, richer metadata, fanart, and visualizer control.

The addon behaves predictably across all routes with hardened HTML parsing, resilient caching with poison detection, correct session lifecycle management, and consistent `InfoTagMusic` metadata throughout.

---

## Features

| | Feature | Notes |
|---|---|---|
| 🎵 | **Browse by Genre** | Full genre tree — Top and New albums by genre and sub-genre |
| 🎤 | **Browse by Artist** | Browse artists by genre, navigate to full album catalogues |
| 🔍 | **Search** | Search songs, albums, or artists |
| ⭐ | **Favourites** | Save/Remove albums, artists, and songs — persisted in SQLite |
| ▶️ | **Play / Shuffle Album** | Start playback from any album listing without opening it first |
| 🔀 | **Shuffle Favourites** | One-click home screen action to shuffle all saved songs |
| 🎬 | **Toggle Visualizer** | Context menu entry on all song items |
| 🔊 | **Music Virtualizer** | Toggle surround upmix via JSON-RPC; state-aware label |
| 🖼️ | **Fanart** | Album art fills the Now Playing background during playback |
| 💾 | **Page Cache** | HTML cache with configurable TTL and content validation |

---

## Requirements

- **Kodi** 19 (Matrix) or later — tested on Kodi 21 (Omega)
- **Python** 3.8+
- **Dependencies** — auto-resolved from the Kodi repository:
  - `script.module.beautifulsoup4`
  - `script.module.requests`
  - `script.module.routing`

---

## Installation

**Install from zip:**

1. Download the latest zip from [Releases](../../releases)
2. In Kodi: **Settings → Addons → Install from zip file**
3. Select the downloaded zip — Kodi resolves dependencies and installs automatically


## Changelog

### v2026.1.0 — Initial Release

Complete modernisation of the original MP3 Streams Reloaded v0.7 (2022) codebase. Version reset to 2026.1.0 for public release.

**Foundation**
- 100% Python 3 native — all Python 2/3 bridge modules removed
- Kodi 19+ metadata API (`InfoTagMusic`) throughout — deprecated `setInfo()` removed
- Fixed multiple crash paths and routing errors from the original codebase
- Modernised User-Agent, Referer logic, and CDN token generation

**Session & Caching**
- HTML cache with content validation — bad pages never enter the cache
- Cache poison detection — stale entries deleted and re-fetched live
- Session warmup and retry-on-empty before every listing and search request
- Cookie persistence after every successful fetch
- Exponential back-off retries on transient network and 5xx errors

**Features**
- Song search fully operational — `track_id` reconstructed from `rel` when site omits `tr id`
- Favourites system — Save/Remove for albums, artists, songs with kind-specific labels
- Play Album / Shuffle Album from any album listing without opening it first
- Shuffle Favourite Songs as a home screen action
- Toggle Visualizer with correct window-state detection
- Music Virtualizer toggle via JSON-RPC with state-aware context menu label
- Expanded album metadata (genre, year, description) on track ListItems
- Fanart during playback

**Correctness**
- `"Artist — Title"` label pattern applied across all listing routes for single-line skin compatibility
- `setAlbumArtist()` added alongside `setArtist()` so both fields are always populated
- `_find_album_sibling()` — ancestor-aware sibling search for genre page artist parsing
- Large album crash fixed — SQLite variable limit avoided by chunking inserts at 100 rows
- Artist page listings fixed — fields absent on artist pages are now optional

---

## License

GPL-3.0 — see [LICENSE](LICENSE)

---

<p align="center">
  <sub>github.com/xechostormx &nbsp;·&nbsp; Nexus: xechostormx</sub>
</p>
