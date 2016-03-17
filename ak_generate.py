import core.utils
import ntpath
import os
import sys
import optparse
import subprocess
import time
import fnmatch
import mutagen
from xml.dom.minidom import *
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
#from xml.dom import minidom


#
# Encapsulates file meta info data to build each xml item node
#
class file_type_info:
   
   def __init__( self, work_folder, local_file ):
      
      self.work_folder = work_folder
      self.local_file = local_file
      self.full_path = self._get_full_path( self.work_folder, self.local_file )

      self.name, self.ext = os.path.splitext( self.full_path )
      #self.size = self._get_file_size( self.full_path )

      self._determine_size()
      self._determine_dates()
      self._determine_audio_type()


   #
   #
   def _determine_size(self):
      self.size = self._get_file_size( self.full_path )
      if self.size == None:
         self.size_error_status = "Error geting size"

   #
   #
   def _determine_dates(self):
      #self.date_created = time.strftime( "%Y-%b-%d %H:%M", time.localtime( self._get_file_date( self.full_path, "c" ) ) )
      self.date_modified_localtime = time.localtime( self._get_file_date( self.full_path, "m" ) )
      self.date_modified = time.strftime( "%Y-%m-%d", self.date_modified_localtime ) #time.localtime( self._get_file_date( self.full_path, "m" ) ) )

      if self.date_modified == None:
         self.date_error_status = "Error geting file dates"

   #
   #
   def _determine_audio_type( self ):
      self.audio_type = None

      if self.ext == ".mp3":
         #print("--------->>>>>> " + f_full )
         try:
            self.audio_type = MP3( self.full_path )
         except:
            self.audio_error = "Error getting MP3 information"
               
      elif self.ext == ".flac":
            #print("--------->>>>>> " + f_full )
            try:
               self.audio_type = FLAC( self.full_path )
            except:
               self.audio_error = "Error getting FLAC info"
      elif self.ext == ".m3u":
         self.audio_error = ""
      elif self.ext == ".cue":
         self.audio_error = ""
      else:
         self.audio_error = "Error!! Unknow audio format"


   #
   #
   def _get_full_path( self, work_folder, local_file ):
      f_full = work_folder + "/" + local_file
      return f_full


   #
   # Retrieves size in kb from a full_path file
   # @return file size or 0
   #
   def _get_file_size( self, f_full ):
      f_size = None
      
      # some microsd files gives access errors
      try:
         f_size = os.path.getsize(f_full) / 1024
      except:
         #print("Something wrong getting size of: " + f_full )
         raise

      finally:
         return f_size


   #
   # Retrieves file date
   # @date_type specifies which date type
   #     "c"   -> means creation date
   #     "m"   -> means modified date
   #
   def _get_file_date( self, f_full, date_type ):
      f_date = None
      
      try:

         if date_type == "c":
            f_date = os.path.getctime(f_full)
         elif date_type == "m":
            f_date = os.path.getmtime(f_full)

      except:
         #print("Something wrong getting creation date of: " + f_full )
         raise

      finally:
         return f_date


   #
   #
   #
   def _get_local_file_size( self, work_folder, local_file ):
      return self._get_file_size( self._get_full_path( work_folder, local_file ) )





#
# Encapsulates item_file meta info data to build each xml item node
#
class item_type_info:
   
   def __init__( self, work_folder, item, is_comment = False ):
      
      self.item = item
      self.is_comment = is_comment
      self.work_folder = work_folder





#
# Manages xml: creation, update, ...
#
class xml_manager:
   
   def __init__( self, work_folder, local_file ):
      self.xml_doc = None


   def create( self ):
      if self.xml_doc != None:
         core.utils.log_error("Oops! can't create a non null xml document")
         return

      self.xml_doc = Document()
      self.xml_root = xml_doc.createElement("root")
      self.xml_doc.appendChild( xml_root )


   #
   # note that changes will be lost if no saved previously
   #
   def close( self ):
      self.xml_doc.unlink();
      self.xml_doc = None



   def load_from_file( self, full_filename ):
      if self.xml_doc != None:
         core.utils.log_error("can't not load from file an already open xml document")
         return

      self.xml_doc = parse( full_filename )



   #
   # Returns node or None if not found
   #
   def find_node( self, node_name ):
      if self.xml_doc == None:
         core.utils.log_error("can't not find within no created/loaded xml document")
         return

      for node in self.xml_doc.getElementsByTagName( node_name ):
         if node.tagName == node_name:
            return node

      return None



   #
   # Saves current data
   #
   def save( full_filename ):
      if self.xml_doc == None:
         core.utils.log_error("can't not flush a non created/loaded xml document")
         return
         
      f = open( full_filename, 'w' )
      self.xml_doc.writexml( f, indent="  ", addindent="  ", newl='\n' )

      core.utils.log( "\nData saved to XML file: " + full_filename )


   #
   # Creates a xml node with 1 attrib if passed
   # Returns created node
   #
   def create_node(self, node_name, attrib_id = None, attrib_value = None ):
      if self.xml_doc == None:
         core.utils.log_error("can't not create node for a non created/loaded xml document")
         return

      xml_node = xml_doc.createElement( node_name )
      
      if attrib_id != None:
         self.add_attribute( xml_node, attrib_id, attrib_value )

      return xml_node




   def add_attribute(self, xml_node, attrib_id, attrib_value ):
      if xml_node == None:
         core.utils.log_error("can't not add attributes over a null xml node")
         return
   
      xml_node.setAttribute( attrib_id, attrib_value )








#
# Iterating over directory tree
#

def traverse_folder( subfolder):
   
   if subfolder!="":
      subfolder = subfolder + "/"

   global total_saved_albums
   global total_saved_albums_size

   work_folder = opt.source_root_path + "/" + subfolder
   #for path_name, dirs, files in os.walk( root_folder ):

   children_folders = set()
   items_type_info_set = set()

   try:
      # get items from subfolder
      process_subfolder_data( subfolder, children_folders, items_type_info_set )

      # by default do not create albums where all items are comments
      all_comments = True
      for i in items_type_info_set:
         if i.is_comment != True:
            all_comments = False
            break

      if all_comments != True:
         if items_type_info_set:

            #if opt.dry_run == False:
            xml_album = xml_doc.createElement( "album" )
            xml_album.setAttribute("src", subfolder )
            xml_section.appendChild( xml_album )

            album_size=0
            core.utils.log_album( subfolder )

            # process songs
            album_size = process_album_items( items_type_info_set, xml_album )

            if opt.dry_run == False:
               set_xml_album_size( xml_album, album_size )

            total_saved_albums = total_saved_albums + 1
            total_saved_albums_size = total_saved_albums_size + album_size



      # iterate over the rest of subfolders
      for ss in children_folders:
         traverse_folder( ss  )

   except Exception as e:
      core.utils.log_error("Something wrong in traverse_folder.\nException: \n" + repr(e) )
      raise




#
# Populates found items ( valid music files, and those to be commented )
#
# @children_folders
# @items_info_type_set      : returns a set with items
#
def process_subfolder_data( subfolder, children_folders, items_info_type_set ):

   work_folder = opt.source_root_path + "/" + subfolder

   since_date_localtime = time.strptime( opt.since_date, "%Y-%m-%d" );
   #print "----------- since_date_localtime: " + str( since_date_localtime )

   core.utils.log( "processing: " + subfolder + "...", opt.verbose_mode )

   # Here store subfolders, items and commented_items
   try:
      for ss in os.listdir(work_folder):

         f_full = work_folder + "/" + ss
         
         if os.path.isdir( f_full ): #work_folder + "/" + ss ):
            #print("dir entry   : " + ss )
            children_folders.add( subfolder + ss )

         if time.localtime( os.path.getmtime( f_full ) ) < since_date_localtime:
            #print "* omitted item : " + ss + "  --  date " + \
             #        time.strftime("%Y-%m-%d",time.localtime(os.path.getmtime(f_full))) + " previous to " + opt.since_date
            continue

         for t in supported_audio_file_types:
            if fnmatch.fnmatch( ss, "*." + t ): #opt.file_type ):
               items_info_type_set.add( item_type_info( work_folder, ss ) )
               break

         for t in supported_comment_file_types:
            if fnmatch.fnmatch( ss, "*." + t ):
               items_info_type_set.add( item_type_info( work_folder, ss, True ) )
               break

   except OSError as e:
      core.utils.log_error( "Error iterating over: " + work_folder + "\nException:\n" + repr(e) )
      raise

   except Exception as e:
      core.utils.log_error("Unknow exception when iterating over: " + work_folder + "\nException:\n" + repr(e) )
      raise



#
#
#
def process_album_items( items_info_type_set, xml_album ):
   
   album_size = 0
   global g_total_processed_items

   for i in items_info_type_set:
      #print(   "- adding: " + i ); 
      g_total_processed_items = g_total_processed_items + 1

      f = file_type_info( i.work_folder, i.item )
      
      if i.is_comment:
         process_album_commented_item( item_type_info( i.work_folder, i.item, True ), xml_album )
         continue

      if opt.dry_run == False:
         xml_item = create_xml_item( f ) 
         set_xml_item_size( xml_item, f ) 
         set_xml_item_dates( xml_item, f ) 

      if f.size != None:
         album_size = album_size + f.size

      if opt.dry_run == False:
         set_xml_item_audio_info( xml_item, f )

         #xml_item = xml_doc.createTextNode( i )
         xml_album.appendChild( xml_item )


   return album_size



#
#
#
def process_album_commented_item( i, xml_album ):

   f = file_type_info( i.work_folder, i.item )

   # to avoid xml parser engine error when a '--' is found in name
   chars_to_remove=['-']
   i_fixed = i.item.translate( None, ''.join(chars_to_remove) )
   
   str_comm = " <item src=\"" + i_fixed + "\" size=\"" + str(f.size) + "Kb\" /> " 

   # Notify the user in some way which files have removed chars
   str_mark = ""
   if i_fixed != i.item:
      str_mark = " *** " 

   core.utils.log_item( str_mark + i_fixed, True, opt.verbose_mode )

   if opt.dry_run:
      return

   xml_item_comm = xml_doc.createComment( str_mark + str_comm ) 
   xml_album.appendChild( xml_item_comm )



#
#
#
def create_xml_item( f_object ):

   #print(   "  - add item: " + f_object.local_file );
   core.utils.log_item( f_object.local_file, False, opt.verbose_mode );

   xml_item = xml_doc.createElement( "item" )
   xml_item.setAttribute( "src", f_object.local_file )

   return xml_item



#
#
#
def set_xml_item_size( xml_item, f_type ):
   if f_type.size != None:
      xml_item.setAttribute( "size", "{0:.1f}".format( f_type.size / 1024.0 ) + " Mb" )
   else:
      xml_item.setAttribute( "size_error", "error getting size" )


#
#
#
def set_xml_item_dates( xml_item, f_type ):
   # if f_type.date_created != None:
   #    xml_item.setAttribute( "created", f_type.date_created )
   # else:
   #    xml_item.setAttribute( "date_error", "error getting creation date" )

   if f_type.date_modified != None:
      xml_item.setAttribute( "modified_date", f_type.date_modified )
   else:
      xml_item.setAttribute( "date_error", "error getting modified date" )




#
#
#
def set_xml_item_audio_info( xml_item, f ):

   if f.audio_type == None:
      
      # because m3u, cue, ... are valid "music" files to be copied but don't have audio info, so, no error because is not an error
      if f.audio_error != "":
         xml_item.setAttribute( "audio_error", f.audio_error )
      
      return

   if isinstance( f.audio_type, MP3 ):
      try:
         xml_item.setAttribute("bpm", str(f.audio_type.info.bitrate / 1000 ) )
         xml_item.setAttribute("length", time.strftime("%H:%M:%S", time.gmtime( f.audio_type.info.length ) ) )
         #xml_item.setAttribute("length", str(f_audio.info.length))

      except Exception as e:
         print("** Error getting MP3 info: " + repr(e) )
         xml_item.setAttribute("bpm", "0" )
         xml_item.setAttribute("audio_error", "MP3 exception: " + repr(e) )

   elif isinstance( f.audio_type, FLAC ):
      try:
         xml_item.setAttribute("sample_rate", str(f.audio_type.info.sample_rate) )
         xml_item.setAttribute("length", time.strftime("%H:%M:%S", time.gmtime( f.audio_type.info.length ) ) )

      except Exception as e:
         print("** Error getting FLAC info: " + repr(e) )
         xml_item.setAttribute("sample_rate", "0")
         xml_item.setAttribute("length", "0")
         xml_item.setAttribute("audio_error", "FLAC exception: " + repr(e) )

#
#
#
def set_xml_album_size( xml_album, album_size ):
   xml_album.setAttribute("size", "{0:.2f}".format( album_size / 1024.0 ) + " Mb" )





#
#
#
# def log( msg ):
#    print( msg )
#
#
# def log_item( item, is_commented=False ):
#    if is_commented:
#       log( "  - add COMMENTED item: " + item )
#    else:
#       log( "  - add item: " + item )
#
#
# def log_album( album ):
#    log( "- add album: " + album )
#
#
# def log_error( msg ):
#    log( "*** " + msg )





#
# Saves and unlink xml
# also updates tag <section> with total albums and total albums size
#

def save_xml( full_filename ):
   
   tot_sz_gb = "{0:.2f}".format( total_saved_albums_size / 1024.0 / 1024.0 ) + " Gb"

   core.utils.log( "\n. total albums: " + str(total_saved_albums) )
   core.utils.log( ". total items: " + str(g_total_processed_items) )
   core.utils.log( ". total albums size: " + tot_sz_gb + "  ( " + str(total_saved_albums_size) + " Mb )"  )

   if opt.dry_run:
      return

   xml_section.setAttribute( "total_albums", str(total_saved_albums) )
   xml_section.setAttribute( "total_albums_size", tot_sz_gb )
   xml_section.setAttribute( "total_items", str(g_total_processed_items) )

   f = open( full_filename, 'w' )
   xml_doc.writexml( f, indent="  ", addindent="  ", newl='\n' )

   core.utils.log( "\nData have been saved to the XML file: " + full_filename )

   # last unlink xml
   xml_doc.unlink()






#
# settings info
#
def show_settings_info( title, request_user_confirm = False ):
   core.utils.log("")
   core.utils.log( title )
   core.utils.log("  - source root_path : " + opt.source_root_path )
   core.utils.log("  - output file      : " + full_output_filename )
   core.utils.log("  - section id       : " + opt.section_id )
   core.utils.log("  - since date       : " + opt.since_date )
   core.utils.log("  - supported audio file types   : " + str(supported_audio_file_types) ) 
   core.utils.log("  - supported comment file types : " + str(supported_comment_file_types)) 
   core.utils.log("  - dry_run mode : " + str(opt.dry_run)) 
   core.utils.log("")
   core.utils.log("  Notes:")
   core.utils.log("  * folders/albums with all its files as comments will not be added by default" )
   core.utils.log("  * commented file with characters '-' in its name will be marked with '***' and replaced with ' '")
   core.utils.log("")

   if request_user_confirm:
      resp = raw_input( "\nContinue with this settings (Y/n) ?" )
      if resp=="n" or resp=="N":
         core.utils.log( "\nOperation canceled by the user" )
         exit(0)





#
# Main
# TODO: Pending refactor whole main entry stuff
#

xml_doc = Document()
xml_root = xml_doc.createElement("root")
xml_doc.appendChild( xml_root )


supported_audio_file_types=['flac','dsd','cue','mp3','m3u','m4a','aac','alac','wav']
supported_comment_file_types = ['jpg', 'png', 'gif']

p = optparse.OptionParser()

p.add_option("-s", "--source_root_path", action="store", type="string", dest="source_root_path", \
                                       help="source path to start search" )
p.add_option("-i", "--section_id", action="store", type="string", dest="section_id", help="optional section id. Default last source path" )
p.add_option("-o", "--output_path", action="store", type="string", dest="output_path", default="output_data", help="optional output generated files path" )
p.add_option("-d", "--since_date", action="store", type="string", dest="since_date", default="1900-01-01", help="optional, files since date yyyy-mm-dd" )
p.add_option("-t", "--target_file", action="store", type="string", dest="target_file", default=None, help="optional alternative target file name" )
p.add_option("-n", "--no_verbose", action="store_true", dest="verbose_mode", help="no verbose mode" )
p.add_option("-u", "--dry_run", action="store_true", dest="dry_run", help="dry_run mode" )

opt,args = p.parse_args()

if opt.source_root_path == None:
   print("Plese enter SOURCE_ROOT_PATH folder. Use -h to show currently available options" )
   sys.exit(1)

if opt.verbose_mode == None:
   opt.verbose_mode = True
else:
   opt.verbose_mode = False

if opt.dry_run == None:
   opt.dry_run = False
else:
   opt.dry_run = True

if opt.source_root_path.endswith('/'):
   opt.source_root_path = opt.source_root_path[:-1]

if opt.section_id == None: 
   #opt.section_id = opt.source_root_path.replace('/','_') #os.path.basename( opt.root_path ) + "_"
   opt.section_id = os.path.basename( os.path.normpath( opt.source_root_path ) ); 
   # remove first '/'
   #opt.section_id = opt.section_id[:0] + opt.section_id[1:]

if opt.target_file == None:
   opt.target_file = opt.section_id + ".xml"


full_output_filename = opt.output_path + "/" + opt.target_file



#
# show settings values and asks to continue
#
show_settings_info( "ak_generate current settings values:\n", True )




#
# create target folder
#
if not os.path.exists(opt.output_path):
   core.utils.log( "Creating folder: " + opt.output_path )
   os.makedirs(opt.output_path)



#
# checks whether output file exists
#
#full_output_filename = opt.output_path + "/" + opt.section_id + ".xml"

if opt.dry_run == False and os.path.isfile( full_output_filename ):
   resp = raw_input( "\nFile: " + full_output_filename + " exists. \ndo you want to be overwritted (y/N) ?" )
   if resp!="y" and resp!="Y":
      core.utils.log( "\nOperation canceled by the user" )
      exit(0)


#
# create xml header <section> info
#
xml_section = xml_doc.createElement("section")
xml_section.setAttribute( "id", opt.section_id )
xml_section.setAttribute( "source", opt.source_root_path )
xml_section.setAttribute( "since_date", opt.since_date )

xml_root.appendChild(xml_section)




#
# start main operation
#
total_saved_albums = 0
g_total_processed_items = 0
total_saved_albums_size = 0

traverse_folder( "" )




#
#
show_settings_info("used settings:")


#
# 
#
save_xml( full_output_filename )




