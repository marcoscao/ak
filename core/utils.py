
#
#
#

def log( msg ):
   print( msg )


def log_item( item, is_commented=False ):
   if is_commented:
      log( "  - add COMMENTED item: " + item )
   else:
      log( "  - add item: " + item )


def log_album( album ):
   log( "- add album: " + album )


def log_error( msg ):
   log( "*** " + msg )

