<p align="center">
  <img src="title.png" alt="MP3 Streams Echoed" width="600">
</p>

<h1>MP3 Streams Echoed</h1>

<p><strong>A modern, fully Python‑3‑native rebuild of the classic MP3 Streams Reloaded and the original 2000's code.</strong></p>

<p>
This fork preserves the spirit of the original addon while replacing its aging Python 2/3 bridge code, fixing long‑standing crashes, modernizing the request + session pipeline, and expanding the UX with playlists, favourites, richer metadata, fanart, and visualizer control.
Every subsystem has been rewritten for Kodi 19+ with stability, maintainability, and predictable behavior as priorities.
</p>

<hr>

<h2>Summary of Changes Since v0.7 (2022)</h2>

<ul>
  <li>Fully removed all Python 2 compatibility layers; now 100% Python 3 native for Kodi 19+.</li>
  <li>Rebuilt request, parsing, routing, and session handling for modern Kodi and modern browsers.</li>
  <li>Fixed multiple crash conditions (keyboard cancel, DB reuse, routing errors, token generation).</li>
  <li>Added song search, favourites system, richer album metadata, and fanart support.</li>
  <li>Added album-level playlist building (Play Album / Shuffle Album) from any album listing.</li>
  <li>Added Shuffle Favourite Songs (home screen) with helpful messaging when track data isn’t cached yet.</li>
  <li>Added Toggle Visualizer context action (track context menu) with correct live window-state behavior.</li>
  <li>Introduced HTML caching with cache-poison detection + automatic recovery from stale-session login walls.</li>
  <li>Added session warmup, retry-on-empty, and HTTP backoff retries for transient failures.</li>
  <li>Modernized headers, User‑Agent, Referer logic, and CDN token generation.</li>
  <li>Replaced deprecated <code>setInfo()</code> calls with Kodi 19+ <code>InfoTagMusic</code> everywhere.</li>
  <li>Added new home screen entries, improved pagination visuals, and a reversible cache-clear tool.</li>
  <li>Stabilized playback routing, buffering behavior, and cookie persistence.</li>
</ul>

<hr>

<h2>Changelog</h2>

<h3>Original v0.7 (2022)</h3>

<p>
Base version of MP3 Streams Reloaded. Provided artist/album browsing, basic playback, and limited metadata.
Required fixed viewmodes and lacked modern Kodi compatibility.
</p>

<hr>

<h2>v2026.1 / v2026.1.1</h2>

<h3>Dependency & Compatibility Fixes</h3>
<ul>
  <li>Removed obsolete Python 2/3 bridge modules (<code>six</code>, <code>kodi-six</code>, <code>future</code>) from <code>addon.xml</code>.</li>
  <li>Replaced all <code>future.backports</code> and <code>kodi_six</code> imports with Python 3 standard library equivalents.</li>
  <li>Updated <code>settings.xml</code> to Kodi 19+ <code>version="2"</code> format.</li>
</ul>

<h3>default.py Fixes</h3>
<ul>
  <li>Corrected imports to use <code>urllib.parse</code>.</li>
  <li>Fixed crash when cancelling keyboard input (uninitialized variable).</li>
  <li>Consolidated duplicate <code>xbmcaddon.Addon()</code> calls.</li>
</ul>

<h3>musicmp3.py Fixes</h3>
<ul>
  <li>Fixed DB connection crash by enabling <code>reuse_if_open=True</code>.</li>
  <li>Corrected <code>boo()</code> padding logic (<code>[-4:]</code> instead of inverted slice).</li>
  <li>Added explicit cookie guard with clear error messaging.</li>
  <li>Replaced bare <code>except:</code> with <code>except Track.DoesNotExist</code>.</li>
  <li>Updated User‑Agent to Firefox 121.</li>
  <li>Added missing Referer header to <code>main_albums()</code>.</li>
</ul>

<h3>New Features</h3>
<ul>
  <li><strong>Song Search</strong> — new main menu entry using <code>all=songs</code> endpoint.</li>
  <li><strong>Clear Page Cache</strong> — wipes only the PageCache table, fully reversible.</li>
  <li><strong>Track Numbers</strong> — assigned automatically for proper album sequencing.</li>
</ul>

<h3>Efficiency Improvements</h3>
<ul>
  <li>Added 6‑hour HTML caching for listing pages (configurable).</li>
  <li>Consolidated album parsing into <code>_parse_album_report()</code>.</li>
  <li>Added settings for <code>page_size</code> and <code>request_timeout</code>.</li>
  <li>Fixed song search CSS class mismatch (<code>song__name--search</code>, etc.).</li>
</ul>

<hr>

<h2>v2026.1.3</h2>

<h3>Fixes</h3>
<ul>
  <li>Removed double‑rendered labels caused by mixing <code>[CR][COLOR]</code> formatting with <code>setInfo()</code>.</li>
  <li>Fixed RoutingError by moving all link passing to query string parameters and encoding <code>/</code> safely.</li>
</ul>

<hr>

<h2>v2026.1.5</h2>

<h3>Routing & Session Fixes</h3>
<ul>
  <li>Reworked play routing to avoid <code>.mp3</code> path ambiguity.</li>
  <li>Session refresh is now unconditional to avoid stale cookies.</li>
  <li>Album URL is now stored in DB and passed through to playback.</li>
  <li>Added <code>BufferingMode=1</code> to improve playback stability.</li>
  <li>Bumped addon version to match package.</li>
</ul>

<hr>

<h2>v2026.1.6</h2>

<h3>CDN & Metadata Fixes</h3>
<ul>
  <li>Corrected Referer handling for CDN validation.</li>
  <li>Switched all music metadata to InfoTagMusic to eliminate deprecation warnings.</li>
</ul>

<hr>

<h2>v2026.1.7</h2>

<h3>Token Format Update</h3>
<ul>
  <li>CDN token is now 16 hex characters (8+8), not 8.</li>
  <li><code>boo()</code> updated to return <code>format(a, '08x') + format(b, '08x')</code>.</li>
  <li>Referer reverted to site root based on verified browser behavior.</li>
</ul>

<hr>

<h2>v2026.2.0</h2>

<h3>Major Feature Expansion</h3>
<ul>
  <li><strong>InfoTagMusic Everywhere</strong> — unified metadata handling across all routes.</li>
  <li><strong>Favourites System</strong> — new DB table + three new home menu entries:
    <ul>
      <li>Favourite Albums</li>
      <li>Favourite Artists</li>
      <li>Favourite Songs</li>
    </ul>
  </li>
  <li><strong>Richer Album Metadata</strong> — genre, description, and year scraped and applied to all tracks.</li>
  <li><strong>Fanart Support</strong> — album art now used as fanart during playback.</li>
</ul>

<hr>

<h2>v2026.2.1</h2>

<h3>Playlist & UX Upgrades</h3>
<ul>
  <li><strong>Play Album / Shuffle Album</strong> — album context menu actions available from any listing (Top/New/Genre/Artist/Search). Fetches all tracks, builds a Kodi PlayList, and starts immediately (no need to open the album first).</li>
  <li><strong>Shuffle Favourite Songs</strong> — new home screen item (uses <code>mixfavouritesongs.jpg</code>) that builds a shuffled playlist from saved favourite songs and starts playback.</li>
  <li><strong>Launch Visualizer</strong> — track context menu action that opens Kodi’s visualizer window (<code>ActivateWindow(Visualisation)</code>).</li>
  <li><strong>Next page icon</strong> — pagination items now display <code>nextpage.jpg</code> instead of a blank square.</li>
</ul>

<hr>

<h2>v2026.2.2</h2>

<h3>Visualizer Behavior Fix</h3>
<ul>
  <li><strong>Toggle Visualizer</strong> — replaces Launch Visualizer with a proper toggle routed through a new <code>/viz/toggle</code> endpoint.</li>
  <li>Checks <code>Window.IsActive(visualisation)</code> each invocation: opens if closed, closes via <code>Action(Back)</code> if open.</li>
</ul>

<hr>

<h2>v2026.3.0</h2>

<h3>No-results Bug Fully Addressed</h3>
<ul>
  <li><strong>Cache poison detection</strong> — cached pages are validated for parseable content (album/artist/song elements). Poisoned entries are deleted and re-fetched.</li>
  <li><strong>Never cache bad pages</strong> — live-fetched pages are only written to cache if they pass the same content validation.</li>
  <li><strong>Session warmup</strong> — <code>_cached_get</code> checks <code>_has_valid_session()</code> before listing requests and refreshes if needed.</li>
  <li><strong>Retry on empty</strong> — if a live fetch returns no content, the session is refreshed and the request is retried once.</li>
  <li><strong>HTTP retries with backoff</strong> — <code>_fetch_live()</code> retries up to 3 times with increasing delay on transient network errors or 5xx responses (4xx does not retry).</li>
  <li><strong>Cookies saved eagerly</strong> — cookies are saved after every successful fetch (no longer relying on <code>__del__</code> under <code>reuselanguageinvoker=true</code>).</li>
  <li><strong>User-visible errors</strong> — routes are wrapped with error handling so failures show a red toast notification instead of a silent empty directory.</li>
</ul>

<hr>
