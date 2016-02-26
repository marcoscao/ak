import os
import sys
import optparse
import subprocess
from xml.dom import minidom


def show_section_info( sec_node, n_count, n_total ):
   print("Section " + str(n_count) + "/" + str(n_total) + "  id: " + sec_node.attributes['id'].value)
   print("Source root : " + sec_node.attributes['source'].value)

def show_album_info( album_node, n_count, n_total ):
   itemslist = album_node.getElementsByTagName('item')
   total_items = len(itemslist)
   print("Album " + str(n_count) + "/" + str(n_total) + ": " + album_node.attributes['src'].value \
      + "  |  Total items: " + str(total_items) )

def show_item_info( item_node, n_count, n_total, tot_size_kb ):
   size_kb = str(format(tot_size_kb,"0.0f")) + " Kb" 
   size_mb = str( format(tot_size_kb / 1024.0, "0.2f") ) + " Mb"
   print( str(n_count) + "/" + str(n_total) + " : " + item_node.attributes['src'].value + " | " + size_kb + " -> " + size_mb )


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
   err = os.system('mkdir -p \"' + target_path + '\"');
   if err != 0:
      print("Ops! error creating target path: " + target_path)
   else:
      print("Created path: " + target_path)


def copy_file( source_path, target_path, f ): 
   #print("source: " + source_path )
   #print("target: " + target_path + f )
   
   if target_path == None:
      print("ERROR!! target_path is NULL")
      return False

   source_path_with_f = "\"" + source_path + f + "\""

   if os.path.exists( source_path + f ) == False:
      print("warning!! source file not found")
      return False

   if os.path.exists( target_path + f ):
      print("warning!! file not copied because it exists on target folder")
      return False

   err=os.system("cp -n " + source_path_with_f + " \"" + target_path + "\"" )
   if (err != 0) and (err != 1):
      print("ERROR!!!! something wrong copying file" )
      return False

   return True



def process_xml_items( section_node, album_node ):
   src_folder = section_node.attributes['source'].value + "/" + album_node.attributes['src'].value

   itemslist = album_node.getElementsByTagName('item')
   total_items = len(itemslist)
   #print("Total items    : " + str(total_items) )
      
   tgt_cpy = None
   if opt.target_path != None:
      tgt_cpy = opt.target_path + "/" + album_node.attributes['src'].value 
   
   src_cpy = src_folder + "/" 
   
   # 
   # only create folders if target_path argument was passed
   # otherwise means we are running in dry-mode to calculate required size
   #
   if opt.target_path != None:
      make_target_path( tgt_cpy )

   tot_size=0
   failed_items = 0
   n=1

   for item_node in itemslist:

      item_size=0
      err_size = False

      try:
         src_item = src_folder + "/" + item_node.attributes['src'].value 
         # size in kb
         item_size = os.path.getsize( src_item ) / 1024.0
      except:
         err_size = True

      show_item_info( item_node, n, total_items, item_size )
      if err_size:
         print("ERROR! Not found item trying to get its size " )
         n=n+1
         failed_items = failed_items + 1
         continue

      # 
      # only copy files if target_path argument is passed
      # if not is ussed to calculate required size
      #
      if opt.target_path != None:
         if copy_file( src_cpy, tgt_cpy, item_node.attributes['src'].value ) == False:
            failed_items = failed_items + 1

      n=n+1
      tot_size = tot_size + item_size

   print("Failed items " + str(failed_items) + " out of " + str(total_items) )
   print("Total Album size: " + str(format(tot_size,"0.0f")) + " kb -> " + str(format(tot_size/1024, "0.2f"))+"Mb")
   print("")
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

   tot_size_mb = format( tot_size / 1024, "0.2f" ) + " Mb"
   tot_size_gb = format( float(tot_size / 1024.0 ) / 1024.0, "0.2f" ) + " Gb"
   print("Total final size : " + str( format(tot_size,"0.0f")) + " Kb  |  " + tot_size_mb + "  |  " + tot_size_gb )




def process_arg_options():

   p = optparse.OptionParser()

   p.add_option("-f", "--data_file", action="store", type="string", dest="xml_data_file",
      help="Input XML data file generated with 'ak_generate.py' with source data info to be copied or calculated" )

   p.add_option("-t", "--target_path", action="store", type="string", dest="target_path")
   #p.add_option("-c", "--copy_data", action="store_true", dest="copy_data")
   #p.set_defaults(target_path="")

   opt, args = p.parse_args()
   #print("args: ", args)

   if opt.xml_data_file == None: 
      print("Plese enter XML data file. You can use -h to show currently available options")
      sys.exit(1)

   if opt.target_path != None and opt.target_path.endswith('/'):
      opt.target_path = opt.target_path[:-1]

   print("xml_data_file : " + opt.xml_data_file )

   if opt.target_path == None:
      print("target_path : [ NO TARGET PATH ]")
   else:
      print("target_path   : " + opt.target_path )

   return opt




#
# Main
#

opt = process_arg_options()

xmldoc = minidom.parse( opt.xml_data_file )

process_xml()


