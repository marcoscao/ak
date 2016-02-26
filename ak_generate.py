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
# Iterating over directory tree
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
   
   if folder_has_file_types:
      xml_album = xml_doc.createElement( "album" )
      xml_album.setAttribute("src", subfolder )


      xml_section.appendChild( xml_album )

      album_size=0
      print("** Creating tag node for " + subfolder )
      for i in items_set:
         print(   "- adding: " + i ); 
         xml_item = xml_doc.createElement( "item" )
         xml_item.setAttribute( "src", i )
      
         f_full = work_folder + "/" + i
         f_name, f_ext = os.path.splitext( f_full )
         
         # size in kb
         f_size=0
         try:
            # some microsd files gives access errors
            f_size = os.path.getsize(f_full) / 1024
         except:
            xml_item.setAttribute("size_status", "error getting size")
            print("Something wrong getting size of: " + f_full )

         album_size=album_size + f_size

         xml_item.setAttribute("size", str(f_size/1024) + "Mb" )
         if f_ext == ".mp3":
            #print("--------->>>>>> " + f_full )
            try:
               f_audio = MP3( f_full )
               xml_item.setAttribute("bpm", str(f_audio.info.bitrate / 1000 ) )
               #xml_item.setAttribute("length", str(f_audio.info.length))
            except:
               print("ERROR!! Getting MP3 information")
               xml_item.setAttribute("bpm", "0" )
               xml_item.setAttribute("status", "error getting MP3 info")
         else:
            if f_ext == ".flac":
               #print("--------->>>>>> " + f_full )
               try:
                  f_audio = FLAC( f_full )
                  xml_item.setAttribute("sample_rate", str(f_audio.info.sample_rate) )
               except:
                  print("ERROR!! Getting FLAC info")
                  xml_item.setAttribute("sample_rate", "0")
                  xml_item.setAttribute("status", "error getting FLAC info")


         #xml_item = xml_doc.createTextNode( i )
         xml_album.appendChild( xml_item )

      for i in items_comm_set:
         print( "- adding COMMENTED: " + i )
         f_full = work_folder + "/" + i
         
         # size in kb
         f_size=0
         try:
            # some microsd files gives access errors
            f_size = os.path.getsize(f_full) / 1024
         except:
            xml_item.setAttribute("size_status", "error getting size")
            print("Something wrong getting size of: " + f_full )

         xml_item_comm = xml_doc.createComment( " <item src=\"" + i + "\" size=\"" + str(f_size) + "Kb\" /> " )
         #xml_item_comm.setText( "<!-- <item src=\"" + i + "\" />  -->" )

         xml_album.appendChild( xml_item_comm )


      xml_album.setAttribute("size", str(album_size/1024) + "Mb" )


   # iterate over the rest of subfolders
   for ss in children_folders:
      traverse_folder( ss )


#
# Main
#

xml_doc = Document()
xml_root = xml_doc.createElement("root")
xml_doc.appendChild( xml_root )


file_types=['flac','dsd','cue','mp3','m3u','m4a','aac','alac','wav']
file_types_comm = ['jpg', 'png', 'gif']

p = optparse.OptionParser()

p.add_option("-s", "--source_root_path", action="store", type="string", dest="source_root_path")
#p.add_option("-f", "--file_types", action="store", type="string", dest="file_type")
p.add_option("-i", "--section_id", action="store", type="string", dest="section_id")

# flac, mp3, dsf, ... or empty means everything
#p.set_defaults( file_type="flac alac mp3 cue wav dsd dsf ogg" )
p.set_defaults( section_id="" )

opt,args = p.parse_args()

if opt.source_root_path == None:
   print("Plese enter SOURCE_ROOT_PATH folder. Use -h to show currently available options" )
   sys.exit(1)

if opt.source_root_path.endswith('/'):
   opt.source_root_path = opt.source_root_path[:-1]

if opt.section_id == "":
   opt.section_id = opt.source_root_path.replace('/','_') #os.path.basename( opt.root_path ) + "_"
   # remove first '/'
   opt.section_id = opt.section_id[:0] + opt.section_id[1:]

   

print("")
print("source root_path    : " + opt.source_root_path )
#print("target root_path    : " + opt.target_root_path )
#print("file types   : " + opt.file_types ) 
print("section id : " + opt.section_id )

xml_section = xml_doc.createElement("section")
xml_section.setAttribute( "id", opt.section_id )
xml_section.setAttribute( "source", opt.source_root_path )
xml_root.appendChild(xml_section)

traverse_folder( "" )

xml_doc.writexml( open( opt.section_id + ".xml",'w'), indent="  ", addindent="  ", newl='\n' )
xml_doc.unlink()


