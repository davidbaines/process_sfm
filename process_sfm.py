#! /usr/bin/python3
# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in c:\Users\David\Documents\Importing\ -in "C:\Users\David\Documents\Importing\Romblomanon\Davids Work\Rodi.sfm" 
# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in "c:\Users\David\Documents\Importing\ -in "C:\Users\David\Documents\Importing\Romblomanon\Toolbox-Unicode\PHDIC.TYP"

# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in "C:\Users\David\Documents\Importing\Demo\Ouldeme.csv" -out "C:\Users\David\Documents\Importing\Demo\Ouldeme.sfm" -r "C:\Users\David\Documents\Importing\Demo\Ouldeme.txt"

# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in "C:\Users\David\Documents\Importing\Demo\Tobelo.csv" -out "C:\Users\David\Documents\Importing\Demo\Tobelo.sfm" -r "C:\Users\David\Documents\Importing\Demo\Tobelo.txt"
# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in c:\Users\David\Documents\Importing\ -in "C:\Users\David\Documents\Importing\Demo\Test.db" -out "C:\Users\David\Documents\Importing\Demo\Test.sfm" -r "C:\Users\David\Documents\Importing\Demo\Test.txt"
# python C:\Users\David\Documents\GitHub\process_sfm\process_sfm.py -in "C:\Users\David\Documents\Importing\Proto Sama-Bajaw\Toolbox New Project\Settings\dictionary2.sfm" -out "C:\Users\David\Documents\Importing\Proto Sama-Bajaw\Toolbox New Project\Settings\dictionary.out" -r "C:\Users\David\Documents\Importing\Proto Sama-Bajaw\Toolbox New Project\Settings\dictionary.info"

# SFM utilities
# This program should read in a text file in either SFM or csv format.
# Then process the file and output a list of markers into markers.txt
# Then you can divide the markers into:
# Entries, Senses, Examples.
# Then it should read in the same file and write it out in list format showing for each field
# whether it is part of an Entry, Sense or Example.

#Functions are :
# 0) Read in an sfm file or CSV file and convert it to a list of lists.
# 1) Replace one marker with another, or with some other marker.
# 2) In a given field find the whole field and replace the data with some other data.
# 3) Save the modified SFM file.
# 4) Write to another file summary information about the input file.
# 5) Split the entries into two files depending on whether they are simple to import or not.
# 6) Write the simple entries out to a file with their fields consistently ordered.

import unicodedata
import os, argparse, io, csv, re
import difflib 
from collections import Counter as Counter
from collections import OrderedDict as OrderedDict
from collections import namedtuple
from copy import deepcopy
from process_sfm_menu import show_menu, main_menu
from easygui import fileopenbox, filesavebox, buttonbox, choicebox, diropenbox
from alphabet_detector import AlphabetDetector
from operator import itemgetter
import process_csv
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logging.debug('A debug message!')
	
#logging.info("main_menu is {} and it's type is {}".format(main_menu,type(main_menu)))
#def fileopenbox(msg=None, title=None, default='*', filetypes=None, multiple=False)

csv.register_dialect('default')

parser = argparse.ArgumentParser(description="Find irregularities in SFM files and convert between sfm and csv")
parser.add_argument("-in", "--input",   help="Specify file to read in.")
parser.add_argument("-out" ,"--output", help="Specify the filename for the processed SFM file.")
parser.add_argument("-r" ,"--report", help="Specify the filename for a report about the data.")
#parser.add_argument( dest='feature', default=False, action='store_true')
#parser.add_argument("-dore", "--do_regex", default=False, action="store_true", help="Process the re and save file as output only.")

#logging.info("\n\n****************************\n")
#logging.info(args)

slash = '\\'
space = ' '
newline = '\n'
empty = ''
comma = ','
new_entry_markers = {'\\lx'}

Field = namedtuple("Field", ['marker','type','data','ws'])

utf8='utf-8'
overwrite = 'w'
append = 'a'
read = 'r'
readbytes = 'rb'
filemasks = ["*.csv","*.db","*.lex","*.mdf","*.sfm","*.typ"]
csv_ext = '.csv'
sfm_ext = '.sfm'
typ_ext = '.typ'

csv_exts = ['.csv']
sfm_exts = ['.sfm','.db', '.lex', '.mdf']
typ_exts = ['.typ']

#These extra markers appear in specific SFM files.
ouldeme_markers = ['\\lx2', '\\ed','\\pit', '\\gs', '\\cwl',\
'\\ir', '\\xs', '\\lv', '\\pdv', '\\par1', '\\par2', '\\par3', '\\par4',\
'\\par5', '\\lc2', '\\pdl', '\\ds', '\\a', '\\scp', \
'\\snd', '\\class', '\\gm']

#These are the specific markers used in Ouldeme in order.
ouldeme_order = ['\\lx','\\lx2','\\hm','\\lc','\\lc2','\\ph','\\pit','\\se','\\ps','\\pn','\\sn',\
'\\gv','\\dv','\\ge','\\re','\\we','\\de','\\gn','\\rn','\\wn','\\dn',\
'\\gr','\\gm','\\gs','\\rr','\\wr','\\dr','\\ds','\\lt','\\sc','\\rf','\\xv','\\xe','\\xn',\
'\\xr','\\xg','\\xs','\\uv','\\ue','\\un','\\ur','\\ev','\\ee','\\en','\\er',\
'\\ov','\\oe','\\on','\\or','\\lf','\\lv','\\le','\\ln','\\lr','\\sy','\\an',\
'\\mr','\\cf','\\ce','\\cn','\\cr','\\mn','\\va','\\ve','\\vn','\\vr',\
'\\bw','\\et','\\eg','\\es','\\ec','\\a','\\pd','\\sg','\\pl','\\rd','\\1s',\
'\\2s','\\3s','\\4s','\\1d','\\2d','\\3d','\\4d','\\1p','\\1e','\\1i',\
'\\2p','\\3p','\\4p','\\tb','\\sd','\\is','\\th','\\bb','\\pc','\\nt',\
'\\pdv', '\\par1', '\\par2', '\\par3', '\\par4','\\par5','\\pdl',\
'\\np','\\ng','\\nd','\\na','\\ns','\\nq','\\scp','\\snd','\\class','\\so','\\st','\\ir','\\cwl','\\ed','\\dt']

#There are 97 markers defined, and usually appear in this order.
mdf_order = ['\\lx','\\hm','\\lc','\\ph','\\se','\\ps','\\pn','\\sn',\
'\\gv','\\dv','\\ge','\\re','\\we','\\de','\\gn','\\rn','\\wn','\\dn',\
'\\gr','\\rr','\\wr','\\dr','\\lt','\\sc','\\rf','\\xv','\\xe','\\xn',\
'\\xr','\\xg','\\uv','\\ue','\\un','\\ur','\\ev','\\ee','\\en','\\er',\
'\\ov','\\oe','\\on','\\or','\\lf','\\le','\\ln','\\lr','\\sy','\\an',\
'\\mr','\\cf','\\ce','\\cn','\\cr','\\mn','\\va','\\ve','\\vn','\\vr',\
'\\bw','\\et','\\eg','\\es','\\ec','\\pd','\\sg','\\pl','\\rd','\\1s',\
'\\2s','\\3s','\\4s','\\1d','\\2d','\\3d','\\4d','\\1p','\\1e','\\1i',\
'\\2p','\\3p','\\4p','\\tb','\\sd','\\is','\\th','\\bb','\\pc','\\nt',\
'\\np','\\ng','\\nd','\\na','\\ns','\\nq','\\so','\\st','\\dt']

entry_fields = ['\\lx','\\lx2','\\hm','\\lc','\\lc2','\\ph','\\pit','\\va','\\ve','\\vn','\\vr',\
'\\bw','\\et','\\eg','\\es','\\ec','\\a','\\pd','\\sg','\\pl','\\rd','\\1s',\
'\\2s','\\3s','\\4s','\\1d','\\2d','\\3d','\\4d','\\1p','\\1e','\\1i',\
'\\2p','\\3p','\\4p','\\tb','\\sd','\\is','\\th','\\bb','\\pc','\\nt',\
'\\pdv', '\\par1', '\\par2', '\\par3', '\\par4','\\par5','\\pdl',\
'\\np','\\ng','\\nd','\\na','\\ns','\\nq','\\scp','\\snd','\\class','\\so','\\st','\\ir','\\cwl','\\ed','\\dt']

sense_fields = ['\\ps','\\pn','\\sn','\\gv','\\dv','\\ge','\\re','\\we','\\de','\\gn','\\rn','\\wn','\\dn',\
'\\gr','\\gm','\\gs','\\rr','\\wr','\\dr','\\ds','\\lt','\\sc','\\uv','\\ue','\\un','\\ur','\\ev','\\ee','\\en','\\er',\
'\\ov','\\oe','\\on','\\or','\\lf','\\lv','\\le','\\ln','\\lr','\\sy','\\an',\
'\\mr','\\cf','\\ce','\\cn','\\cr']

example_fields = ['\\xv','\\rf','\\xe','\\xn','\\xr','\\xg','\\xs']
	
subentry_fields = ['\\se','\\mn']

ordered_entry_dict = OrderedDict.fromkeys(mdf_order)

#These are list markers specific to the current sfm file.
#specific_list_markers = ['\\cat','\\wjk','\\ed','\\class','\\bw-s']

list_markers = ['\\ps','\\lf', '\\so', '\\pdl','\\bw' ]
#list_markers.append(specific_list_markers)

class Marker(object):
	def __init__(self, marker, name, language, parent_marker):
		self.marker = marker
		self.name = name
		self.language = language
		self.parent_marker = parent_marker

class XRef(object):

	def __init__(self,  lexeme, xref_marker, xref, exists):
		self.lexeme = lexeme
		self.xref_marker = xref_marker
		self.xref = xref
		self.exists = exists
		return
	
class XRefs(object):
	
	def find_cross_refs(self,sfm,xref_markers):
		self.crossrefs = []
		self.crossrefs.append(XRef('lexeme','\cf','word','compare',False))
		return self.crossrefs
		
	def __init__(self, sfm, xref_markers = ['\va','\sy','\se','\mn','\lv','\cf','\an']):
		self.xref_markers = xref_markers
		self.sfm = sfm
		self.crossrefs = self.find_cross_refs(sfm,xref_markers)
		return
		
def read_typ_file(filein):
	typ = read_sfm_file(filein)
	defined_markers = []
	Marker = namedtuple('Marker',['mkr','nam','mkrOverThis'])
	
# \+mkr ud
# \nam Update
# \lng Default
# \mkrOverThis lx
# \CharStyle
# \-mkr

	# Little error checking here, but file computer generated so usually consistent.
	for entry in typ:
		mkr = name = parent = None
		for field in entry:
			key , value = field
			logging.info('key is : {}, and value is {}'.format(key,value))
			if key == '\\+mkr':
				mkr = value
			if key == '\\nam':
				name = value
			if key == '\\mkrOverThis':
				parent = value
			if key == '\\-mkr':
				this_marker = Marker(mkr,name,parent)
				defined_markers.append(this_marker)
			
	groups = dict()
	for marker in defined_markers:
		logging.info(marker)
		logging.info(marker[2])
		#continue
	for marker in defined_markers:
		logging.info("There are {} defined markers.\nGroups are: {}".format(len(defined_markers),groups))
		if marker.mkrOverThis not in groups.keys():
			groups[marker.mkrOverThis] = [marker.mkr]
		elif marker.mkrOverThis:
			groups[marker.mkrOverThis].append(marker.mkr)
		else :
			raise ValueError("There seems to be a problem with marker {} in read_typ_file.".format(marker))
	
	groups_by_length = sorted(groups, key=lambda k: len(groups[k]), reverse=False)
	for k in groups_by_length:
		logging.info(k, groups[k])
	exit()
	# for group in groups:
		# logging.info("Marker for parent group: {}".format(group))
		# logging.info("{}".format(groups[group]))

	logging.info("\nGroups found are as follows:\n{}".format(groups))
	return typ, groups

def get_lexemes(sfm):
	lexemes = []
	for entry in sfm:
		for marker, data in entry:
			if marker == '\\lx':
				lexemes.append(data)
				break
	return sorted(lexemes)
	

def num_to_column(num):
	letters = ''
	while num:
		mod = (num - 1) % 26
		letters += chr(mod + 65)
		num = (num - 1) // 26
	return ''.join(reversed(letters))


def output_counter(c,title,limit=0,filename='',mode=append):
	'''Display onscreen or write to a file the information from a Counter, optionally limited to counts above a given threshold.'''
	
	lines = []
#	lines.append("\n---------------This is start of the output from output_counter---------------\n")
#	lines.append("\n---------------Limit is set to {}---------------\n".format(limit))

	spacing_str_counts = "{0:>7d} : {1:<s}"
	spacing_str_header = "{0:>7s} : {1:<s}"
	column1 = "Count"
	column2 = "Item"

	column_heading = spacing_str_header.format(column1,column2)
	
	for counted_thing in list(c.most_common()):
		thing_counted = counted_thing[0]
		count = int(counted_thing[1])
		
		if count >= limit :#and thing_counted != '':
			line = spacing_str_counts.format(count, thing_counted)
			lines.append(line)
	
#	lines.append("\n---------------This is the end of the output from output_counter---------------\n")
	if lines and filename :	
		with io.open(filename,mode,encoding=utf8) as out:
			out.write(title + newline)
			out.write(column_heading + newline)
			for line in lines:
				out.write(line + newline)
			out.write(newline)
	elif lines and not filename :
		print(title)
		print(column_heading)
		for line in lines:
			print(line)
				
	return None


def writemarkers(marker_count,marker_count_with_data,emtpy_marker_count,filename,write_mode=append):
	'''Write to a file information about the frequency of markers and markers with data.'''
	logging.info("\nIn writemarkers")
	logging.info("Marker_count is \n{}".format(marker_count))
	logging.info("Marker_count_with_data is \n{}".format(marker_count_with_data))
	logging.info("Empty_marker_count is \n{}".format(emtpy_marker_count))
	
	with io.open(filename,write_mode,encoding=utf8) as out:
		out.write("\n---------------This is start of the output from writemarkers---------------\n")
		out.write("{0:<8s}{1:>10s}{2:>8s}{3:>10s}\n".format('Marker','With data','Empty','Total'))
		for m, count in marker_count.most_common():
			out.write("{0:<8s}{1:>10d}{2:>8d}{3:>10d}\n".format(m,marker_count_with_data[m],emtpy_marker_count[m],marker_count[m]))
		out.write("\n---------------This is the end of the output from writemarkers---------------\n")
	return
	
def printmarkers(marker_count,marker_count_with_data):
	title = "{0:<8s}{1:>10s}{2:>8s}{3:>10s}\n".format('Marker','With data','Empty','Total')
	lines = []
	for m, count in marker_count.most_common():
		lines.append(["{0:<8s}{1:>10d}{2:>8d}{3:>10d}".format(m,marker_count_with_data[m],count - marker_count_with_data[m],count)])

	print(title)
	for line in lines:
		print(line[0])
	print()
	return 
	
def print_sfm(sfm, maximum):
	
	for entry in sfm[0:maximum]:
		for field in entry:
			marker , data = field
			print(marker,data)
		print()
	return
	
def sort_sfm(sfm, sort_by = 'lexeme', rev = False):
#Sort the sfm entries. Either sort alphabetically on the lexeme form or by the number of field in the entry.
#To sort longest first requires 'reverse=True' in the sorted function.

	if sort_by == 'lexeme' :
		return sorted(sfm, key=lambda x: x[0][1], reverse = rev)
	elif sort_by == 'shortest_first' :
		return sorted(sfm, key=lambda x: len(x), reverse = rev)
	return	

def output_markers(marker_count,marker_count_with_data,emtpy_marker_count,filename = '',write_mode=append):
	logging.info("\nIn output_markers")
	logging.info("Marker_count is \n{}".format(marker_count))
	logging.info("Marker_count_with_data is \n{}".format(marker_count_with_data))
	logging.info("Empty_marker_count is \n{}".format(emtpy_marker_count))
	
	title = "{0:<8s}{1:>10s}{2:>8s}{3:>10s}".format('Marker','With data','THIS','Total')
	lines = ["\n---------------This is start of the output from output markers---------------\n"]
	for m, count in marker_count.most_common():
		lines.append(["{0:<8s}{1:>10d}{2:>8d}{3:>10d}".format(m,marker_count_with_data[m],emtpy_marker_count[m],count)])
	lines.append("\n---------------This is the end of the output from output markers---------------\n")	
	
	if filename == '' and lines :
		print(newline)
		print(title)
		for line in lines:
			print(line[0])
		print()
		
	elif lines :
		with io.open(filename,write_mode,encoding=utf8) as out:
			out.write(title + newline)			
			for line in lines:
				out.write(line[0] + newline)
			out.write(newline)
	logging.info("Leaving output_markers\n")
	return
	
def sfm_from_list(sfmlist):
	sfm = []
	entry = []
	marker_count = Counter()
	marker_count_with_data = Counter()
	emtpy_marker_count = Counter()
	#markers_per_entry = Counter()
	field_count = 0
	
	for i , line in enumerate(sfmlist):			
		line = line.strip()
		lineno = i + 1
		if line:
			field_count += 1
			if space in line:
				marker, data = line.split(space, 1)
				marker_count.update([marker])
				if data:
					marker_count_with_data.update([marker])
				else:
					emtpy_marker_count.update([marker])
					logging.info("Line {} has the {}th  {} marker without data.".format(lineno,emtpy_marker_count[marker],marker))
			else:
				marker = line
				marker_count.update([marker])
				emtpy_marker_count.update([marker])
				print("Line {} has the {}th  {} marker without data.".format(lineno,emtpy_marker_count[marker],marker))

		if marker[0] != slash:
			raise ValueError("\nLine {} doesn't begin with a slash. Line is:\n{}. First character is:\n{}".format(lineno,line,marker[0]))
			
		if marker in new_entry_markers and entry != []:
			sfm.append(entry)
			entry = [[marker,data]]
#			markers_per_entry.update(len(entry))
			
		else :
			entry.append([marker,data])
	
	logging.info("\nCompleting sfm_from_list.")
	logging.info("There are {} entries in the list.\n".format(len(sfm)))
	logging.info("There are {} fields in total in the entries.\n".format(field_count))	
	logging.info("Marker_count is \n{}".format(marker_count))
	logging.info("Marker_count_with_data is \n{}".format(marker_count_with_data))
	logging.info("Empty_marker_count is \n{}".format(emtpy_marker_count))

	return sfm, marker_count, marker_count_with_data, emtpy_marker_count#, markers_per_entry
	
def sfmlist_from_file(filename):
	'''Read in an sfm file, return the file as a list of unicode strings.'''
	
	#logging.info("\nReading sfm file : {}".format(filename))
	non_blank = 0
	blank = 0
	sfmlist = []
	with io.open(filename, readbytes) as infile:	
		for i, linebytes in enumerate(infile):
			try:
				line_str = linebytes.decode('utf-8')
			except UnicodeDecodeError:
				line_str_backslash = linebytes.decode(utf8,'backslashreplace')
				print("Couldn't decode line {} as Unicode. Line is:\n{}".format(i+1,line_str_backslash))
			if line_str.isspace() :
				blank += 1
			else :
				non_blank += 1
				sfmlist.append(line_str)
				
	#logging.info("Completing sfmlist_from_file.")
	#logging.info("There are {} lines in the file.\n".format(blank + non_blank))
	#logging.info("There are {} lines with data and {} blank lines in the file.".format(non_blank,blank))
	return sfmlist

def read_sfm_file(filename):
	'''Read in an sfm file, return the file, the marker counts and the counts of markers with data.'''
	logging.info("\nReading sfm file : {}\n".format(filename))
	fields_in_file = 0
	sfm = []
	entry = []
	is_new_entry = True
	
	with open(filename) as infile:
		lines = infile.readlines()
		
	for i, line in enumerate(lines):
		line = line.strip()
		#lineno = i + 1
		
		if line == empty:
			is_new_entry = True
			logging.info()
			continue
			
		if space in line:
			marker, data = line.split(space, 1)
			fields_in_file += 1
		else:
			marker = line
			data = empty
			fields_in_file += 1
			
		if marker[0] != slash:
			raise ValueError("\nLine {} doesn't begin with a slash. Line is:\n{}. First character is:\n{}".format(lineno,line,marker[0]))

		logging.info("{}		{}".format(marker,data))

		if is_new_entry :
			new_entry_markers.update([marker])
			logging.info("New entry markers are: {}".format(new_entry_markers))
			is_new_entry = False
		
		if is_new_entry and marker:
			new_entry_markers.append(marker)
			is_new_entry = False

		if marker in new_entry_markers and entry != []:
			logging.info("Appended to entry")
			sfm.append(entry)
			entry = [[marker,data]]
		else :
			entry.append([marker,data])
	sfm.append(entry)
	
	#Remove the \sh line if present.
	logging.info("\nFirst entry is \n")
	logging.info(sfm[0])
	logging.info("\nSecond entry is \n")
	logging.info(sfm[1])
	
	firstmarker , data = sfm[0][0]
	if	firstmarker == "\\_sh" :
		logging.info("\nFirst marker is {}.\n Deleting first entry.".format(firstmarker))
		del sfm[0] 
		logging.info("\nFirst entry is {} {}".format(sfm[0][0],sfm[0],[1]))
		logging.info("\nSecond entry is {} {}".format(sfm[1][0],sfm[1],[1]))
	#	exit()
		
	sfm_len =  0
	for entry in sfm:
		sfm_len = sfm_len + len(entry)
	logging.info("There are {} fields in total in {} entries in the file.".format(sfm_len,len(sfm)))
	logging.info("SFM is of type {}.".format(type(sfm)))
	logging.info("There are {} lines with data in the file.\n".format(fields_in_file))
	logging.info("\nLeaving readsfm.")
	
	return sfm#, marker_count, marker_count_with_data		
	
def readsfm(filename):
	'''Read in an sfm file, return the file, the marker counts and the counts of markers with data.'''
	logging.info("\nReading sfm file : {}\n".format(filename))
	fields_in_file = 0
	sfm = []
	entry = []
	
#read as bytes
#	with io.open(filename, readbytes) as infile:
#		for i , line in enumerate(infile):
#			line = line.decode(utf8, 'backslashreplace')
	is_new_entry = True
#read as unicode
	with io.open(filename, read, encoding=utf8) as infile:
		for i , line in enumerate(infile):
			line = line.strip()
			lineno = i + 1
			
			if line == empty:
				is_new_entry = True
				continue
			elif space in line:
				marker, data = line.split(space, 1)
				fields_in_file += 1
			else:
				marker = line
				data = empty
				fields_in_file += 1
				
			if marker[0] != slash:
				raise ValueError("\nLine {} doesn't begin with a slash. Line is:\n{}. First character is:\n{}".format(lineno,line,marker[0]))
			logging.info("{}		{}".format(marker,data))
			if marker in new_entry_markers and entry != []:
				logging.info("Appended to entry")
				sfm.append(entry)
				entry = [[marker,data]]
				is_new_entry = False
			if is_new_entry and marker:
				new_entry_markers.append(marker)
			else :
				entry.append([marker,data])
	sfm.append(entry)
	
	#Remove the \sh line if present.
	logging.info("\nFirst entry is \n")
	logging.info(sfm[0])
	logging.info("\nSecond entry is \n")
	logging.info(sfm[1])
	
	firstmarker , data = sfm[0][0]
	if	firstmarker == "\\_sh" :
		logging.info("\nFirst marker is {}.\n Deleting first entry.".format(firstmarker))
		del sfm[0] 
		logging.info("\nFirst entry is {} {}".format(sfm[0][0],sfm[0],[1]))
		logging.info("\nSecond entry is {} {}".format(sfm[1][0],sfm[1],[1]))
	#	exit()
		
	sfm_len =  0
	for entry in sfm:
		sfm_len = sfm_len + len(entry)
	logging.info("There are {} fields in total in  {} entries in the file.".format(sfm_len,len(sfm)))
	logging.info("SFM list has {} fields.".format(sfm_len))
	logging.info("There are {} lines with data in the file.\n".format(fields_in_file))
	logging.info("Leaving readsfm.")
		
	return sfm#, marker_count, marker_count_with_data

def reorder_entries(sfm,entry_order_dict):
	
	sfm_reordered = []
	#logging.info("Ordering entries according to :\n{}".format(entry_order_dict))
	for i,entry in enumerate(sfm):
		ordered_entry_dict = deepcopy(entry_order_dict)
		#logging.info("o-e-d and e-o-d are:{}\nAND:\n{}".format(ordered_entry_dict,entry_order_dict))
		for field in entry:
			marker,data = field
			ordered_entry_dict[marker] = data
			ordered_entry = []
			for k,v in ordered_entry_dict.items():
				if v:
					ordered_entry.append([k,v])
			#ordered_entry = [[k,v] for k, v in ordered_entry_dict.items() if v is not None]
		
		#logging.info("ordered_entry is {}\n".format(ordered_entry))
		sfm_reordered.append(ordered_entry)
#		if i > 2:
#			exit()
	return sfm_reordered

def writesfm(sfm,mode,filename,order=None):
	'''Given an sfm as a list of lists write it to a file.'''

	logging.info("\n In writesfm. SFM has {} entries.\n".format(len(sfm)))
	
	if order :
		sfm = reorder_entries(sfm,order)
		logging.info("\nFirst entry after reordering is {}".format(sfm[0]))
	lines = []
	for entry in sfm:
		#logging.info("Entry is: {}".format(entry))
		for field in entry:
			#logging.info("Field is: {}".format(field))
			if len(field) != 2 :
				logging.info("\nThis field doesn't contain exactly two items, a marker and data. : {}\n".format(field))
			marker, data = field
			nextline = (marker + space + data).strip()
			if marker in new_entry_markers:
				lines.append(newline)
			lines.append(nextline + newline)
			
	if lines[0] == newline :
		lines = lines[1:]
	with io.open(filename, mode, encoding=utf8) as out:
		out.writelines(lines)
	return

def writesfm_without_empty_markers(sfm,mode,filename):
	'''Given an sfm as a list of lists write it to a file omitting empty markers except empty \ps or \sn markers'''

	#logging.info("Writing out the processed file {}".format(filename))
	lines = []
	for entry in sfm:
		for field in entry:
			marker, data = field
			if len(data) > 0 or marker in ['\\ps', '\\sn','\\se']:
				nextline = (marker + space + data).strip()
			else:
				continue

			if marker in new_entry_markers:
				lines.append(newline)
			lines.append(nextline + newline)
			
	if lines[0] == newline :
		lines = lines[1:]
	with io.open(filename, mode, encoding=utf8) as out:
		out.writelines(lines)
	return
	
def marker_definitions(filename,mode=read,markers=None):
	'''Read or write to a csv file containing the names of each marker and it's language and script'''
	
	if markers and mode == write:
		headers = dict(['Marker','Field Name','Language','Script','Dialect','Field location'])
		with open(filename,mode,encoding=utf8) as out:
		
			f = csv.DictWriter(out,markers)
			f.writeheader()
	return
	
def sanitised_input(prompt, type_=None, min_=None, max_=None, range_=None):
	if min_ is not None and max_ is not None and max_ < min_:
		raise ValueError("min_ must be less than or equal to max_.")
	while True:
		ui = input(prompt)
		if type_ is not None:
			try:
				ui = type_(ui)
			except ValueError:
				print("Input type must be {0}.".format(type_.__name__))
				continue
		if max_ is not None and ui > max_:
			print("Input must be less than or equal to {0}.".format(max_))
		elif min_ is not None and ui < min_:
			print("Input must be greater than or equal to {0}.".format(min_))
		elif range_ is not None and ui not in range_:
			if isinstance(range_, range):
				template = "Input must be between {0.start} and {0.stop}."
				print(template.format(range_))
			else:
				template = "Input must be {0}."
				if len(range_) == 1:
					print(template.format(*range_))
				else:
					print(template.format(" or ".join((", ".join(map(str, range_[:-1])),str(range_[-1])))))
		else:
			return ui


#With usage such as:
#age = sanitised_input_input("Enter your age: ", int, 1, 101)
#answer = sanitised_input("Enter your answer", str.lower, range_=('a', 'b', 'c', 'd'))

def get_replacement_markers(markers):

	find_marker = sanitised_input("Which marker would you like to modify? Type the number of the marker.", int, 1, len(markers))
	find = markers[find_marker - 1]

	replacement_marker = sanitised_input("Which marker would you like to change {} to? Type the number of the marker or 0 for another option.".format(find), int, 0, len(markers))
	if replacement_marker == 0 :
		replacement_marker = sanitised_input("Type the new marker without the backslash.>", str)
		replace = slash + replacement_marker
	else:
		replace = markers[replacement_marker - 1]
	
	return find,replace

def do_replace_marker(sfm,find,replace):
#Replace one marker with another.

	logging.info("\nIn replace_marker code:\n")
	new_sfm = sfm
	count = 0
	
	for i,entry in enumerate(new_sfm):
		for j , field in enumerate(entry):
			marker, data = field
			if marker == find :
				count = count + 1
				new_sfm[i][j][0] = replace
	logging.info("\nLeaving replace_marker.\n")
	return new_sfm, count

def duplicate_marker(sfm,find_marker,dup_marker):
#Duplicate one marker with another.
	new_sfm = []
	count = 0
	#logging.info("\nIn duplicate_marker code:\n")
	
	for entry in sfm:
		new_entry = []
		for field in entry:
			marker, data = field
			new_entry.append([marker,data])
			if marker == find_marker :
				count = count + 1
				new_entry.append([dup_marker,data])
				
		new_sfm.append(new_entry)		
	
	return new_sfm, count
	
def do_split_marker_by_script(sfm,find_marker,script1,script2,new_marker1,new_marker2):
#Find a given marker and split it by script.

	ad = AlphabetDetector()
	new_sfm = sfm
	count = 0
	logging.info("\nIn do_split_marker_by_script code:\n")
	
	for i,entry in enumerate(new_sfm):
		for j , field in enumerate(entry):
			marker, data = field
			if marker == find_marker :
				count = count + 1
				scripts = ad.detect_alphabet(data)
				script_count = len(scripts)
				
				if script_count == 1:
					script = next(iter(scripts))
					new_field = [marker + '_' + script,data]
					new_sfm[i].insert(j+1,new_field)
					#logging.info("\nFound '{}' only containing {}. Adding new field: {}".format(data,script,new_field))
					#logging.info(new_sfm[i])
					
				elif script_count > 1:
					print("\nFound {} scripts: {}".format(len(scripts),scripts))
					print("Data is {}".format(data))
					for script_number,script in enumerate(scripts):
						string_list = [character for character in data if character == space or script in ad.detect_alphabet(character)]
						string = ''.join(string_list).strip()
						new_field = [marker + '_' + script,string]
						print("New_field is {}".format(new_field))
						new_sfm[i].insert(j+script_number+1,new_field)
					print(new_sfm[i])
	return new_sfm, count

def do_replace_marker2(sfm,find,replace):
#Replace one marker with another.
	#logging.info("\nIn replace_marker2 code:\n")
	sfm[:] = [[[replace,data] if marker == find else [marker,data] for marker,data in entry] for entry in sfm]
		
	#logging.info("\nLeaving replace_marker2 code:\n")
	return sfm

def replace_data(sfm, in_marker,find,replace):
#Replace data in a given marker with other data.
	print("Finding {} to replace with {} in field {}.".format(find,replace,in_marker))
	replacement_count = 0
	for i, entry in enumerate(sfm):
		for j, field in enumerate(entry):
			marker , data = field
			if marker == in_marker and data == find:
				#logging.info("Found data match.")
				sfm[i][j][1] = replace
				replacement_count += 1
	return sfm, replacement_count

def depth(lst):
    depths = []
    for item in lst:
        if isinstance(item, list):
            depths.append(depth(item))
    if len(depths) > 0:
        return 1 + max(depths)
    return 1

def count_markers(sfm):
	marker_count = Counter()
	marker_count_with_data = Counter()
	markers_per_entry = Counter()
	
	#logging.info("sfm has depth = {}".format(depth(sfm)))
	#logging.info("sfm has type = {}".format(type(sfm)))
	for entry in sfm:
		#logging.info("Entry has {} fields. {}	".format(len(entry),entry))
		#markers_per_entry.update(len(entry))
		
		for field in entry:
			if len(field) == 2:
				#logging.info("Field has {} parts. {}".format(len(field),field))
				marker , data = field
				marker_count.update([marker])
				marker_count_with_data.update([marker])
			elif len(field) == 1:
				logging.info("Field has {} parts. {}".format(len(field),field))
				marker = field
				#logging.info("Marker is {},length is {}".format(field,len(field)))
				marker_count.update([field])
	return marker_count, marker_count_with_data

def fits_in_simple_mdf(entry):
	''' Function to check whether a given entry contains only one of each field in the MDF spec.'''

	marker_count = Counter()
	for field in entry:
#		logging.info("marker_count is {}".format(marker_count))
#		logging.info("Field[0] is {}".format(field[0]))
		marker_count.update([field[0]])
		if marker_count[field[0]] > 1:
#			logging.info("Marker {} occurs more than once, - Doesn't fit.".format(field[0]))
			return False
		
#	print("Final Marker_count is {}. No markers occur twice = Fits.".format(marker_count))
	return True


def markers_not_fit(entry):
	''' Function to count the markers in a given entry that make it fail to fit in the simple_mdf format.'''

	marker_count = Counter()
	for field in entry:
		marker_count.update([field[0]])
	return marker_count


def check_markers(sfm,known_markers):

	unknown_markers = []
	seen_markers = []
	for entry in sfm:
		for field in entry:
			marker, data = field
			if marker in seen_markers:
				continue
			elif marker in known_markers:
				seen_markers.append(marker)
				continue
			elif marker not in unknown_markers:
				seen_markers.append(marker)
				unknown_markers.append(marker)
			else :
				raise ValueError("Logic error perhaps! Marker is {}\nSeen_markers are:\n{}\nUnknown markers are:\n{}".format(marker,seen_markers,unknown_markers))
	
	if seen_markers:
		print("These expected markers were seen in the file:\n{}".format(seen_markers))
		
	if not unknown_markers: 
		print("There were no unexpected markers seen in the file:")
	else :
		print("These unexpected markers were seen in the file:\n{}".format(unknown_markers))

	return seen_markers, unknown_markers

def split(sfm):
	''' function to return two lists. one of all the entries that fit in as simple mdf and a list of all the entries that don't.'''
	
	fit = []
	dont_fit = []
	for i, entry in enumerate(sfm):
		if fits_in_simple_mdf(entry):
			fit.append(entry)
		else :
			dont_fit.append(entry)
#		if i > 2 :
#			exit()
	return fit, dont_fit
	

def find_list_data(sfm,markers):
	#The sfm file is a list of entries, each containing a list of fields.
	#Look at the data from all fields looking for repeated data. 
	#Repeated data may indicate that it is a 'Range field' (Toolbox) or a 'List Field' (FLEx)

	#logging.info("In find_list_data. SFM type is {}".format(type(sfm)))
	markers.sort()

	#Create a dictionary with each marker as a key and a Counter() as the value.
	possible_list_data_dict = dict()

	for marker in markers:
		possible_list_data_dict[marker] = Counter()

	for entry in sfm:
		#logging.info("Entry is: {}".format(entry))
		for field in entry:
			marker,data = field
			possible_list_data_dict[marker].update([data])

	return possible_list_data_dict

def determine_file_type(filein):
	
	filename, file_extension = os.path.splitext(filein)
	if file_extension.lower() in sfm_exts:
		return sfm_ext		
	elif file_extension.lower() in csv_exts:
		return csv_ext
	elif file_extension.lower() in typ_exts:
		return typ_ext	
	else :
		choice = empty
		while choice not in ['s', 'c', 't', 'q']:
			choice = sanitised_input("The file extension {} isn't recognised. Should it be treated as an SFM, CSV or TYP file? Type s, c, or t to indicate the file type or q to quit.>".format(file_extension), str, range_=('sfm', 's', 'csv', 'c', 'typ', 't', 'q', 'quit'))
			choice = choice.lower()[0]
			logging.info("Choice is {}".format(choice))
			
		if choice is 's':
			return '.sfm'
		elif choice is 'c': 
			return '.csv'
		elif choice is 't': 
			return '.typ'
		elif choice is 'q':
			quit()
		
	print("Could not determine the filetype of file {}".format(filein))
	return None
		

def process_input_file(filein):
	filetype = determine_file_type(filein)
	
	if filetype == sfm_ext :
		#sfm = read_sfm_file(filein)
		#return sfm, marker_count, marker_count_with_data, emtpy_marker_count		
		return sfm_from_list(sfmlist_from_file(filein))
		
	elif filetype == csv_ext :
		sfm , markers, no_slash_cells = readcsv(filein)
		logging.info("In process_input_file sfm is of type {}".format(type(sfm)))
		
		if no_slash_cells :
			print("\nSome cells do not contain slashes so it isn't clear whether they contain a marker.")
			choice = sanitised_input("Would you like information about those cells written to a file? y/n \n", str)
			if choice.lower()[0] == 'y':
				out_file = filesavebox(title="File name for information about the cells without markers.")
			with io.open(out_file, 'w', encoding = utf8) as out:
				out.write("There are cells that don't contain a backslash marker.\n")
				out.write("They are shown below, with the preceeding cell and the row and column.\n")
				out.write("{0:>5} {1:<5}  {2:}***{3:}\n".format('Row','Column','Preceeding cell', 'Slashless cell'))
				for item in no_slash_cells:
					out.write("{0:>5} {1:<5}  {2:}***{3:}\n".format(item.row,item.column,item.previous_cell,item.contents))
					print("Cell {}:{} contains: '{}'.".format(item.row,item.column, item.contents))
					
		#Note that filetype might not be set and the data is returned as a nested list (sfm not csv).
		
		return sfm, None, None, None
		
	# elif filetype == typ_ext:
		# logging.info("Extension is {}".format(filetype))
		# typ, groups =  read_typ_file(filein)
		# return typ, groups
	else :
		raise ValueError("Didn't know what to do with file {} of type {} in process_input_file.".format(filein,filetype))
	return
	
def process_replacements_from_file(sfm,marker,changefile):

	total_replacements = 0
	
	with open(changefile, 'r', encoding="utf8") as infile:
		datareader = csv.reader(infile, dialect='default')
		replacements = [line for line in datareader]
		
	for find,replace in replacements:
		sfm, replacement_count = replace_data(sfm,marker,find,replace)
		total_replacements = total_replacements + replacement_count
	
	return sfm,total_replacements

	
def split_file(sfm,easy_file,hard_file,order_dict=None):
	''' Write out the entries that should be simple to import to one file, optionally reordered and the others to another.'''

	simple_mdf , not_simple_mdf = split(sfm)

	if not_simple_mdf :
		writesfm(not_simple_mdf,overwrite,hard_file)
		
	if simple_mdf :
		writesfm(simple_mdf,overwrite,easy_file,order=order_dict)
	
	return simple_mdf, not_simple_mdf
	
def get_field():
	while field_chosen not in markers:
		field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
	return field_chosen
	
def split_file_info(simple_mdf,not_simple_mdf):	
	''' Return info about the split files. '''
	single_field_counter = Counter()
	double_field_counter = Counter()
	
	for i, entry in enumerate(not_simple_mdf):
		markers_in_entry  =  markers_not_fit(entry)
		lexeme = entry[0][1]
		not_fitting = [(k,v) for k,v in markers_in_entry.items() if v > 1]
#		logging.info("Marker counts for entry {} are:\n{}\n".format(lexeme, markers_in_entry))
#		logging.info("Markers not fitting: {}\n".format(not_fitting))

		if len(not_fitting) == 1:
			single_field_counter.update(not_fitting)
	
		if len(not_fitting) == 2:
			marker1 = not_fitting[0][0].strip(slash)
			marker2 = not_fitting[1][0].strip(slash)
			
			logging.info([marker1 + space + marker2])
			double_field_counter.update([marker1 + space + marker2])
	
	print("A total of {} entries don't fit due to multiples of one field.".format(sum(single_field_counter.values())))
	print("A total of {} entries don't fit due to multiples of two fields.".format(sum(double_field_counter.values())))
	logging.info("Leaving split_file_info")
	return None	


def show_main_menu(sfm):
	while True:
		#logging.info("main_menu is {} and it's type is {}".format(main_menu,type(main_menu)))
		possible_list_data_dict = get_sfm_info(sfm,markers)
		
		menu = main_menu()
		choice = show_menu(*menu)

		if choice == '1':
			print(marker_count)
			printmarkers(marker_count, marker_count_with_data)
			print()
			for marker in mdf_order:
				if marker_count[marker]:
					print(marker, marker_count[marker])
				else:
					print(marker, marker_count[marker])
					
			input("Press enter to return to the menu")
		
		if choice == '2':
			for i, marker in enumerate(markers):
				print("{0:>3d} : {1:s}".format(i+1,marker))
			
			find, replace = get_replacement_markers(markers)
			
			input("Finding marker {} and replacing it with marker {}\nPress enter to continue.".format(find,replace))
			sfm , count = do_replace_marker(sfm[:],find,replace)
			input("\nMade {} replacements\n\nPress enter to continue.".format(count))
			
		if choice == '3':
			marker = None
			print("First {} entries of new SFM are {}".format(3,sfm[0:3]))
			marker = choicebox('Choose the field you want to duplicate.', 'Field Markers',[' '+x+' ' for x in markers]).strip()

			print("Marker chosen is {}".format(marker))
			print(markers)
			while marker not in markers:
				marker = input("Type in the field whose data you want to duplicate. Or hit enter to go back.")
				if not marker:
					break
			
			dup_marker = sanitised_input("What marker would you like to use for the duplicate field?", str)
			if dup_marker[0] != slash :
				dup_marker = slash + dup_marker
			
			choice = sanitised_input("Duplicating field {} to field {}. Proceed? y/n ".format(marker,dup_marker), str)
			if choice.lower()[0] == 'y':
				sfm, replacement_count = duplicate_marker(sfm,marker,dup_marker)
				print("Made {} replacements".format(replacement_count))
				print("First {} entries of new SFM are {}".format(3,sfm[0:3]))
				
		if choice == '4':
			marker = None
			#marker = choicebox('Choose field whose data you want to change.', 'Field Markers', [' '+x+' ' for x in markers])
			while marker not in markers:
				marker = input("Type in the field whose data you want to change. Or hit enter to go back.")
				if not marker:
					break
			choice = sanitised_input("How would you like specify the changes to make? By file (csv) or typed in?", str, range_=('file','f','typed','t'))
			if choice.lower()[0] == 'f':
				changefile = fileopenbox(title="Choose csv file containing changes.",msg='Choose csv file.',filetypes=['*.csv'])
				if changefile:
					sfm, total_replacements = process_replacements_from_file(sfm,marker,changefile)
					print("Made {} replacements".format(total_replacements))
			elif choice.lower()[0] == 't':
			
				find = sanitised_input("What data would you like to find in field {}? >".format(marker), str)
				replace = sanitised_input("What would you like to replace {} with? >".format(find), str)
				sfm, replacement_count = replace_data(sfm,marker,find,replace)
				print("Made {} replacements".format(replacement_count))
				
				
		if choice == '5':
			out_file = filesavebox(title="Save processed file as:")
			writesfm(sfm,overwrite,out_file)
			input("Processed SFM file written to {}\n\nPress enter to continue.".format(out_file))
		
		if choice == '6':
			info_file = filesavebox(title="Save processed file as:")
			print("Writing data to file {}.".format(info_file))
			possible_list_data_dict = find_list_data(sfm,markers)
			
			# new_counter_dict = dict()
			# for i,entry in enumerate(counter_dict.items()):
				# marker,c = entry
				# new_counter_dict[marker] = c.most_common(10)
			
			# print("First few entries in dict are:\n")
			# for i,entry in enumerate(new_counter_dict.items()):
				# print(i,entry)
				# if i > 5:
					# break

			#writemarkers(marker_count, marker_count_with_data,markersfile,overwrite)
			#printmarkers(marker_count, marker_count_with_data)
			#output_markers(marker_count, marker_count_with_data)
			output_markers(marker_count, marker_count_with_data,emtpy_marker_count,info_file,overwrite)
			#output_counter(marker_count_with_data,"The most used markers are:")
			
		if choice == '7':
			limit = 6
			print("\nLooking for common data in each field.")
			print("Data repeated more than {} times is shown with a count of the occurances, under the field marker.".format(limit))
			possible_list_data_dict = find_list_data(sfm,markers)
			#print(counter_dict)
			#exit()
			info_file = filesavebox(title="Save info as:")
		   
			for marker in markers:
			#	output_counter(counter_dict[marker],"  Marker: {}".format(marker),limit,filename=info_file,mode=append)
			#	if marker in list_markers:
				output_counter(counter_dict[marker],"  Marker: {}".format(marker),limit,filename=info_file,mode=append)

			#for marker in markers:
			#	if marker not in list_markers:
			#		output_counter(counter_dict[marker],"  Marker: {}".format(marker),limit,filename=info_file,mode=append)
		
		if choice == '8':
			out_file = filesavebox(title="Save processed file as:")
			writesfm_without_empty_markers(sfm,overwrite,out_file)
			input("Processed SFM file written to {}\n\nPress enter to continue.".format(out_file))
			
		if choice == '9':
			field_chosen = None
			field_chosen = choicebox('Choose field whose data you want to change.', 'Field Markers', [' '+x+' ' for x in markers])
			print("{} is the chosen field.\n".format(field_chosen))
			#while field_chosen not in markers:
			#	field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
			if not field_chosen:
				break
			possible_list_data_dict = find_list_data(sfm,markers)
			for item,count in counter_dict[field_chosen].items():
				print(item,"\t\t",count)
				
		if choice == '10':
			easy_file = filesavebox(title="Save the Simple-to-import file as:")
			hard_file = filesavebox(title="Save the Difficult-to-import file as:")
			simple_mdf,not_simple_mdf = split_file(sfm,easy_file,hard_file)
			print("There are {} simple entries.".format(len(simple_mdf)))
			print("There are {} not so simple entries.".format(len(not_simple_mdf)))
	
		if choice =='11':
			field_chosen = None
			while field_chosen not in markers:
				#field_chosen = choicebox('Choose field whose data you want to split.', 'Field Markers', [' '+x+' ' for x in markers])
				field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
				if not field_chosen:
					break
			print("Marker {} occurs {} times in the data.".format(field_chosen,marker_count[field_chosen]))
			sfm, count = do_split_marker_by_script(sfm,field_chosen,"LATIN","ARABIC","\\ar_la","\\ar_ar")
			print("{} entries modified.".format(count))
	

		if choice =='12':
			
			sort_order = sanitised_input("How would you like to sort the entries:\n1) Alphabetically A to Z \n2) Alphabetically Z to A \n3) By number of fields, longest first\n4) By number of fields, shortest first\n\n0) To return to main menu", int, 0,4)
			
			if sort_order == 0:
				break
			elif sort_order == 1:
				sfm = sort_sfm(sfm, 'lexeme', False)
			elif sort_order == 2:
				sfm = sort_sfm(sfm, 'lexeme', True)
			elif sort_order == 3:
				sfm = sort_sfm(sfm, 'shortest_first', True)
			elif sort_order == 4:
				sfm = sort_sfm(sfm, 'shortest_first', False)
			
		if choice =='13':
		
			number = sanitised_input("There are {} entries, how many would you to show? ".format(len(sfm)), int)
			print_sfm(sfm,number)
		
		if choice == '14':
			typ = read_typ_file(args.input)
			
		if choice == '15':
			#sfm = sfmlist_from_file(args.input)
			crossrefs = []
			xref_markers = ['\va','\sy','\se','\mn','\lv','\cf','\an']
			lexemes = [entry[0][1] for entry in sfm]
			for entry in sfm:
				lexeme = None
				xrefs = None
				for field in entry:
					marker,data = field
					if marker in new_entry_markers:
						lexeme = data
					if marker in xref_markers:
						xref_marker = marker
						xref = data
						exists = xref in lexemes
						crossrefs.append(XRef(lexeme,xref_marker,xref, exists))
						
		if choice == '16':
			for entry in sfm:
				entry.append([new_marker,files_and_values[file.name]])

			#print("Entries are {}".format(entries))
			xrefs_exist	= [xref for xref in crossrefs if xref.exists]
			xrefs_missing = [xref for xref in crossrefs if not xref.exists]
			
			print("\nThe following cross references refer to existing entries.\n")
			for xref in xrefs_exist:
				print("Lexeme {} has marker: {} which refers to : {}".format(xref.lexeme,xref.xref_marker,xref.xref))
			print("\nThe following cross references do not have matching entries.\n")
			for xref in xrefs_missing:
				print("Lexeme {} has marker: {} which refers to : {}".format(xref.lexeme,xref.xref_marker,xref.xref))
			
	return sfm, out_file, summary_file


if __name__ == "__main__":
	""" Run as a stand-alone script """
	
	args = parser.parse_args()
	
	if not args.input:
		args.input = fileopenbox(title="Choose a file to process.", filetypes=filemasks)

	sfm , marker_count, marker_count_with_data, emtpy_marker_count = process_input_file(args.input)
	
	print("The sfm file has {} entries\n".format(len(sfm)))
	
	if not args.output:
		args.output = filesavebox("Where would you like to save the processed SFM file?")

	if (args.output) :
		writesfm(sfm,overwrite,args.output)
	
	#("In __main__. sfm has type = {}".format(type(sfm)))
	possible_list_data_dict = find_list_data(sfm,markers)
	#seen_markers, unknown_markers = check_markers(sfm,mdf_order)

	if not args.report:
		args.report = filesavebox("Where would you like to save a report about the data?")
	
	if (args.report) :
		output_markers(marker_count, marker_count_with_data,emtpy_marker_count,args.report,overwrite)
		writemarkers(marker_count, marker_count_with_data,emtpy_marker_count,args.report,append)
		for marker in markers:
			output_counter(counter_dict[marker],"  Marker: {}".format(marker),limit=8,filename=args.report,mode=append)
		
	show_main_menu(sfm)
				
	# def remove_subsets(lists):
		# return [x for x in lists if not any(set(x)<=set(y) for y in lists if x is not y)]
		
	# #if (args.output):
	# #get all the words.
	# words = get_lexemes(sfm)

	# #remove any duplicates (homographs) and slice the list here for testing.
	# words = sorted(set(words))[0:1000]

	# #Create an empty list to store the lists of similar words.
	# all_similar = []
	# while words:
		# word = words.pop()
		# similar_words = difflib.get_close_matches(word,words,n=15,cutoff=0.90)
		# if similar_words:
			
			# all_similar.append([word ,similar_words])
		# for similar in similar_words:
			# words.remove(similar)

	#for word, matches in sorted(all_similar):
	#	print("{:>15}	{}".format(word,matches))

	#deduped = remove_subsets(all_similar)
		# print("Deduped are: {}".format(deduped))
		# with open(args.output, append, encoding=utf8) as out :
			# out.write("\nSimilar words to compare are :\n")
			# for similar in deduped:
				# out.write(str(similar) + newline)

	# #Now process the list again, to reduce the number of lists.
	# words = [item for sublist in deduped for item in sublist]

	# # with open(args.output, append, encoding=utf8) as out :
		# # out.write("\nAll Similar words to compare again are :\n")
		# # out.write(str(words) + newline)

	# all_similar = []
	# for word in words:
		# similar_words = difflib.get_close_matches(word,words,n=100,cutoff=0.80)
		# if len(similar_words) > 1:
			# all_similar.append(similar_words)

	# # with open(args.output, append, encoding=utf8) as out :
		# # out.write("\nReduced lists are :\n")
		# # for similar in all_similar:
			# # out.write(str(similar) + newline)

	# deduped = remove_subsets(all_similar)

	# print("Deduped are :\n")
	# for words in deduped:
		# print(words)
		# words.sort()

	# print("Deduped sorted are :\n")
	# for new_words in deduped:
		# print(new_words)
		
	# deduped = sorted(deduped, key = lambda x:x[0])
	# print("Deduped are: {}".format(deduped))
	# with open(args.output, overwrite, encoding=utf8) as out :
		# out.write("\nSimilar words to compare are :\n")
		# for similar in deduped:
			# out.write(str(similar) + newline)

#def to_be_converted_to_function():
# if args.do_regex :
	# print("Doing Regex.")
	# # List of replacements to do.
	# # my_regex = re.compile('(\\\\.?),',"\r\n\1")
	# # my_regex = re.compile('b',"a")
	# lines = []
	# with io.open(args.input, 'r', encoding=utf8) as in_file:
		# with io.open(args.output, 'w', encoding=utf8) as out_file:
			# for line in in_file:
				# line = re.sub('\,\\\\','\n\\\\', line) # Replace every comma that preceeds a backslash with a newline.
				# out_file.writelines(line + '\r\n')	
	# lines_out = []
	# with io.open(args.output, 'r', encoding=utf8) as in_file:
		# for line in in_file:
			# # line = rtrim(line,' ,')
			# line = line.rstrip(",")	# Remove all the line final commas 
			# line = line.rstrip()		# Remove all the line final whitespace.
		# # line = re.sub('\,+\\r',empty,line)	   # Delete all the line-final commas
		# # line = re.sub(' +\\r',empty,line)	   # Delete all the line-final spaces
			# line = re.sub('\\\\lx ','\\n\\\\lx ',line)	# Put a newline before each entry.
			# lines_out.append(line)
		
	# with io.open(args.output, 'w', encoding=utf8) as out_file:
		# out_file.writelines(lines_out)
		
	#return
