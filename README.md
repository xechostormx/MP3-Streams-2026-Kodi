<p align="center">
  <img src="title.png" alt="MP3 Streams Echoed" width="600">
</p>

<h1>MP3 Streams Echoed</h1>

<p><strong>A modern, fully Python‑3‑native rebuild of the classic MP3 Streams Reloaded and its early‑2000s codebase.</strong></p>

<p>
MP3 Streams Echoed preserves the original browsing and playback experience while replacing every internal subsystem with a stable, maintainable, Kodi‑19+ architecture. What began as a compatibility repair became a full modernization: all Python 2/3 bridge code removed, request and session handling rebuilt, long‑standing crashes fixed, and the UX expanded with playlists, favourites, richer metadata, fanart, and visualizer control.
</p>

<p>
The addon now behaves predictably across all routes, with hardened parsing, resilient caching, correct session lifecycle management, and consistent <code>InfoTagMusic</code> metadata throughout.
</p>

<hr>

<h2>Summary of Changes Since v0.7 (2022)</h2>

<ul>
  <li>100% Python 3 native; all legacy compatibility layers removed.</li>
  <li>Modernized request, parsing, routing, and session handling.</li>
  <li>Fixed multiple crash conditions (keyboard cancel, DB reuse, routing, token generation).</li>
  <li>Added song search, favourites system, richer album metadata, and fanart support.</li>
  <li>Album‑level playlist building (Play Album / Shuffle Album) from any listing.</li>
  <li>Shuffle Favourite Songs as a one‑click home screen action.</li>
  <li>Global Toggle Visualizer action with correct window‑state handling.</li>
  <li>Resilient HTML caching with poison detection and automatic recovery.</li>
  <li>Session warmup, retry‑on‑empty, and HTTP backoff retries.</li>
  <li>Unified <code>InfoTagMusic</code> metadata; deprecated <code>setInfo()</code> fully removed.</li>
  <li>Improved pagination visuals, buffering behavior, and cookie persistence.</li>
</ul>

<hr>

<h2>Changelog</h2>

<h3>Original v0.7 (2022)</h3>
<p>
Base version of MP3 Streams Reloaded. Provided artist and album browsing with basic playback and limited metadata. Relied on fixed viewmodes and legacy Python compatibility layers.
</p>

<hr>

<h2>v2026.1 – v2026.1.7</h2>

<h3>Foundation & Compatibility</h3>
<ul>
  <li>Removed all Python 2/3 bridge modules and deprecated dependencies.</li>
  <li>Updated settings and metadata handling for Kodi 19+.</li>
  <li>Fixed multiple crash paths and routing errors.</li>
  <li>Modernized headers, User‑Agent, Referer logic, and CDN token generation.</li>
</ul>

<h3>Core Improvements</h3>
<ul>
  <li>Added first‑class song search.</li>
  <li>Introduced HTML caching with configurable TTL.</li>
  <li>Consolidated and hardened album parsing.</li>
  <li>Stabilized playback routing and improved buffering behavior.</li>
</ul>

<hr>

<h2>v2026.2.0</h2>

<h3>Major Feature Expansion</h3>
<ul>
  <li>Unified metadata handling using <code>InfoTagMusic</code> across all routes.</li>
  <li>Added favourites system (albums, artists, songs).</li>
  <li>Expanded album metadata (genre, year, description).</li>
  <li>Added fanart support during playback.</li>
</ul>

<hr>

<h2>v2026.2.1 – v2026.2.2</h2>

<h3>Playlist & UX Enhancements</h3>
<ul>
  <li>Play Album / Shuffle Album actions available from any album listing.</li>
  <li>Shuffle Favourite Songs home screen entry.</li>
  <li>Visualizer upgraded to a proper toggle with live window‑state detection.</li>
  <li>Improved pagination visuals.</li>
</ul>

<hr>

<h2>v2026.3.0 – v2026.3.2</h2>

<h3>Stability & Correctness Pass</h3>
<ul>
  <li>Resolved silent “no results” failures caused by stale sessions and poisoned cache entries.</li>
  <li>Validated cache entries for real content before use or storage.</li>
  <li>Enforced session refresh before all listing and search requests.</li>
  <li>Added retry logic for transient network and mid‑session expiry failures.</li>
  <li>Corrected album parsing to match actual page structure across all listings.</li>
  <li>Replaced silent empty directories with user‑visible error notifications.</li>
</ul>

<hr>

<h2>v2026.3.3 – v2026.3.7</h2>

<h3>Deep Bug Fixes</h3>
<ul>
  <li>Artists were present but not visible in some skins; fixed by adding <code>setLabel2(artist)</code> to album ListItems.</li>
  <li>Audit pass fixed several silent issues: duplicate <code>_ensure_session</code> definition, log object used before initialization, artist parsing pulling nav/header links, login‑wall pages misdetected, and song search overwriting stored <code>album_url</code> values.</li>
  <li>Artist pages returned zero albums due to requiring fields that don’t exist on artist pages; made those fields optional.</li>
  <li>Diagnostic build added deep debug logging and temporary URL‑filtering fallbacks.</li>
  <li>Root cause fixes: corrected artist URL pattern (<code>/artist_name.html</code> instead of directory paths) and capped unpaginated song search results to avoid Kodi refusing to render massive lists.</li>
</ul>

<hr>

<h2>v2026.3.11</h2>

<h3>Music Virtualizer Toggle</h3>
<ul>
  <li>Added a <strong>Music Virtualizer</strong> context menu entry to all song items (search results and album track listings).</li>
  <li>Uses JSON-RPC <code>audiooutput.stereoupmix</code> to read the current state once per directory load and write it on toggle. Label reflects live state: <em>Music Virtualizer: ON [toggle off]</em> or <em>Music Virtualizer: OFF [toggle on]</em>.</li>
  <li>Falls back to a neutral label if the setting is unavailable on the current hardware or Kodi build.</li>
  <li>New route: <code>/virt/toggle</code>. New helper: <code>_virt_label()</code>.</li>
</ul>

<hr>

<h2>v2026.3.8 – v2026.3.10</h2>

<h3>UX & Logging Polish</h3>
<ul>
  <li>Debug logging level lowered from <code>DEBUG</code> to <code>WARNING</code> for production use. Flip <code>basicConfig(level=logging.WARNING)</code> back to <code>DEBUG</code> in <code>default.py</code> to re-enable verbose output.</li>
  <li>Context menu labels for the favourites system renamed to avoid confusion with Kodi's own built-in "Add to Favourites" action, which saves plugin entry points rather than song/album/artist data.</li>
  <li>Labels are now kind-specific: <strong>Save to My Songs</strong>, <strong>Save to My Albums</strong>, <strong>Save to My Artists</strong> with matching <strong>Remove from …</strong> entries.</li>
  <li>Song items now show both Save and Remove entries simultaneously in the context menu, so you can add or remove without first checking whether the song is already saved.</li>
  <li>Album and artist items continue to show one entry at a time (Save or Remove) based on current saved state.</li>
  <li>Toast notifications updated to match: <em>"Saved to My Songs: Title"</em> on add, <em>"Removed from saved list."</em> on remove.</li>
</ul>

<hr>

<h2>v2026.3.10</h2>

<h3>Bug Fix — Large Album Crash</h3>
<ul>
  <li>Fixed a crash ("Too many SQL variables") when opening large albums such as remastered deluxe box sets with 100+ tracks.</li>
  <li>Root cause: SQLite enforces a limit of 999 bound variables per statement on older builds. <code>Track</code> has 8 fields, so a single <code>replace_many()</code> call fails at ~124 rows. Multi-disc box sets exceed this easily.</li>
  <li>Fix: new <code>_save_tracks()</code> helper in <code>musicmp3.py</code> chunks inserts at 100 rows at a time. Applied to both album track saves and song search saves.</li>
</ul>
