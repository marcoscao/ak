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
# Iterating over directory tree
#

def traverse_folder( subfolder):
   
   if subfolder!="":
      subfolder = subfolder + "/"

   work_folder = opt.source_root_path + "/" + subfolder
   #for path_name, dirs, files in os.walk( root_folder ):

   children_folders = set()
   items_type_info_set = set()

   # get items from subfolder
   process_subfolder_data( subfolder, children_folders, items_type_info_set )

   # if folder_has_file_types or commented ones create the album:
   if items_type_info_set:

      xml_album = xml_doc.createElement( "album" )
      xml_album.setAttribute("src", subfolder )
      xml_section.appendChild( xml_album )

      album_size=0
      log_album( subfolder )

      # process songs
      album_size = process_album_items( items_type_info_set, xml_album )

      set_xml_album_size( xml_album, album_size )


   # iterate over the rest of subfolders
   for ss in children_folders:
      traverse_folder( ss  )





#
# Populates found items ( valid music files, and those to be commented )
#
# @children_folders
# @items_info_type_set      : returns a set with items
#
def process_subfolder_data( subfolder, children_folders, items_info_type_set ):

   print( "subfolder : " + subfolder )
   work_folder = opt.source_root_path + "/" + subfolder

   since_date_localtime = time.strptime( opt.since_date, "%Y-%m-%d" );
   #print "----------- since_date_localtime: " + str( since_date_localtime )

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

         for t in file_types:
            if fnmatch.fnmatch( ss, "*." + t ): #opt.file_type ):
               items_info_type_set.add( item_type_info( work_folder, ss ) )
               break

         for t in file_types_comm:
            if fnmatch.fnmatch( ss, "*." + t ):
               items_info_type_set.add( item_type_info( work_folder, ss, True ) )
               break

   except OSError as e:
      log_error( "Error iterating over: " + work_folder + "\nException:\n" + repr(e) )
      return




#
#
#
def process_album_items( items_info_type_set, xml_album ):
   
   album_size = 0

   for i in items_info_type_set:
      #print(   "- adding: " + i ); 

      f = file_type_info( i.work_folder, i.item )

      if i.is_comment:
         process_album_commented_item( item_type_info( i.work_folder, i.item, True ), xml_album )
         continue

      xml_item = create_xml_item( f ) 
      set_xml_item_size( xml_item, f ) 
      set_xml_item_dates( xml_item, f ) 

      if f.size != None:
         album_size = album_size + f.size

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

   log_item( str_mark + i_fixed, True )

   xml_item_comm = xml_doc.createComment( str_mark + str_comm ) 
   xml_album.appendChild( xml_item_comm )



#
#
#
def create_xml_item( f_object ):

   #print(   "  - add item: " + f_object.local_file );
   log_item( f_object.local_file );

   xml_item = xml_doc.createElement( "item" )
   xml_item.setAttribute( "src", f_object.local_file )

   return xml_item



#
#
#
def set_xml_item_size( xml_item, f_type ):
   if f_type.size != None:
      xml_item.setAttribute( "size", str( f_type.size / 1024 ) + "Mb" )
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
   xml_album.setAttribute("size", str( album_size / 1024 ) + "Mb" )




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




#
# Saves and unlink xml
#
def save_xml():

   if not os.path.exists(opt.output_path):
      log( "Creating folder: " + opt.output_path )
      os.makedirs(opt.output_path)

   full_filename = opt.output_path + "/" + opt.section_id + ".xml"
   #xml_doc.writexml( open( opt.output_path + "/" + opt.section_id + ".xml",'w'), indent="  ", addindent="  ", newl='\n' )
   if os.path.isfile( full_filename ):
      resp = raw_input( "\nFile: " + full_filename + " exists. \ndo you want to overwrite it (y/N) ?" )
      if resp!="y" and resp!="Y":
         log( "\nOperation canceled by the user" )
         return
      

   f = open( full_filename, 'w' )
   xml_doc.writexml( f, indent="  ", addindent="  ", newl='\n' )

   log( "\nData saved to XML file: " + full_filename )

   # last unlink xml
   xml_doc.unlink()








#
# Main
# TODO: Pending refactor whole main entry stuff
#

xml_doc = Document()
xml_root = xml_doc.createElement("root")
xml_doc.appendChild( xml_root )


file_types=['flac','dsd','cue','mp3','m3u','m4a','aac','alac','wav']
file_types_comm = ['jpg', 'png', 'gif']

p = optparse.OptionParser()

p.add_option("-s", "--source_root_path", action="store", type="string", dest="source_root_path", \
                                       help="source path to start search" )
#p.add_option("-f", "--file_types", action="store", type="string", dest="file_type")
p.add_option("-i", "--section_id", action="store", type="string", dest="section_id", help="optional section id. Default last source path" )
p.add_option("-o", "--output_path", action="store", type="string", dest="output_path", default="output_data", help="optional output generated files path" )
p.add_option("-d", "--since_date", action="store", type="string", dest="since_date", default="1900-01-01", help="optional, files since date yyyy-mm-dd" )

# flac, mp3, dsf, ... or empty means everything
#p.set_defaults( file_type="flac alac mp3 cue wav dsd dsf ogg" )
#p.set_defaults( section_id="" )

opt,args = p.parse_args()

if opt.source_root_path == None:
   print("Plese enter SOURCE_ROOT_PATH folder. Use -h to show currently available options" )
   sys.exit(1)

if opt.source_root_path.endswith('/'):
   opt.source_root_path = opt.source_root_path[:-1]

if opt.section_id == None: 
   #opt.section_id = opt.source_root_path.replace('/','_') #os.path.basename( opt.root_path ) + "_"
   opt.section_id = os.path.basename( os.path.normpath( opt.source_root_path ) ); 
   # remove first '/'
   #opt.section_id = opt.section_id[:0] + opt.section_id[1:]


print("")
print("source root_path    : " + opt.source_root_path )
print("output_path    : " + opt.output_path )
#print("file types   : " + opt.file_types ) 
print("section id : " + opt.section_id )
print("since_date : " + opt.since_date )
print ""


xml_section = xml_doc.createElement("section")
xml_section.setAttribute( "id", opt.section_id )
xml_section.setAttribute( "source", opt.source_root_path )
xml_section.setAttribute( "since_date", opt.since_date )
xml_root.appendChild(xml_section)


traverse_folder( "" )

save_xml()


