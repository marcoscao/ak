import ntpath
import os
import sys
import optparse
import subprocess
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
      self._determine_audio_type()


   #
   #
   def _determine_size(self):
      self.size = self._get_file_size( self.full_path )
      if self.size == None:
         self.size_error_status = "Error geting size"

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
   #
   #
   def _get_local_file_size( self, work_folder, local_file ):
      return self._get_file_size( self._get_full_path( work_folder, local_file ) )











#
# Iterating over directory tree
# TODO: Pending refactor this method
#

def traverse_folder( subfolder):
   #print("* Traversing folder: " + root_folder )
   work_folder = opt.source_root_path + "/" + subfolder
   n = 0
   print( "subfolder : " + subfolder )
   #print( "Subdirectories of " + work_folder + " :")
   #for path_name, dirs, files in os.walk( root_folder ):
   if subfolder!="":
      subfolder = subfolder + "/"

   folder_has_file_types = False
   children_folders = set()

   items_set = set()
   items_comm_set = set()
   items_rest = set()

   # Here store subfolders, items and commented_items
   try:
      n = 0
      for ss in os.listdir(work_folder):
         if os.path.isdir( work_folder + "/" + ss ):
            #print("dir entry   : " + ss )
            ###traverse_folder( subfolder + ss )
            children_folders.add( subfolder + ss )

         #if folder_has_file_types==False and fnmatch.fnmatch( ss, "*." + "flac" ): #opt.file_type ):
         for t in file_types:
            if fnmatch.fnmatch( ss, "*." + t ): #opt.file_type ):
               items_set.add( ss )
               #print("** Folder " + subfolder + " has files of type *." + opt.file_type)
               folder_has_file_types = True
         
         for t in file_types_comm:
            if fnmatch.fnmatch( ss, "*." + t ):
               items_comm_set.add(ss )
               #folder_has_file_types = True

   except OSError as e:
      log_error( "Error iterating over: " + work_folder + "\nException:\n" + repr(e) )
      return


   if folder_has_file_types:
      xml_album = xml_doc.createElement( "album" )
      xml_album.setAttribute("src", subfolder )

      xml_section.appendChild( xml_album )

      album_size=0
      log_album( subfolder )

      for i in items_set:
         #print(   "- adding: " + i ); 

         f = file_type_info( work_folder, i )

         xml_item = create_xml_item( f ) 
         set_xml_item_size( xml_item, f ) 

         if f.size != None:
            album_size = album_size + f.size

         set_xml_item_audio_info( xml_item, f )

         #xml_item = xml_doc.createTextNode( i )
         xml_album.appendChild( xml_item )

      for i in items_comm_set:
         f = file_type_info( work_folder, i )

         # to avoid xml parser engine error when a '--' is found in name
         chars_to_remove=['-']
         i_fixed = i.translate( None, ''.join(chars_to_remove) )
         
         str_comm = " <item src=\"" + i_fixed + "\" size=\"" + str(f.size) + "Kb\" /> " 

         # Notify the user in some way which files have removed chars
         str_mark = ""
         if i_fixed != i:
            str_mark = " *** " 

         log_item( str_mark + i, True )

         xml_item_comm = xml_doc.createComment( str_mark + i ) 
         xml_album.appendChild( xml_item_comm )


      set_xml_album_size( xml_album, album_size );



   # iterate over the rest of subfolders
   for ss in children_folders:
      traverse_folder( ss  )





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
# Retrieves size in kb from a full_path file
# @return file size or 0 for aditional album size computations
#
def set_xml_item_size( xml_item, f_type ):
   if f_type.size != None:
      xml_item.setAttribute( "size", str( f_type.size / 1024 ) + "Mb" )
   else:
      xml_item.setAttribute( "size_error", "error getting size" )



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
         #xml_item.setAttribute("length", str(f_audio.info.length))

      except Exception as e:
         print("** Error getting MP3 info: " + repr(e) )
         xml_item.setAttribute("bpm", "0" )
         xml_item.setAttribute("audio_error", "MP3 exception: " + repr(e) )

   elif isinstance( f.audio_type, FLAC ):
      try:
         xml_item.setAttribute("sample_rate", str(f.audio_type.info.sample_rate) )

      except Exception as e:
         print("** Error getting FLAC info: " + repr(e) )
         xml_item.setAttribute("sample_rate", "0")
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

xml_section = xml_doc.createElement("section")
xml_section.setAttribute( "id", opt.section_id )
xml_section.setAttribute( "source", opt.source_root_path )
xml_root.appendChild(xml_section)

traverse_folder( "" )


if not os.path.exists(opt.output_path):
   os.makedirs(opt.output_path)

xml_doc.writexml( open( opt.output_path + "/" + opt.section_id + ".xml",'w'), indent="  ", addindent="  ", newl='\n' )
xml_doc.unlink()


