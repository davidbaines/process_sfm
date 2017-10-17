#! /usr/bin/python3

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
from collections import Counter as Counter
from collections import OrderedDict as OrderedDict
from collections import namedtuple
from copy import deepcopy
import difflib 
from process_sfm_menu import show_menu, main_menu
from easygui import fileopenbox, filesavebox, buttonbox, choicebox, diropenbox
from alphabet_detector import AlphabetDetector

#print("main_menu is {} and it's type is {}".format(main_menu,type(main_menu)))
#def fileopenbox(msg=None, title=None, default='*', filetypes=None, multiple=False)

csv.register_dialect('default')

parser = argparse.ArgumentParser(description="Find irregularities in SFM files and convert between sfm and csv")
parser.add_argument("-in", "--input",   help="Specify file to read in.")
parser.add_argument("-out" ,"--output", help="Specify the output filename")
#parser.add_argument( dest='feature', default=False, action='store_true')
#parser.add_argument("-dore", "--do_regex", default=False, action="store_true", help="Process the re and save file as output only.")

#print("\n\n****************************\n")
#print(args)

slash = '\\'
space = ' '
newline = '\n'
empty = ''
comma = ','
new_entry_marker = '\\lx'

Field = namedtuple("Field", ['marker','type','data','ws'])

utf8='utf-8'
overwrite = 'w'
append = 'a'
read = 'r'
readbytes = 'rb'
csv_ext = '.csv'
sfm_ext = '.sfm'
csvfileexts = ['.csv']
sfmfileexts = ['.db', '.lex', '.mdf']
filemasks = ["*.csv","*.db","*.lex","*.mdf"]

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
specific_list_markers = ['\\cat','\\wjk','\\ed','\\class','\\bw-s']

list_markers = ['\\ps','\\lf', '\\so', '\\pdl','\\bw' ]
list_markers.append(specific_list_markers)

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
	
	if filename == '' and lines :
		print(title)
		print(column_heading)
		for line in lines:
			print(line)
		
	elif lines :
		with io.open(filename,mode,encoding=utf8) as out:
			out.write(title + newline)
			out.write(column_heading + newline)
			for line in lines:
				out.write(line + newline)
			out.write(newline)
			
	return None


def writemarkers(marker_count,marker_count_with_data,filename,write_mode=append):
	'''Write to a given file information about the frequency of markers and markers with data.'''

	with io.open(filename,write_mode,encoding=utf8) as out:
		out.write("{0:<8s}{1:>10s}{2:>8s}{3:>10s}\n".format('Marker','With data','Empty','Total'))
		for m, count in marker_count.most_common():
			out.write("{0:<8s}{1:>10d}{2:>8d}{3:>10d}\n".format(m,marker_count_with_data[m],count - marker_count_with_data[m],count))
		out.write(newline)


def printmarkers(marker_count,marker_count_with_data):
	title = "{0:<8s}{1:>10s}{2:>8s}{3:>10s}\n".format('Marker','With data','Empty','Total')
	lines = []
	for m, count in marker_count.most_common():
		lines.append(["{0:<8s}{1:>10d}{2:>8d}{3:>10d}".format(m,marker_count_with_data[m],count - marker_count_with_data[m],count)])

	print(title)
	for line in lines:
		print(line[0])
	print()


def print_sfm(sfm):
	for entry in sfm:
		for field in entry:
			marker , data = field
			print(marker,data)


def output_markers(marker_count,m_with_data,filename = '',write_mode=append):
	title = "{0:<8s}{1:>10s}{2:>8s}{3:>10s}".format('Marker','With data','Empty','Total')
	lines = []
	for m, count in marker_count.most_common():
		lines.append(["{0:<8s}{1:>10d}{2:>8d}{3:>10d}".format(m,m_with_data[m],count - m_with_data[m],count)])
	
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

			
def sfm_from_list(sfmlist):
	sfm = []
	entry = []
	
	for i , line in enumerate(sfmlist):			
		line = line.strip()
		lineno = i + 1
		if line == empty:
			continue
		elif space in line:
			marker, data = line.split(space, 1)
		else:
			marker = line
			data = empty

		if marker[0] != slash:
			raise ValueError("\nLine {} doesn't begin with a slash. Line is:\n{}. First character is:\n{}".format(lineno,line,marker[0]))
			
		if marker == new_entry_marker and entry != []:
			sfm.append(entry)
			entry = [[marker,data]]
		else :
			entry.append([marker,data])

	sfm_len =  0
	for entry in sfm:
		sfm_len = sfm_len + len(entry)
	
	#print("\nCompleting sfm_from_list.")
	#print("There are {} entries in the list.\n".format(len(sfm)))
	#print("There are {} fields in total in the entries.\n".format(sfm_len))
	return sfm#, marker_count, marker_count_with_data		


def sfmlist_from_file(filename):
	'''Read in an sfm file, return the file as a list of unicode strings.'''
	
	#print("\nReading sfm file : {}".format(filename))
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
				
	#print("Completing sfmlist_from_file.")
	#print("There are {} lines in the file.\n".format(blank + non_blank))
	#print("There are {} lines with data and {} blank lines in the file.".format(non_blank,blank))
	return sfmlist


def readsfm(filename):
	'''Read in an sfm file, return the file, the marker counts and the counts of markers with data.'''
	print("\nReading sfm file : {}\n".format(filename))
	fields_in_file = 0
	sfm = []
	entry = []
#read as bytes
#	with io.open(filename, readbytes) as infile:
#		for i , line in enumerate(infile):
#			line = line.decode(utf8, 'backslashreplace')
#read as unicode
	with io.open(filename, read, encoding=utf8) as infile:
		for i , line in enumerate(infile):
			line = line.strip()
			lineno = i + 1
			if line == empty:
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
				
			if marker == new_entry_marker and entry != []:
				sfm.append(entry)
				entry = [[marker,data]]
			else :
				entry.append([marker,data])
	sfm.append(entry)
	
	#Remove the \sh line if present.
	print("\nFirst entry is {} {}".format(sfm[0][0],sfm[0],[1]))
	print("\nSecond entry is {} {}".format(sfm[1][0],sfm[1],[1]))
	
	firstmarker , data = sfm[0][0]
	if	firstmarker == "\\_sh" :
		print("\nFirst marker is {}.\n Deleting first entry.".format(firstmarker))
		del sfm[0] 
		print("\nFirst entry is {} {}".format(sfm[0][0],sfm[0],[1]))
		print("\nSecond entry is {} {}".format(sfm[1][0],sfm[1],[1]))
	#	exit()
		
	sfm_len =  0
	for entry in sfm:
		sfm_len = sfm_len + len(entry)
	print("\nCompleting readsfm.")
	print("There are {} fields in total in  {} entries in the file.".format(sfm_len,len(sfm)))
	print("SFM list has {} fields.".format(sfm_len))
	print("There are {} lines with data in the file.\n".format(fields_in_file))
	
	
	
	return sfm#, marker_count, marker_count_with_data		


def readcsv(filename):

	#print("Reading csv file : {}".format(filename))
	sfm = []

	No_slash_info = namedtuple('No_slash_info',['row','column','contents','previous_cell'])
	No_slash_cells = []
	
	with open(filename, 'r', encoding="utf8") as infile:
		datareader = csv.reader(infile, dialect='default')
		firstline = next(datareader)
		
		for i,row in enumerate(datareader):
			entry = []
			previous_cell = empty
			#firstdata = row[0].split(space,1)[1]
			#print(firstdata)	
			for j,cell in enumerate(row):
				if cell == empty :
					previous_cell = empty
					continue
				elif not cell[0] == slash :
					No_slash_cells.append(No_slash_info(i+2,num_to_column(j+1), cell,previous_cell))
					#raise ValueError("Cell in Row {}, Column {} doesn't contain a slash. Contents are :{}".format(i+2,num_to_column(j+1), cell))
					previous_cell = cell
					continue
				if space in cell:
					#Separate the marker from the data.
					marker , data = cell.split(space,1)
					if len(data) == 0 :
						print("This marker {} has no data {}".format(marker,data))
						entry.append([marker,data])
					previous_cell = cell
			sfm.append(entry)
			
	return sfm , No_slash_cells


def reorder_entries(sfm,entry_order_dict):
	
	sfm_reordered = []
	#print("Ordering entries according to :\n{}".format(entry_order_dict))
	for i,entry in enumerate(sfm):
		ordered_entry_dict = deepcopy(entry_order_dict)
		#print("o-e-d and e-o-d are:{}\nAND:\n{}".format(ordered_entry_dict,entry_order_dict))
		for field in entry:
			marker,data = field
			ordered_entry_dict[marker] = data
			ordered_entry = []
			for k,v in ordered_entry_dict.items():
				if v:
					ordered_entry.append([k,v])
			#ordered_entry = [[k,v] for k, v in ordered_entry_dict.items() if v is not None]
		
		#print("ordered_entry is {}\n".format(ordered_entry))
		sfm_reordered.append(ordered_entry)
#		if i > 2:
#			exit()
	return sfm_reordered


def writesfm(sfm,mode,filename,order=None):
	'''Given an sfm as a list of lists write it to a file.'''

	if order :
		sfm = reorder_entries(sfm,order)
		print("\nFirst entry after reordering is {}".format(sfm[0]))
		#exit()
	lines = []
	for entry in sfm:
		for field in entry:
			if len(field) != 2 :
				print("\nThe field is: {}\n".format(field))
			marker, data = field
			nextline = (marker + space + data).strip()
			if marker == new_entry_marker:
				lines.append(newline)
			lines.append(nextline + newline)
			
	if lines[0] == newline :
		lines = lines[1:]
	with io.open(filename, mode, encoding=utf8) as out:
		out.writelines(lines)


def writesfm_without_empty_markers(sfm,mode,filename):
	'''Given an sfm as a list of lists write it to a file omitting empty markers except empty \ps or \sn markers'''

	#print("Writing out the processed file {}".format(filename))
	lines = []
	for entry in sfm:
		for field in entry:
			marker, data = field
			if len(data) > 0 or marker in ['\\ps', '\\sn','\\se']:
				nextline = (marker + space + data).strip()
			else:
				continue
			if marker == new_entry_marker:
				lines.append(newline)
			lines.append(nextline + newline)
			
	if lines[0] == newline :
		lines = lines[1:]
	with io.open(filename, mode, encoding=utf8) as out:
		out.writelines(lines)
		

def writecsv(sfm, mode, filename):
# ''' Write an sfm to a csv file'''
	lines = []
	for i,entry in enumerate(sfm):
		line = empty
		for field in entry:
			marker, data = field
			if line == empty :
				line = marker + space + data
			else :
				line = line + comma + marker + space + data
			if i < 10 : print(line)
		
		lines.append(line + newline)
				
	with io.open(filename, mode, encoding=utf8) as out:
		out.writelines(lines)

	
def marker_definitions(filename,mode=read,markers=None):
	'''Read or write to a csv file containing the names of each marker and it's language and script'''
	
	if markers and mode != read:
		headers = dict(['Marker','Field Name','Language','Script','Dialect','Field location'])
		with open(filename,mode,encoding=utf8) as out:
		
			f = csv.DictWriter(out,markers)
			f.writeheader()
			

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
	new_sfm = sfm
	count = 0
	#print("\nIn replace_marker code:\n")
	
	for i,entry in enumerate(new_sfm):
		for j , field in enumerate(entry):
			marker, data = field
			if marker == find :
				count = count + 1
				new_sfm[i][j][0] = replace
	
	return new_sfm, count

def do_split_marker_by_script(sfm,find_marker,script1,script2,new_marker1,new_marker2):
#Find a given marker and split it by script.

	ad = AlphabetDetector()
	new_sfm = sfm
	count = 0
	print("\nIn do_split_marker_by_script code:\n")
	
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
					#print("\nFound '{}' only containing {}. Adding new field: {}".format(data,script,new_field))
					#print(new_sfm[i])
					
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
	#print("\nIn replace_marker2 code:\n")
	sfm[:] = [[[replace,data] if marker == find else [marker,data] for marker,data in entry] for entry in sfm]
		
	#print("\nLeaving replace_marker2 code:\n")
	return sfm


def replace_data(sfm, in_marker,find,replace):
#Replace data in a given marker with other data.
	print("Finding {} to replace with {} in field {}.".format(find,replace,in_marker))
	replacement_count = 0
	for i, entry in enumerate(sfm):
		for j, field in enumerate(entry):
			marker , data = field
			if marker == in_marker and data == find:
				#print("Found data match.")
				sfm[i][j][1] = replace
				replacement_count += 1
	return sfm, replacement_count


def count_markers(sfm):
	marker_count = Counter()
	marker_count_with_data = Counter()
	
	for entry in sfm:
		#print("Entry has {} fields. {}	".format(len(entry),entry))
		for field in entry:
			if len(field) == 2:
				#print("Field has {} parts. {}".format(len(field),field))
				marker , data = field
				marker_count.update([marker])
				marker_count_with_data.update([marker])
			elif len(field) == 1:
				marker = field
				marker_count.update([marker])
	return marker_count, marker_count_with_data


def fits_in_simple_mdf(entry):
	''' Function to check whether a given entry contains only one of each field in the MDF spec.'''

	marker_count = Counter()
	for field in entry:
#		print("marker_count is {}".format(marker_count))
#		print("Field[0] is {}".format(field[0]))
		marker_count.update([field[0]])
		if marker_count[field[0]] > 1:
#			print("Marker {} occurs more than once, - Doesn't fit.".format(field[0]))
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
	
	if not unknown_markers: 
		print("There were no unexpected markers seen in the file:")
	else :
		print("These unexpected markers were seen in the file:\n{}".format(unknown_markers))
	
	if not seen_markers:
		print("There were no unexpected markers seen in the file:")
	else :
		print("These expected markers were seen in the file:\n{}".format(seen_markers))
		
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
	

def get_sfm_info(sfm):
	marker_count, marker_count_with_data = count_markers(sfm)
	markers = [k for k in marker_count.keys()]
	markers.sort()

	#The sfm file is a list of entries, each containing a list of fields.
	#Extract data from all fields looking for repeated data. 
	#These are likely indicates a 'Range field' (Toolbox) or a 'List Field' (FLEx)

	#Create a dictionary with each marker as a key and a Counter() as the value.
	counter_dict = dict()

	for marker in markers:
		counter_dict[marker] = Counter()

	for entry in sfm:
		for marker,data in entry: 
			counter_dict[marker].update([data])

	return counter_dict, markers, marker_count, marker_count_with_data


def process_input_file(filein):	

	filename, file_extension = os.path.splitext(filein)
	if file_extension.lower() in csvfileexts :
		filetype = csv_ext
		
	elif file_extension.lower() in sfmfileexts :
		filetype = sfm_ext

	else :
		choice = empty
		while choice not in ['sfm', 's', 'csv', 'c', 'q']:
			choice = sanitised_input("The file extension {} isn't recognised. Should it be treated as an SFM or CSV file? Type s or c, or q to quit.>".format(file_extension), str.lower, range_=('sfm', 's', 'csv', 'c', 'q'))

		if choice in ['s','sfm'] :
			filetype = sfm_ext
		elif choice in ['c','csv'] : 
			filetype = csv_ext
		elif choice in ['q','quit'] :
			exit()

	if filetype == sfm_ext :
		#sfm = sfm_from_list(sfmlist_from_file(args.input))
		sfm = readsfm(args.input)
	elif filetype == csv_ext :
		sfm , No_slash_cells = readcsv(args.input)

		if No_slash_cells :
			print("The following cells don't contain a backslash marker.")
			with io.open("Slashless.txt", 'w', encoding = utf8) as out:
				out.write("There are cells that don't contain a backslash marker.\n")
				out.write("They are shown below, with the preceeding cell and the row and column.\n")
				out.write("{0:>5} {1:<5}  {2:}***{3:}\n".format('Row','Column','Preceeding cell', 'Slashless cell'))
				for item in No_slash_cells:
					out.write("{0:>5} {1:<5}  {2:}***{3:}\n".format(item.row,item.column,item.previous_cell,item.contents))
					print("Cell {}:{} contains: '{}'.".format(item.row,item.column, item.contents))
	return sfm


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

def split_file_info(simple_mdf,not_simple_mdf):	
	''' Return info about the split files. '''
	single_field_counter = Counter()
	double_field_counter = Counter()
	
	for i, entry in enumerate(not_simple_mdf):
		markers_in_entry  =  markers_not_fit(entry)
		lexeme = entry[0][1]
		not_fitting = [(k,v) for k,v in markers_in_entry.items() if v > 1]
#		print("Marker counts for entry {} are:\n{}\n".format(lexeme, markers_in_entry))
#		print("Markers not fitting: {}\n".format(not_fitting))

		if len(not_fitting) == 1:
			single_field_counter.update(not_fitting)
	
		if len(not_fitting) == 2:
			marker1 = not_fitting[0][0].strip(slash)
			marker2 = not_fitting[1][0].strip(slash)
			
			print([marker1 + space + marker2])
			double_field_counter.update([marker1 + space + marker2])
	
	#print(single_field_counter)
	print("A total of {} entries don't fit due to multiples of one field.".format(sum(single_field_counter.values())))
	#print(double_field_counter)
	print("A total of {} entries don't fit due to multiples of two fields.".format(sum(double_field_counter.values())))
		
	return None	


def show_main_menu(sfm):
	while True:
		counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)
		#print("main_menu is {} and it's type is {}".format(main_menu,type(main_menu)))
		
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
			field_chosen = None
			#field_chosen = choicebox('Choose field whose data you want to change.', 'Field Markers', [' '+x+' ' for x in markers])
			while field_chosen not in markers:
				field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
				if not field_chosen:
					break
			choice = sanitised_input("How would you like specify the changes to make? By file (csv) or typed in?", str, range_=('file','f','type','t'))
			if choice.lower() in ['file','f']:
				changefile = fileopenbox(title="Choose csv file containing changes.",msg='Choose csv file.',filetypes=['*.csv'])
				if changefile:
					sfm, total_replacements = process_replacements_from_file(sfm,field_chosen,changefile)
					print("Made {} replacements".format(total_replacements))
				else:
					continue
					
		if choice == '4':
			out_file = filesavebox(title="Save processed file as:")
			writesfm(sfm,overwrite,out_file)
			input("Processed SFM file written to {}\n\nPress enter to continue.".format(out_file))
		
		if choice == '5':
			info_file = filesavebox(title="Save processed file as:")
			print("Writing data to file {}.".format(info_file))
			counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)
			
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
			output_markers(marker_count, marker_count_with_data,info_file,overwrite)
			#output_counter(marker_count_with_data,"The most used markers are:")
			
		if choice == '6':
			limit = 6
			print("\nLooking for common data in each field.")
			print("Data repeated more than {} times is shown with a count of the occurances, under the field marker.".format(limit))
			counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)
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
		
		if choice == '7':
			out_file = filesavebox(title="Save processed file as:")
			writesfm_without_empty_markers(sfm,overwrite,out_file)
			input("Processed SFM file written to {}\n\nPress enter to continue.".format(out_file))
			out_file = filesavebox(title="Save processed file as:")
			writesfm_without_empty_markers(sfm,overwrite,out_file)
			input("Processed SFM file written to {}\n\nPress enter to continue.".format(out_file))

		if choice == '8':
			field_chosen = None
			#field_chosen = choicebox('Choose field whose data you want to change.', 'Field Markers', [' '+x+' ' for x in markers])
			while field_chosen not in markers:
				field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
				if not field_chosen:
					break
			counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)
			for item,count in counter_dict[field_chosen].items():
				print(item,"\t\t",count)
				
		if choice == '9':
			easy_file = filesavebox(title="Save the Simple-to-import file as:")
			hard_file = filesavebox(title="Save the Difficult-to-import file as:")
			simple_mdf,not_simple_mdf = split_file(sfm,easy_file,hard_file)
			print("There are {} simple entries.".format(len(simple_mdf)))
			print("There are {} not so simple entries.".format(len(not_simple_mdf)))
	
		if choice =='10':
			field_chosen = None
			#field_chosen = choicebox('Choose field whose data you want to split.', 'Field Markers', [' '+x+' ' for x in markers])
			while field_chosen not in markers:
				field_chosen = input("Type in the field whose data you want to change. Or hit enter to go back.")
				if not field_chosen:
					break
			print("Marker {} occurs {} times in the data.".format(field_chosen,marker_count[field_chosen]))
			sfm, count = do_split_marker_by_script(sfm,field_chosen,"LATIN","ARABIC","\\ar_la","\\ar_ar")
			print("{} entries modified.".format(count))
		
	# if args.output and fileout_extention in csvfileexts :	
		# writecsv(sfm, overwrite, args.output)

	# if args.output and fileout_extention in sfmfileexts :
		#print("\nWriting out the processed file {}".format(filename))
		#print("First entry is \n{}".format(sfm[0]))
		# writesfm(sfm,overwrite,args.output)
		
	return sfm, out_file, summary_file


if __name__ == "__main__":
	""" Run as a stand-alone script """
	
	args = parser.parse_args()
	
	if not args.input:
		args.input = fileopenbox(title="Choose a file to process.", filetypes=filemasks)

	sfm = process_input_file(args.input)
	counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)
	seen_markers, unknown_markers = check_markers(sfm,mdf_order)

	show_main_menu(sfm)


	if not args.output:
		args.output = filesavebox("Where would you like to save the output file")
		
	fileout , fileout_extention = os.path.splitext(args.output)


		
	# change = sanitised_input("Are is there data in a particular marker that needs to be changed? y/n >", str.lower, range_=('y', 'n'))

	# if change == 'y':
		
		# find_in_marker = sanitised_input("Which marker would you like to modify? Type the number of the marker.".format(marker), int, 1, len(markers))
		# find_in_marker = markers[find_in_marker - 1]

		# find_data = sanitised_input("Which data would you like to find?> Type the data.", str)
		
		# replacement_data = sanitised_input("What should {} be replaced with? Type the data.>".format(find_data), str)
		
		# confirm = sanitised_input("Looking for '{}' in marker: '{} to be replaced with '{}'. Is this correct? y/n >".format(find_data,find_in_marker,replacement_data), str.lower, range_=('y', 'n'))
		
		# if confirm == 'y':
			# new_sfm = replace_data(sfm[:],find_in_marker,find_data,replacement_data)
			# writesfm(new_sfm,overwrite,args.output)
			# sfm = new_sfm

	if (args.output) :
		# writesfm(sfm,overwrite,args.output)
		markersfile = args.output + "_markers.txt"
		counter_dict, markers, marker_count, marker_count_with_data = get_sfm_info(sfm)

		#writemarkers(marker_count, marker_count_with_data,markersfile,overwrite)
		#printmarkers(marker_count, marker_count_with_data)
		#output_markers(marker_count, marker_count_with_data)
		output_markers(marker_count, marker_count_with_data,markersfile,overwrite)
		#output_counter(marker_count_with_data,"The most used markers are:")

			# if args.output and fileout_extention in csvfileexts :
				# writecsv(sfm, overwrite, args.output)

			# if args.output and fileout_extention in sfmfileexts :
				# writesfm(sfm,overwrite,args.output)

				
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
