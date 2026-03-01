--------------------------------------------------------------------------------
ORIGINAL V0.7 (2022)

# plugin.audio.m3sr2019

MP3 Streams Reloaded

### Notes
  * Force fixed viewmode in settings if needed (default ids for Confluence, other skins will be different)
  * Seeking is not possible (server side)
  * Try not to queue everything at once, one album/artist at a time should be fine.
  * Kodi 18 PAPlayer can crash Kodi if something goes wrong with stream/server  
    To avoid this crash use different player for audio playback eg. VideoPlayer  
    advancedsettings.xml:  
```
    <audio>
    <defaultplayer>VideoPlayer</defaultplayer>
    </audio>
```
-----------------------------------------------------------------------------

Changes v2026.1

Fixes:

addon.xml declared three dependencies (script.module.six, script.module.kodi-six, script.module.future) that are Python 2/3 bridge libraries. Kodi 19 (Matrix) and later run Python 3.8 exclusively, and these modules may not be installed at all on modern Kodi systems — causing the plugin to fail at the dependency check before even loading.

default.py
Was importing from future.backports.urllib.parse and kodi_six instead of the standard library. In Python 3, urllib.parse has everything needed — quote, unquote — natively.
Hard crash: in musicmp3_search(), keyboardinput was only assigned inside the if keyboard.isConfirmed() block, but referenced unconditionally on the next line. If the user pressed Cancel on the keyboard dialog, this raised UnboundLocalError: name 'keyboardinput' is not defined and crashed the plugin. Fixed by initialising it to "" before the check.
xbmcaddon.Addon() was called twice — once for the addon variable, then again inline when building MEDIA_DIR. Wasteful and inconsistent; now reuses the single addon object.

musicmp3.py
Same future import issue.
DB connect crash: the plugin uses reuselanguageinvoker=true, meaning the same Python process can handle multiple route calls. Each call created a new musicMp3() object which called db.connect() — but the database was already connected from the previous call, raising OperationalError: Connection already open. Fixed with reuse_if_open=True.
boo() token bug: the hex padding slice was [len(d)-4:] which is logically inverted (for short hex strings it returns too many chars, for long ones too few). Fixed to [-4:] which correctly takes the last 4 characters.
Missing cookie guard in boo(): if the SessionId cookie wasn't present, it crashed with a bare KeyError. Now raises a clear RuntimeError with an explanation.
Bare except: in get_track() was swallowing everything including KeyboardInterrupt. Changed to except Track.DoesNotExist.
User-Agent string was Firefox 68 from 2019. Updated to Firefox 121 — many servers now reject very old UAs.
Missing Referer header on main_albums() requests (it was present on main_artists() but not here).

settings.xml was in the Kodi 18 format. Updated to the Kodi 19+ version="2" format.

Changes:





