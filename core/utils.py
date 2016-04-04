import os
from xml.dom.minidom import *


class FileManager:   

   #
   # concatenate path and file
   # note that a_file shouldn't start with '/'
   #
   @staticmethod
   def full_path( a_path, a_file ):
      #f_full = a_work_folder + "/" + local_file
      #return f_full
      return os.path.join( a_path, a_file )


   #
   # concatenate folders ( note: not folder + file )
   #
   @staticmethod
   def concat_folder( a_path_1, a_folder ):
      if a_path_1.endswith('/'):
         a_path_1 = a_path_1[:-1]

      if a_folder.startswith('/'):
         a_folder = a_folder[1:]

      return a_path_1 + "/" + a_folder


   #
   # add end slash
   #
   @staticmethod
   def add_end_slash( folder ):
      if folder.endswith('/'):
         folder = folder[:-1]
      return folder


   #
   # add start slash
   #
   @staticmethod
   def add_start_slash( folder ):
      if folder.startswith('/'):
         folder = folder[1:]
      return folder

   

   #
   # retrieves basename from a full path file
   #
   @staticmethod
   def file_basename( a_full_path ):
      name, ext = os.path.splitext( a_full_path )
      return name


   #
   # retrieves extension from a full path file
   #
   @staticmethod
   def file_extension( a_full_path ):
      name, ext = os.path.splitext( a_full_path )
      return ext


   #
   # Retrieves size in bytes from a full_path file
   # @return file size, None or exception
   #
   @staticmethod
   def file_size( f_full ):
      f_size = None
      
      # some microsd files gives access errors
      try:
         f_size = os.path.getsize(f_full)
      except:
         #print("Something wrong getting size of: " + f_full )
         log_error( "Something wrong getting size of: " + f_full )
         raise

      finally:
         return f_size


   #
   # file size overload ( passing file and path separated )
   #
   @staticmethod
   def local_file_size( a_path, a_file ):
      return FileManager.file_size( FileManager.full_path( a_path, a_file ) )

   
   #
   # Retrieves file date
   # @date_type specifies which date type
   #     "c"   -> means creation date
   #     "m"   -> means modified date
   #
   @staticmethod
   def file_date( f_full, date_type ):

      f_date = None
      
      try:
         if date_type == "c":
            f_date = os.path.getctime(f_full)
         elif date_type == "m":
            f_date = os.path.getmtime(f_full)
      except:
         #print("Something wrong getting creation date of: " + f_full )
         log_error( "Something wrong getting date of: " + f_full )
         raise

      finally:
         return f_date




#
# Manages xml: creation, update, ...
#
class XmlManager:

   xml_file_version = "01.01.013"


   def __init__( self, work_folder, local_file ):
      self.xml_doc = None



   def create( self ):
      if self.xml_doc != None:
         core.utils.log_error("Oops! can't create a non null xml document")
         return

      self.xml_doc = Document()
      self.xml_root = xml_doc.createElement("root")
      self.xml_doc.appendChild( xml_root )
   
      self.add_attribute( self.xml_root, "version", xml_file_version )



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



class Log:

   verbose_mode = True

   #
   #
   #
   @staticmethod
   def log( msg, a_vm = verbose_mode ):
      if a_vm:
         print( msg )


   #
   # Error msg
   #
   @staticmethod
   def log_error( msg ):
      Log.log( "ERROR : " + msg )


   #
   # Shows a critical error
   #
   def log_critical_error( msg ):
      Log.log( "CRITICAL_ERROR : " + msg, True )






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




