import core.utils

import os
import sys
import optparse
import subprocess
from codecs import open
from xml.dom import minidom


def show_section_info( sec_node, n_count, n_total ):
   core.utils.log("Section " + str(n_count) + "/" + str(n_total) + "  id: " + sec_node.attributes['id'].value)
   core.utils.log("Source root : " + sec_node.attributes['source'].value)

def show_album_info( album_node, n_count, n_total ):
   #itemslist = album_node.getElementsByTagName('item')
   #total_items = len(itemslist)
   #print("Album " + str(n_count) + "/" + str(n_total) + ": " + album_node.attributes['src'].value + "  |  Total items: " + str(total_items) )
   core.utils.log("Album " + str(n_count) + "/" + str(n_total) + ": " + album_node.attributes['src'].value )

#def show_item_info( item_node, n_count, n_total, tot_size_kb ):
def show_item_info( item_node, n_count, n_total ):
   #size_kb = str(format(tot_size_kb,"0.0f")) + " Kb" 
   #size_mb = str( format(tot_size_kb / 1024.0, "0.2f") ) + " Mb"
   #print( str(n_count) + "/" + str(n_total) + " : " + item_node.attributes['src'].value + " | " + size_kb + " -> " + size_mb )
   core.utils.log( str( n_count ) + "/" + str( n_total ) + " : " + item_node.attributes['src'].value, opt.verbose_mode )




def make_target_path( target_path ):

   try:
      subprocess.check_call( [ "mkdir", "-p", target_path ] )
      #err = os.system('mkdir -p \"' + target_path + '\"');
      core.utils.log( "Created path: " + target_path )
   except Exception as e:
      core.utils.log_error("Ops! error creating target path: " + target_path )
      core.utils.log_error ("Exception:\n" + repr(e) )




#
# no real copy if in dry_run mode
#
def copy_file( source_path, target_path, f ): 
   
   if target_path == None and opt.dry_run == False:
      print("ERROR!! target_path is NULL")
      return 0

   global g_total_failed_source_items
   global g_total_failed_target_items
   global g_total_failed_items
   global g_total_copied_items
   global g_total_processed_items
   
   g_total_processed_items = g_total_processed_items + 1

   source_path_with_f = source_path + f
   target_path_with_f = target_path + f

   # if not exists return 0 size
   if os.path.exists( source_path_with_f ) == False:
      core.utils.log( "Error! not found source file: " + source_path_with_f )
      g_total_failed_source_items = g_total_failed_source_items + 1
      raise

   try:
      sz_1 = os.path.getsize( source_path_with_f)
   except:
      core.utils.log("Error getting size of source file: " + source_path_with_f )
      g_total_failed_source_items = g_total_failed_source_items + 1
      raise


   #
   # if target exists and same size do not copy it
   #
   if os.path.exists( target_path + f ):
      #print source_path_with_f
      try:
         sz_2 = os.path.getsize( target_path_with_f )
      except:
         core.utils.log("Error getting size of target file: " + target_path_with_f )
         g_total_failed_target_items = g_total_failed_target_items + 1
         raise

      if sz_1 == sz_2:
         core.utils.log( "...not copied because it exists on target with same size", opt.verbose_mode )
         return 0

   try:
      if opt.dry_run == False or opt.verbose_mode:
         sys.stdout.write("copying " + format( sz_1 / 1024.0 / 1024.0, "0.2f" ) + " Mb.........." )
         sys.stdout.flush()
      
      if opt.dry_run == False:
         subprocess.check_call( "cp " + "\"" + source_path_with_f + "\" \"" + target_path + "\"", shell = True )
     
      if opt.dry_run == False or opt.verbose_mode:
         sys.stdout.write("Ok\n")
      
      g_total_copied_items = g_total_copied_items + 1

   except subprocess.CalledProcessError as e:
      core.utils.log("ERROR!!!! something wrong copying file" )
      core.utils.log ("Exception:\n" + repr(e) )
      core.utils.log (" cmd:" + str(e.cmd) )
      core.utils.log (" returncode: " + str(e.returncode) )
      core.utils.log (" output: " + str(e.output) )
      g_total_failed_items = g_total_failed_items + 1
      raise

   return (sz_1 / 1024)



def process_xml_items( section_node, album_node ):
   src_folder = section_node.attributes['source'].value + "/" + album_node.attributes['src'].value

   itemslist = album_node.getElementsByTagName('item')
   total_items = len(itemslist)
   #print("Total items    : " + str(total_items) )
      
   tgt_cpy = None
   if opt.target_path != None:
      tgt_cpy = opt.target_path + "/" + section_node.attributes['id'].value + "/" + album_node.attributes['src'].value 
   
   src_cpy = src_folder #+ "/" 
   
   # 
   # only create folders if target_path argument was passed
   # otherwise means we are running in dry-mode to calculate required size
   #
   if opt.dry_run == False:
      if opt.target_path != None:
         make_target_path( tgt_cpy )

   tot_size=0
   failed_items = 0
   copied_items = 0
   processed_items = 0
   n=1

   for item_node in itemslist:

      item_size=0

      # try:
      #    src_item = src_folder + item_node.attributes['src'].value 
      #    #print "--->>>> " + src_item
      #    # size in kb
      #    item_size = os.path.getsize( src_item ) / 1024.0
      # except:
      #    show_item_info( item_node, n, total_items, item_size )
      #    core.utils.log_error("ERROR! trying to get item size " )
      #    n=n+1
      #    failed_items = failed_items + 1
      #    continue

      show_item_info( item_node, n, total_items )

      # 
      # ithis only copy files if target_path argument is passed and not in dry_run mode
      #
      #if opt.dry_run == False and opt.target_path != None:
      try:
         # returns real copied size, avoiding not copied existing files
         item_size = copy_file( src_cpy, tgt_cpy, item_node.attributes['src'].value )
            
         if item_size > 0:
            copied_items = copied_items + 1

      except Exception as e:
         failed_items = failed_items + 1

      n=n+1
      tot_size = tot_size + item_size
      processed_items = processed_items + 1


   core.utils.log( "Processed items " + str(processed_items) + " of " + str(total_items), opt.verbose_mode )

   if failed_items:
      core.utils.log("Failed items " + str(failed_items) )
   
   if opt.dry_run == False:
      if copied_items:
         core.utils.log("Copied items " + str(copied_items) )
   else:
      if copied_items:
         core.utils.log("Items to be copied " + str(copied_items) )

   #if tot_size:
   album_sz = str( format( tot_size / 1024.0, "0.1f" ) ) + " Mb"


   core.utils.log("Total album size of copied items: " + album_sz )
   
      
   core.utils.log("")

   return tot_size




def process_xml_albums( sec ):
   albumslist = sec.getElementsByTagName('album')
   total_albums = len(albumslist)
   print( "Number of albums found: " + str( total_albums ) )

   tot_size = 0
   n_album=1
   for album in albumslist:
      show_album_info( album, n_album, total_albums )
      tot_size = tot_size + process_xml_items( sec, album )
      n_album=n_album+1

   global g_total_albums
   g_total_albums = g_total_albums + n_album

   return tot_size




def process_xml():
   sectionlist = xmldoc.getElementsByTagName('section')
   total_sections = len(sectionlist)
   print( "Number of sections found: " + str( total_sections ) )
   print("\n")

   tot_size=0
   n_sec=1

   global g_target_path_main_folder
   global g_total_copied_size

   for sec in sectionlist:
      g_target_path_main_folder = opt.target_path + "/" + sec.attributes['id'].value + "/"

      show_section_info( sec, n_sec, total_sections )
      g_total_copied_size = g_total_copied_size + process_xml_albums(sec)
      n_sec=n_sec+1
      


   tot_size_mb = format( g_total_copied_size / 1024.0, "0.1f" ) + " Mb"
   tot_size_gb = format( g_total_copied_size / 1024.0 / 1024.0, "0.2f" ) + " Gb"
   core.utils.log("\n** Source" )
   core.utils.log("   xml data file : " + opt.xml_data_file )
   core.utils.log("   sections found : " + str( n_sec - 1 ) )
   core.utils.log("   total albums found : " + str( g_total_albums ) )
   core.utils.log("   total items found : " + str( g_total_processed_items ) )
   core.utils.log("   copied items : " + str( g_total_copied_items ) )
   core.utils.log("   failed items : " + str( g_total_failed_source_items ) )
   core.utils.log("   Total copied items size : " + tot_size_gb + " ( " + tot_size_mb + " ) " )

   if opt.target_path != None:
      device_size( opt.target_path )
   else:
      device_size("/")




def device_size( target_folder ):

   df = subprocess.Popen(["df", "-h", target_folder], stdout=subprocess.PIPE)
   output = df.communicate()[0]
   device, size, used, available, percent, iused, ifree, iused_percent, mountpoint = output.split("\n")[1].split()
   core.utils.log("\n** Target" )
   core.utils.log("   target path : " + str(target_folder) )
   core.utils.log("   main parent folder : " + str(g_target_path_main_folder) )
   core.utils.log("   copied items : " + str( g_total_copied_items ) )
   core.utils.log("   failed items : " + str( g_total_failed_target_items ) )
   core.utils.log("   device : " + device )
   core.utils.log("   size : " + size )
   core.utils.log("   used : " + used )
   core.utils.log("   available : " + available )
   #core.utils.log("   available after copy : " + str( float(available) - (g_total_sections_size/1024.0/1024.0) ) )






def process_arg_options():

   p = optparse.OptionParser()

   p.add_option("-s", "--source_file", action="store", type="string", dest="xml_data_file",
      help="Input XML data file generated with 'ak_generate.py' with source data info to be copied or calculated" )

   p.add_option("-t", "--target_path", action="store", type="string", dest="target_path")
   p.add_option("-d", "--dry_run", action="store_true", dest="dry_run", help="Run in dry_run mode to estimate total size, copied items, main folder...")
   p.add_option("-n", "--no_verbose", action="store_true", dest="verbose_mode", help="No verbose mode")
   #p.add_option("-c", "--copy_data", action="store_true", dest="copy_data")
   #p.set_defaults(target_path="")

   opt, args = p.parse_args()
   #print("args: ", args)


   if opt.target_path != None:
      if opt.target_path.endswith('/'):
         opt.target_path = opt.target_path[:-1]


   if opt.verbose_mode == None:
      opt.verbose_mode = True
   else:
      opt.verbose_mode = False


   if opt.dry_run == None:
      opt.dry_run = False
   else:
      opt.dry_run = True

   core.utils.log("- source xml data file  : " + str(opt.xml_data_file) )
   core.utils.log("- target main folder    : " + str(opt.target_path) )
   core.utils.log("- dry_run mode          : " + str(opt.dry_run) )


   if opt.xml_data_file == None: 
      core.utils.log("\nPlese enter source XML data file. You can use -h to show currently available options")
      exit(0)

   return opt



#
# Main
#

g_total_failed_source_items = 0
g_total_failed_target_items = 0
g_total_failed_items = 0
g_total_copied_items = 0
g_total_processed_items = 0
g_total_albums = 0
g_total_copied_size = 0

g_target_path_main_folder = None


opt = process_arg_options()

xmldoc = minidom.parse( opt.xml_data_file )
      


process_xml()


