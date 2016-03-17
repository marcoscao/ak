
#
#
#

def log( msg, verbose_mode = True ):
   if verbose_mode:
      print( msg )


def log_item( item, is_commented=False, verbose = True ):
   if is_commented:
      log( "  - add COMMENTED item: " + item, verbose )
   else:
      log( "  - add item: " + item, verbose )


def log_album( album, verbose = True ):
   log( "- add album: " + album, verbose )


def log_error( msg, verbose = True ):
   log( "*** " + msg, verbose )

