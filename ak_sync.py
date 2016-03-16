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

def show_item_info( item_node, n_count, n_total, tot_size_kb ):
   #size_kb = str(format(tot_size_kb,"0.0f")) + " Kb" 
   #size_mb = str( format(tot_size_kb / 1024.0, "0.2f") ) + " Mb"
   #print( str(n_count) + "/" + str(n_total) + " : " + item_node.attributes['src'].value + " | " + size_kb + " -> " + size_mb )
   core.utils.log( str( n_count ) + "/" + str( n_total ) + " : " + item_node.attributes['src'].value )


#def get_source_size( section_node, album_node, item_node ): 
#   src_folder = section_node.attributes['source_root'].value + "/" + item_node.attributes['src'].value
#   src_file = item_node.attributes['file'].value
#
#   du_str='du -ksc \"' + src_folder + '\"/' #+ src_file
#
#   if src_file.find("*") != -1:
#      du_str = du_str + src_file
#      #err=os.system('du -ch \"' + src_folder + '\"/' + src_file )
#   else:
#      #err=os.system('du -ch \"' + src_folder + '\"/' + '\"' + src_file + '\"' )
#      du_str = du_str +  '\"' + src_file + '\"'
#
#   #err=os.system( du_str )
#   p1=subprocess.Popen( du_str, shell=True, stdout=subprocess.PIPE)
#   p2=subprocess.Popen("tail -1", shell=True, stdin=p1.stdout,stdout=subprocess.PIPE)
#   p3=subprocess.Popen("cut -f1", shell=True, stdin=p2.stdout,stdout=subprocess.PIPE)
#
#   items_size = int( p3.stdout.read() )
#   #print(p1.stdout.read())
#   #print("Total size : " + str( items_size ) + " kb" )
#   
#   return items_size



def make_target_path( target_path ):

   try:
      subprocess.check_call( [ "mkdir", "-p", target_path ] )
      #err = os.system('mkdir -p \"' + target_path + '\"');
      print("Created path: " + target_path)
   except Exception as e:
      print("Ops! error creating target path: " + target_path)
      print ("Exception:\n" + repr(e) )


def copy_file( source_path, target_path, f ): 
   #print("source: " + source_path )
   #print("target: " + target_path + f )
   
   if target_path == None:
      print("ERROR!! target_path is NULL")
      return 0

   #source_path_with_f = "\"" + source_path + f + "\""
   source_path_with_f = source_path + f
   #target_path_with_f = "\"" + target_path + f + "\""
   target_path_with_f = target_path + f

   if os.path.exists( source_path + f ) == False:
      print("warning!! source file not found")
      return 0

   sz_1 = os.path.getsize( source_path_with_f)
   
   if os.path.exists( target_path + f ):
      # if same size do not copy
      print source_path_with_f
      sz_2 = os.path.getsize( target_path_with_f )
      if os.path.getsize( source_path_with_f ) == os.path.getsize( target_path_with_f ):
         print "...not copied because it exists on target with same size"
         return 0

      #print "...different size"
      #print("warning!! file not copied because it exists on target folder")

   try:
      #print "--->>>>1111 " + source_path_with_f
      #print "--->>>>2222 " + target_path
      #process = subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE)
      #stdout = process.communicate()[0]
      #print '............. STDOUT:{}'.format(stdout)
      sys.stdout.write("copying " + format( sz_1 / 1024.0 / 1024.0, "0.2f" ) + " Mb.........." )
      sys.stdout.flush()
      subprocess.check_call( "cp " + "\"" + source_path_with_f + "\" \"" + target_path + "\"", shell = True )
      sys.stdout.write("Ok\n")

   except subprocess.CalledProcessError as e:
      #if (err != 0) and (err != 1):
      print("ERROR!!!! something wrong copying file" )

      print ("Exception:\n" + repr(e) )
      print (" cmd:" + str(e.cmd) )
      print (" returncode: " + str(e.returncode) )
      print (" output: " + str(e.output) )
      return 0

   return sz_1



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
   if opt.dry_run != False:
      if opt.target_path != None:
         make_target_path( tgt_cpy )

   tot_size=0
   failed_items = 0
   copied_items = 0
   processed_items = 0
   n=1

   for item_node in itemslist:

      item_size=0

      try:
         src_item = src_folder + item_node.attributes['src'].value 
         #print "--->>>> " + src_item
         # size in kb
         item_size = os.path.getsize( src_item ) / 1024.0
      except:
         show_item_info( item_node, n, total_items, item_size )
         core.utils.log_error("ERROR! trying to get item size " )
         n=n+1
         failed_items = failed_items + 1
         continue

      show_item_info( item_node, n, total_items, item_size )

      # 
      # only copy files if target_path argument is passed and not in dry_run mode
      #
      if opt.dry_run == False and opt.target_path != None:
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



   if failed_items:
      core.utils.log("Failed items " + str(failed_items) + " of " + str(total_items) )
   
   if opt.dry_run == False:
      if copied_items:
         core.utils.log("Copied items " + str(copied_items) + " of " + str(total_items) )
      
      if tot_size:
         core.utils.log("Total album copied size: " + str( format( tot_size / 1024.0, "0.2f" ) ) + "Mb" )

   else:
      core.utils.log("Processed items " + str(processed_items) + " of " + str(total_items) )
      core.utils.log("Total album size: " + str( format( tot_size / 1024.0, "0.2f" ) ) + "Mb" )
      

   core.utils.log("")

   global g_total_failed_items
   global g_total_copied_items
   global g_total_processed_items

   g_total_failed_items = g_total_failed_items + failed_items
   g_total_copied_items = g_total_copied_items + copied_items
   g_total_processed_items = g_total_processed_items + processed_items

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

   for sec in sectionlist:
      show_section_info( sec, n_sec, total_sections )
      tot_size = tot_size + process_xml_albums(sec)
      n_sec=n_sec+1

   tot_size_mb = format( tot_size / 1024.0, "0.1f" ) + " Mb"
   tot_size_gb = format( tot_size / 1024.0 / 1024.0, "0.2f" ) + " Gb"
   core.utils.log("\n** Source" )
   core.utils.log("   xml data file : " + opt.xml_data_file )
   core.utils.log("   Total Final Size : " + tot_size_gb + " ( " + tot_size_mb + " ) " )
   core.utils.log("   total processed albums : " + str( g_total_albums ) )
   core.utils.log("   total processed items : " + str( g_total_processed_items ) )
   core.utils.log("   total failed items : " + str( g_total_failed_items ) )
   core.utils.log("   total copied items : " + str( g_total_copied_items ) )

   if opt.target_path != None:
      device_size( opt.target_path )
   else:
      device_size("/")




def device_size( target_folder ):

   df = subprocess.Popen(["df", "-h", target_folder], stdout=subprocess.PIPE)
   output = df.communicate()[0]
   device, size, used, available, percent, iused, ifree, iused_percent, mountpoint = output.split("\n")[1].split()
   core.utils.log("\n** Target" )
   core.utils.log("   folder : " + target_folder )
   core.utils.log("   device : " + device )
   core.utils.log("   size : " + size )
   core.utils.log("   used : " + used )
   core.utils.log("   available : " + available )



def process_arg_options():

   p = optparse.OptionParser()

   p.add_option("-f", "--data_file", action="store", type="string", dest="xml_data_file",
      help="Input XML data file generated with 'ak_generate.py' with source data info to be copied or calculated" )

   p.add_option("-t", "--target_path", action="store", type="string", dest="target_path")
   p.add_option("-d", "--dry_run", action="store_true", dest="dry_run", help="Run in dry_run mode to estimate total size")
   #p.add_option("-c", "--copy_data", action="store_true", dest="copy_data")
   #p.set_defaults(target_path="")

   opt, args = p.parse_args()
   #print("args: ", args)


   if opt.target_path != None and opt.target_path.endswith('/'):
      opt.target_path = opt.target_path[:-1]

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

g_total_failed_items = 0
g_total_copied_items = 0
g_total_processed_items = 0
g_total_albums = 0


opt = process_arg_options()

xmldoc = minidom.parse( opt.xml_data_file )

process_xml()


