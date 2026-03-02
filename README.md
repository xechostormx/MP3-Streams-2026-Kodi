<p align="center">
  <img src="title.png" alt="MP3 Streams Echoed" width="600">
</p>

<h1>MP3 Streams Echoed</h1>

<p><strong>A modern, fully Python‑3‑native rebuild of the classic MP3 Streams Reloaded and its original early‑2000s codebase.</strong></p>

<p>
MP3 Streams Echoed preserves the spirit and browsing experience of the original addon while completely replacing its aging internals.
What began as a compatibility repair evolved into a full architectural refresh focused on stability, correctness, and modern Kodi behavior.
</p>

<p>
All Python 2/3 bridge code has been removed, the request and session pipeline rebuilt, long‑standing crashes fixed, and the UX expanded with playlists, favourites, richer metadata, fanart, and visualizer control.
Every subsystem has been rewritten for Kodi 19+ with predictable behavior and maintainability as priorities.
</p>

<hr>

<h2>Summary of Changes Since v0.7 (2022)</h2>

<ul>
  <li>100% Python 3 native; all legacy compatibility layers removed.</li>
  <li>Modernized request, parsing, routing, and session handling.</li>
  <li>Fixed multiple crash conditions (keyboard cancel, DB reuse, routing, token generation).</li>
  <li>Added song search, favourites system, richer album metadata, and fanart support.</li>
  <li>Introduced album‑level playlist building (Play Album / Shuffle Album) from any listing.</li>
  <li>Added Shuffle Favourite Songs as a one‑click home screen action.</li>
  <li>Integrated a global Toggle Visualizer context action with correct window‑state handling.</li>
  <li>Implemented resilient HTML caching with poison detection and automatic recovery.</li>
  <li>Added session warmup, retry‑on‑empty, and HTTP backoff retries.</li>
  <li>Replaced deprecated <code>setInfo()</code> calls with Kodi 19+ <code>InfoTagMusic</code> everywhere.</li>
  <li>Improved pagination visuals, buffering behavior, and cookie persistence.</li>
</ul>

<hr>

<h2>Changelog</h2>

<h3>Original v0.7 (2022)</h3>

<p>
Base version of MP3 Streams Reloaded. Provided artist and album browsing with basic playback and limited metadata.
Relied on fixed viewmodes and legacy Python compatibility layers.
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
  <li>Song search added as a first‑class feature.</li>
  <li>HTML caching introduced with configurable TTL.</li>
  <li>Album parsing consolidated and hardened.</li>
  <li>Playback routing stabilized and buffering behavior improved.</li>
</ul>

<hr>

<h2>v2026.2.0</h2>

<h3>Major Feature Expansion</h3>
<ul>
  <li>Unified metadata handling using <code>InfoTagMusic</code> across all routes.</li>
  <li>Favourites system added (albums, artists, songs).</li>
  <li>Richer album metadata (genre, year, description).</li>
  <li>Fanart support during playback.</li>
</ul>

<hr>

<h2>v2026.2.1 – v2026.2.2</h2>

<h3>Playlist & UX Enhancements</h3>
<ul>
  <li>Play Album / Shuffle Album context actions available from any album listing.</li>
  <li>Shuffle Favourite Songs home screen entry.</li>
  <li>Visualizer integration upgraded to a proper toggle with live window‑state detection.</li>
  <li>Improved pagination visuals.</li>
</ul>

<hr>

<h2>v2026.3.0 – v2026.3.2</h2>

<h3>Stability & Correctness Pass</h3>
<ul>
  <li>Resolved silent “no results” failures caused by stale sessions and poisoned cache entries.</li>
  <li>Cache entries are now validated for real content before use or storage.</li>
  <li>Session refresh is enforced before all listing and search requests.</li>
  <li>Retry logic added for transient network and mid‑session expiry failures.</li>
  <li>Album parsing corrected to reflect actual page structure across all listings.</li>
  <li>User‑visible error notifications replace silent empty directories.</li>
</ul>

<hr>
