#!/usr/bin/python

from core.utils import FileManager
from core.utils import XmlManager
from core.utils import Log

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



def current_date_time():
   return time.strftime("%Y/%m/%d %H:%M:%S")



#
# Encapsulates file meta info data to build each xml item node
#
class file_type_info:
   
   def __init__( self, work_folder, local_file ):
      
      self.work_folder = work_folder
      self.local_file = local_file
      self.full_path = FileManager.full_path( self.work_folder, self.local_file )

      self.name = FileManager.file_basename( self.full_path )
      self.ext = FileManager.file_extension( self.full_path )

      self._determine_size()
      self._determine_dates()
      self._determine_audio_type()


   #
   #
   def _determine_size(self):
      self.size = FileManager.file_size( self.full_path )
      if self.size == None:
         self.size_error_status = "Error geting size"

   #
   #
   def _determine_dates(self):
      ##self.date_created = time.strftime( "%Y-%b-%d %H:%M", time.localtime( self._get_file_date( self.full_path, "c" ) ) )
      self.date_modified_localtime = time.localtime( FileManager.file_date( self.full_path, "m" ) )
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
# Encapsulates item_file meta info data to build each xml item node
#
class item_type_info:
   
   def __init__( self, work_folder, item, is_comment = False ):
      
      self.item = item
      self.is_comment = is_comment
      self.work_folder = work_folder







#
# Iterating over directory tree
# if first_time = True, the subfolder won't be created

def traverse_folder( subfolder, first_time = False ):
   
   global total_saved_albums
   global total_saved_albums_size
   global xml_source_parent

   work_folder = FileManager.concat_folder( opt.source_root_path, subfolder )
   xml_previous_source_parent = xml_source_parent

   # creates xml source entry ( parent )
   last_subfolder = os.path.basename( os.path.normpath( subfolder ) );
            
   nd_folder = find_node_by_value( xml_source_parent, "source", "src", last_subfolder )
   if nd_folder != None:
      xml_source_parent = nd_folder


   if first_time == False and node_attribute( xml_source_parent, "src" ) != last_subfolder:
      #print( "going to create: \'"+last_subfolder+"\' during traverse_folder" )
      #nd = find_node_by_value( xml_source_parent, "source", "src", last_subfolder )
      #if nd == None:
      #   xml_source_parent = create_xml_source( xml_source_parent, last_subfolder ) 
      #else:
      #   xml_source_parent = nd

      xml_source_parent = create_xml_source( xml_source_parent, last_subfolder ) 

   print( "\n** entering traverse_folder:" )
   print( "  subfolder : " + subfolder )
   print( "  last_subfolder : " + last_subfolder )
   print( "  xml_source_node: " + str(node_attribute( xml_source_parent, "src" )) )
   print( "  xml_previous_source_node: " + str(node_attribute( xml_previous_source_parent, "src" )) )

   #if subfolder.endswith('/'):
   #   subfolder = subolder[:-1]

   subfolder = subfolder + "/"

   # if subfolder != None:
   #    subfolder = subfolder + "/"
   #    work_folder = FileManager.concat_folder( opt.source_root_path, subfolder )
   # else:
   #    work_folder = FileManager.concat_folder( opt.source_root_path, "" )
   #    subfolder=opt.source_root_path_last_folder + "/"


   ##work_folder = opt.source_root_path + "/" + subfolder
   #work_folder = FileManager.concat_folder( opt.source_root_path, subfolder )
   ##for path_name, dirs, files in os.walk( root_folder ):

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

            xml_album = None
            #if opt.update_mode:
            #xml_album = find_node_by_value( xml_section, "album", "src", subfolder )
            xml_album = find_node_by_value( xml_source_parent, "album", "src", last_subfolder )
            if xml_album == None:
               #Log.log("  + found new album")
               create_new_update_entry( "added_new_album", last_subfolder )

            if xml_album == None:
               xml_album = xml_doc.createElement( "album" )
               xml_album.setAttribute( "src", last_subfolder )
               xml_album.setAttribute( "add", current_date_time() )
               #xml_section.appendChild( xml_album )
               xml_source_parent.appendChild( xml_album )
               
               total_saved_albums = total_saved_albums + 1
               core.utils.log_album( last_subfolder )

            album_size=0

            # process songs
            album_size = process_album_items( items_type_info_set, xml_album )

            set_xml_album_size( xml_album, album_size )

            #total_saved_albums = total_saved_albums + 1
            total_saved_albums_size = total_saved_albums_size + album_size



      # iterate over the rest of subfolders
      for ss in children_folders:
         traverse_folder( ss  )


      xml_source_parent = xml_previous_source_parent

      print( "\n******** END traverse_folder:" )
      print( "  subfolder : " + subfolder )
      print( "  last_subfolder : " + last_subfolder )
      print( "  xml_source_node: " + str(node_attribute( xml_source_parent, "src" )) )
      print( "  xml_previous_source_node: " + str(node_attribute( xml_previous_source_parent, "src" )) )


   except Exception as e:
      Log.log_error("Something wrong in traverse_folder.\nException: \n" + repr(e) )
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

   Log.log( "processing: " + subfolder + "...", opt.verbose_mode )

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
      Log.log_error( "Iterating over : " + work_folder + "\nException:\n" + repr(e) )
      raise

   except Exception as e:
      Log.log_error("Unknow exception when iterating over: " + work_folder + "\nException:\n" + repr(e) )
      raise



#
#
#
def process_album_items( items_info_type_set, xml_album ):
   
   album_size = 0
   global g_total_processed_items

   for i in items_info_type_set:
      #print(   "- adding: " + i ); 
      #g_total_processed_items = g_total_processed_items + 1

      f = file_type_info( i.work_folder, i.item )
      
      if i.is_comment:
         #if opt.update_mode != None:
         process_album_commented_item( item_type_info( i.work_folder, i.item, True ), xml_album )
         continue
   
      xml_item = None

      #if opt.update_mode:
      xml_item = find_node_by_value( xml_album, "item", "src", f.local_file )
      if xml_item == None:
         #Log.log("  + found new item")
         create_new_update_entry( "added_new_item", f.full_path )
      else:
         attr_sz = xml_item.attributes["size"]
         if attr_sz:
            #print "attr_sz = " + attr_sz.value + " || f.size = " + str( f.size )
            if long(attr_sz.value) != f.size:
               Log.log("  + updating existing item with different size")
               create_new_update_entry( "update_modified_item", f.full_path )
               xml_album.removeChild( xml_item )
               xml_item = None
         
      if xml_item != None:
         continue

      g_total_processed_items = g_total_processed_items + 1

      xml_item = create_xml_item( f ) 
      xml_item.setAttribute( "add", current_date_time() )
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

   #if opt.update_mode:
   #   return

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
      xml_item.setAttribute( "size", str( f_type.size ) )
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
      xml_item.setAttribute( "fdate", f_type.date_modified )
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
         xml_item.setAttribute("srate", str(f.audio_type.info.sample_rate) )
         xml_item.setAttribute("length", time.strftime("%H:%M:%S", time.gmtime( f.audio_type.info.length ) ) )

      except Exception as e:
         print("** Error getting FLAC info: " + repr(e) )
         xml_item.setAttribute("srate", "0")
         xml_item.setAttribute("length", "0")
         xml_item.setAttribute("audio_error", "FLAC exception: " + repr(e) )

#
#
#
def set_xml_album_size( xml_album, album_size ):
   #xml_album.setAttribute("size", "{0:.2f}".format( album_size / 1024.0 / 1024.0 ) + " Mb" )
   xml_album.setAttribute("size", str( album_size ) )



#
# return first node matching or None
#
def find_node( parent_node, node_name ):
   for subnode in parent_node.getElementsByTagName( node_name ):
      return subnode
   return None


#
# return node for attrib_key = attrib_value
#
def find_node_by_value( parent_node, node_name, a_attrib_key, a_attrib_value ):
   for subnode in parent_node.getElementsByTagName( node_name ):
      attr = subnode.attributes[ a_attrib_key ]
      if attr != None:
         if a_attrib_value == attr.value:
            return subnode
   return None



#
# Returns node attribute key value ( None if not node )
#
def node_attribute( node, a_attrib_key ):
   #print( "node_attribute for " + a_attrib_key )

   if node == None:
      return None

   atr = node.attributes[ a_attrib_key ]
   if atr == None:
      return None

   return atr.value



#
# create a new album entry inside <updates><update_serie>
# it's only interesting info, the real album data is within <section>
#
def create_new_update_entry( tag_name, desc ):
   
   global xml_current_updates

   if xml_current_updates == None:
      xml_current_updates = xml_doc.createElement( "update" )
      xml_current_updates.setAttribute( "date", current_date_time() )
      xml_updates.appendChild( xml_current_updates )

   xml_upd_new = xml_doc.createElement( tag_name )
   xml_upd_new.appendChild( xml_doc.createTextNode( desc ) )
   xml_current_updates.appendChild( xml_upd_new )




#
# Parse opr.source_path to create all implicit initial passed subfolders if not previously created
# sets the initial xml_source_parent
#

def create_xml_sources_entries():

   global xml_source_parent
   global xml_root
   
   # get main <sources> section
   xml_source_parent = find_node( xml_doc, "sources" )  

   if xml_source_parent == None:
      Log.log_error("Not found main <sources> xml section")
      exit(1)

   # iterate over each source path folder
   for e in opt.source_root_path.split('/'):
      if e==None or e=="":
         continue

      print "************ iterating source: " + e

      # do not create the last one, it will be created later
      #if e == opt.source_root_path_last_folder:
      #   continue

      print "************ processing source: " + e

      nd = find_node_by_value( xml_source_parent, "source", "src", e )
      if nd == None:
         xml_source_parent = create_xml_source( xml_source_parent, e ) 
      else:
         xml_source_parent = nd


   # build last folder
   nd = find_node_by_value( xml_source_parent, "source", "src", opt.source_root_path_last_folder )
   if nd == None:
      xml_source_parent = create_xml_source( xml_source_parent, opt.source_root_path_last_folder ) 
   else:
      xml_source_parent = nd



#
# return created source node
#
def create_xml_source( xml_source_parent, source_name ):

   Log.log("Creating new source folder: " + source_name )
   
   xml_source = xml_doc.createElement( "source" )
   xml_source.setAttribute( "src", source_name )
   xml_source.setAttribute( "created", current_date_time() )
   xml_source_parent.appendChild( xml_source )

   return xml_source



#
# Initialize XML target file, either creating a new one or importing existing if in "update_mode"
# needed in case of update mode
#
def initialize_target_xml( full_output_filename ):

   global opt

   # need to create it "virtually" due to design and traverse items
   #if opt.dry_run and opt.update_mode == False:
   #   create_memory_xml()
   #   return

   # create target folder
   if not os.path.exists(opt.output_path):
      Log.log( "Creating folder: " + opt.output_path )
      os.makedirs(opt.output_path)

   # check if target file exists
   is_file = os.path.isfile( full_output_filename )

   # asks before overwrite existing one
   #if opt.dry_run == False and opt.update_mode == False and is_file:
   #   resp = raw_input( "\nFile: " + full_output_filename + " exists. \ndo you want to be overwritted (y/N) ?" )
   #   if resp!="y" and resp!="Y":
   #      Log.log( "\nOperation canceled by the user" )
   #      exit(0)

   # we're updating so exit if file does not exists
   #if opt.update_mode and is_file == False:
   #   Log.log("\nCan not update a non existing target file: " + full_output_filename )
   #   exit(0)

   # open and set working variables if file exists and we're updating
   #if opt.update_mode and is_file:
   if is_file:
      load_target_xml_in_memory( full_output_filename )
   else:
      create_target_xml_in_memory()


   # create initial folders if needed ( opt.source_path argument )
   create_xml_sources_entries()






#
# Creating new xml
#
#def create_target_xml():
def create_target_xml_in_memory():

   global xml_doc
   global xml_root
   global xml_section
   global xml_updates
   global xml_source_parent

   xml_doc = Document()
   xml_root = xml_doc.createElement("root")
   xml_root.setAttribute( "version", XmlManager.xml_file_version )
   xml_doc.appendChild( xml_root )

   xml_updates = xml_doc.createElement("updates")
   xml_root.appendChild(xml_updates)

   xml_section = xml_doc.createElement("section")
   xml_root.appendChild(xml_section)

   xml_section.setAttribute( "id", opt.section_id )
   xml_section.setAttribute( "source", opt.source_root_path )
   #xml_section.setAttribute( "since_date", opt.since_date )
   xml_section.setAttribute( "create", current_date_time() )

   #date = current_date
   #xml_section.setAttribute( "created_date", created_date )
   #xml_section.setAttribute( "last_update", created_date )

   # note this are written at the end
   #xml_section.setAttribute( "total_albums", str(total_saved_albums) )
   #xml_section.setAttribute( "total_albums_size", tot_sz_gb )
   #xml_section.setAttribute( "total_items", str(g_total_processed_items) )

   # main sources section
   xml_source_parent = xml_doc.createElement( "sources" )
   xml_root.appendChild( xml_source_parent )





#
# Load and existing target xml
#
def load_target_xml_in_memory( full_output_filename ):
   
   global xml_doc
   global xml_section
   global xml_updates
   global opt

   with open( full_output_filename, "r" ) as f:
      s = f.read()
      s = s.replace('\r\n','')
      #s = s.rstrip()
      #s = s.lstrip()

   #xml_doc = parse( full_output_filename )
   xml_doc = parseString( s )

   #sec_node = xml_mngr.find_node( xml_doc, "section" )
   #opt.section_id = sec_node.attribute("id")
   #opt.source_folder = sec_node.attribute("source")

   xml_upds_list = xml_doc.getElementsByTagName( "updates" )
   xml_updates = xml_upds_list[0]

   if xml_updates == None:
      Log.log_error( "Oops! not found updates section node while loading xml" )
      exit(1)

   xml_sections_list = xml_doc.getElementsByTagName( "section" )
   xml_section = xml_sections_list[0]

   if xml_section == None:
      Log.log_error( "Oops! not found section node while loading xml" )
      exit(1)

   #attr_src = xml_section.attributes[ "source" ]
   #if attr_src != None:
   #   opt.source_root_path = attr_src.value

   attr_id = xml_section.attributes[ "id" ]
   if attr_id != None:
      opt.section_id = attr_id.value



#
# Saves and unlink xml
# also updates tag <section> with total albums and total albums size
#

def save_xml( full_filename ):
   
   tot_sz_gb = "{0:.2f}".format( total_saved_albums_size / 1024.0 / 1024.0 / 1024.0 ) + " Gb"

   Log.log("")
   Log.log( "  . total albums found : " + str(total_saved_albums) )
   Log.log( "  . total items found  : " + str(g_total_processed_items) )
   Log.log( "  . total size : " + tot_sz_gb + "  ( " + str(total_saved_albums_size/1024.0/1024.0) + " Mb )"  )

   if opt.dry_run:
      return

   xml_section.setAttribute( "albums", str(total_saved_albums) )
   xml_section.setAttribute( "items", str(g_total_processed_items) )
   xml_section.setAttribute( "size", tot_sz_gb )
   xml_section.setAttribute( "update", current_date_time() )

   #if opt.update_mode == False or ( opt.update_mode and g_total_processed_items ):
  
   f = open( full_filename, "wb" )
   #xml_doc.writexml( f, xml_doc.toprettyxml(indent='  ', newl='\n' ) ) #indent="  ", addindent="  ", newl="\r\n" )
   # if opt.update_mode:
   #    s1 = xml_doc.toxml()
   #    #xml_doc.writexml( f, newl='\n' )
   #    #xml_doc.writexml( f )
   #    xml_doc.writexml( f, indent='  ', addindent='  ', newl='\r\n' )
   # else:
   #    xml_doc.writexml( f, indent='  ', addindent='  ', newl='\r\n' )
   #    #xml_doc.writexml( f )

   xml_doc.writexml( f, indent='  ', addindent='  ', newl='\r\n' )

   Log.log( "\nData have been saved to the XML file: " + full_filename )

   # last unlink xml
   xml_doc.unlink()






#
# settings info
#
def show_settings_info( title, request_user_confirm = False ):

   str_mode = None

   if opt.dry_run:
      str_mode = "dry run"

   # if opt.update_mode:
   #    if str_mode:
   #       str_mode = str_mode + " and update"
   #    else:
   #       str_mode = "update"

   if str_mode == None:
      str_mode = "normal"

   Log.log("")
   Log.log("  " + title )
   Log.log("")
   Log.log("  - source root_path       : " + str(opt.source_root_path) )
   Log.log("  - source starting folder : " + str(opt.source_root_path_last_folder) )
   Log.log("  - output file      : " + full_output_filename )
   Log.log("  - section id       : " + str(opt.section_id) )
   Log.log("  - since date       : " + opt.since_date )
   Log.log("  - supported audio file types   : " + str(supported_audio_file_types) ) 
   Log.log("  - supported comment file types : " + str(supported_comment_file_types)) 
   Log.log("  - verbose : " + str(opt.verbose_mode)) 
   Log.log("  - dry_run mode : " + str(opt.dry_run)) 
   # Log.log("  - update : " + str(opt.update_mode)) 
   Log.log("")
   Log.log("  Notes:")
   Log.log("    * folders/albums with no audio files will not be added by default" )
   Log.log("    * commented files with characters '-' in its name will be marked with '***' and replaced with ' '")
   Log.log("")
   Log.log("  - working mode     : " + str_mode )

   if request_user_confirm:
      resp = raw_input( "\nContinue with this settings (Y/n) ?" )
      if resp=="n" or resp=="N":
         Log.log( "\nOperation canceled by the user" )
         exit(0)






#
# Main
# TODO: Pending refactor whole main entry stuff
#

xml_doc = None
xml_root = None
xml_section = None
xml_updates = None
xml_current_updates = None
xml_parent_source = None

#xml_mngr = xml_manager()


#xml_doc = Document()
#xml_root = xml_doc.createElement("root")
#xml_doc.appendChild( xml_root )


supported_audio_file_types=[ 'aac', 'aiff', 'alac', 'cue', 'dsd', 'flac', 'mp3','m3u','m4a','wav' ]
supported_comment_file_types = ['jpg', 'png', 'gif', 'txt' ]

p = optparse.OptionParser()

p.add_option("-s", "--source_root_path", action="store", type="string", dest="source_root_path", help="source path to start search" )
p.add_option("-t", "--target_file", action="store", type="string", dest="target_file", default=None, help="optional alternative target file name [ ak_master_data.xml by default ]" )
p.add_option("-i", "--section_id", action="store", type="string", dest="section_id", help="optional section id. Default last source path" )
p.add_option("-o", "--output_path", action="store", type="string", dest="output_path", default="output_data", help="optional output generated files path" )
p.add_option("-e", "--since_date", action="store", type="string", dest="since_date", default="1900-01-01", help="optional, files since date yyyy-mm-dd" )
p.add_option("-n", "--no_verbose", action="store_true", dest="verbose_mode", help="no verbose mode" )
p.add_option("-d", "--dry_run", action="store_true", dest="dry_run", help="dry_run mode" )
# p.add_option("-u", "--update", action="store_true", dest="update_mode", help="update existing target_file with new existing xml_source_path items" )

opt,args = p.parse_args()


# if opt.update_mode == None:
#    opt.update_mode = False
# else:
#    opt.update_mode = True


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

# store the last part of full path, I mean the last folder ( ex: "Volumes/media/audio/flac/w" -> "w" )
opt.source_root_path_last_folder = os.path.basename( os.path.normpath( opt.source_root_path ) ); 

opt.source_root_path = opt.source_root_path[:-len(opt.source_root_path_last_folder)]


if opt.section_id == None: 
   #opt.section_id = opt.source_root_path.replace('/','_') #os.path.basename( opt.root_path ) + "_"
   opt.section_id = os.path.basename( os.path.normpath( opt.source_root_path ) ); 
   # remove first '/'
   #opt.section_id = opt.section_id[:0] + opt.section_id[1:]

if opt.target_file == None:
   opt.target_file = "ak_master_data.xml" #opt.section_id + ".xml"


full_output_filename = opt.output_path + "/" + opt.target_file


#
# if update selected then source path will be retrieved from existing taget xml
#
#if opt.update_mode:
#   opt.section_id = None
#   #opt.source_root_path = None


#
# show settings values and asks to continue
#
show_settings_info( "AK_GENERATE Current Settings", True )





#
# checks whether output file exists
# needed in case of update mode
#
initialize_target_xml( full_output_filename )




#
# start main operation
#
total_saved_albums = 0
g_total_processed_items = 0
total_saved_albums_size = 0



traverse_folder( opt.source_root_path_last_folder, True )
#traverse_folder( )


#
show_settings_info("AK_GENERATE Used Settings")


# 
#
save_xml( full_output_filename )



