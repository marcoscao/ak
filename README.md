# ak
TODO:

ak_generate:
  - dump to xml every "chunk number" of albums


ak_sync:
  - sync_del removing from target those items not found in source xml
  - sync_upd copy new items found in the xml into target
  - identify failed source items names ( not found, error reading... )
  - identify failed target items names ( not copied maybe due to space or not mounted, ... )


ak_query:
   - query a built source xml file
   - list in a human readable
   - search for specific bpm, or interval
   - search for specific artist, album, song, ...
   - export album/artist/... to raw txt, import ...
   - comment, uncomment songs, albums, ...



core/utils:
   - also save log to file


general:
   - move xml management to core/xml



