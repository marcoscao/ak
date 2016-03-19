# ak
TODO:

ak_generate:
  - dump to xml every "chunk number" of albums
  - let user stop/cancel operation, saving until last or current complete album
  - update support
  - list failed items
  - make use of xml_manager
  - continue refactoring
  - log to file


ak_sync:
  - sync_del removing from target those items not found in source xml
  - sync_upd copy new items found in the xml into target
  - save failed source and target items names to a file ( not found, error reading, not copied due to not enough space or not mounted, ... )


ak_query:
   - query a built source xml file
   - list in a human readable
   - search for specific bpm, or interval
   - search for specific artist, album, song, ...
   - export album/artist/... to raw txt, import ...
   - comment, uncomment songs, albums, ...


core/utils:
   - also save log to file
   - conver log methods into a class
   - add SQLite support
   - make xml_manager usage
   - rename core to akc?


general:
   - move xml_management to a standalone core/xml
   


