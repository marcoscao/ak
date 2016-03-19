from xml.dom.minidom import *

#
# Manages xml: creation, update, ...
#
class xml_manager:

   version_value = "01.01.003"


   def __init__( self, work_folder, local_file ):
      self.xml_doc = None



   def create( self ):
      if self.xml_doc != None:
         core.utils.log_error("Oops! can't create a non null xml document")
         return

      self.xml_doc = Document()
      self.xml_root = xml_doc.createElement("root")
      self.xml_doc.appendChild( xml_root )
   
      self.add_attribute( self.xml_root, "version", version_value )



   #
   # note that changes will be lost if no saved previously
   #
   def close( self ):
      self.xml_doc.unlink();
      self.xml_doc = None



   #
   # Attempts to load and existing file
   #
   def load_from_file( self, full_filename ):
      if self.xml_doc != None:
         log_error( "can't not load from file an already open xml document" )
         return

      # check if target file exists
      if os.path.isfile( full_output_filename ) == False:
         log_critical_error( "can't load a not found file: " + full_filename )

      self.xml_doc = parse( full_filename )



   #
   # Returns node or None if not found
   #
   def find_node( self, node_name ):
      if self.xml_doc == None:
         log_error("can't not find within no created/loaded xml document")
         return

      for node in self.xml_doc.getElementsByTagName( node_name ):
         if node.tagName == node_name:
            return node

      return None



   #
   # return node for attrib_key = attrib_value
   #
   def find_node_by_value( self, parent_node, node_name, attrib_key, attrib_value ):
      for subnode in parent_node.GetElementsByTagName( node_name ):
         if subnode.getAttribute( attrib_key ) == attrib_value:
            return subnode
      return None



   #
   # Saves current data
   #
   def save( full_filename ):
      if self.xml_doc == None:
         log_error("can't not flush a non created/loaded xml document")
         return

      f = open( full_filename, 'w' )
      self.xml_doc.writexml( f, indent="  ", addindent="  ", newl='\n' )

      log( "\nData saved to XML file: " + full_filename )



   #
   # Creates a xml node with 1 attrib if passed
   # Returns created node
   #
   def create_node(self, node_name, attrib_id = None, attrib_value = None ):
      if self.xml_doc == None:
         log_error("can't not create node for a non created/loaded xml document")
         return

      xml_node = xml_doc.createElement( node_name )

      if attrib_id != None:
         self.add_attribute( xml_node, attrib_id, attrib_value )

      return xml_node



   def add_attribute(self, xml_node, attrib_id, attrib_value ):
      if xml_node == None:
         log_error("can't not add attributes over a null xml node")
         return

      xml_node.setAttribute( attrib_id, attrib_value )





#
# Log methods
#

def log( msg, verbose_mode = True ):
   if verbose_mode:
      print( msg )


def log_item( item, is_commented=False, verbose = True ):
   if is_commented:
      log( "  - COMMENTED item : " + item, verbose )
   else:
      log( "  - audio item : " + item, verbose )


def log_album( album, verbose = True ):
   log( "- found album: " + album, verbose )


def log_error( msg, verbose = True ):
   log( "*** " + msg, verbose )

def log_critical_error( msg ):
   log_error( "*** " + msg )
   raise




