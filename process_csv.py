def readcsv(filename):

	#print("Reading csv file : {}".format(filename))
	with open(filename, 'r', encoding="utf8") as infile:
		datareader = csv.reader(infile, dialect='default')
		firstline = next(datareader)
	print("\n\nThe first line of the data is: \n{}".format(firstline))
	choice = sanitised_input("Does the first line contain markers only?",str)
	if choice.lower()[0] == 'y':
		no_slash_cells = []
		sfm, markers = readcsv_with_headers(filename)
		return sfm, markers, no_slash_cells
	else:	
		sfm, markers, no_slash_cells = read_csv_with_markers_in_cells(filename)
		#print("Returning sfm,markers and no_slash_cells, lengths are {}, {} and {} respectively.\n".format(len(sfm),len(markers),len(no_slash_cells)))
		return sfm, markers, no_slash_cells
	
def read_csv_with_markers_in_cells(filename):
	print("\nReading csv file: {}\nLooking for markers in each cell.\n".format(filename))

	sfm = []
	markers = []

	No_slash_info = namedtuple('No_slash_info',['row','column','contents','previous_cell'])
	no_slash_cells = []
	
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
					no_slash_cells.append(No_slash_info(i+2,num_to_column(j+1), cell,previous_cell))
					#raise ValueError("Cell in Row {}, Column {} doesn't contain a slash. Contents are :{}".format(i+2,num_to_column(j+1), cell))
					previous_cell = cell
					continue
				if space in cell:
					#Separate the marker from the data.
					marker, data = cell.split(space,1)
					if len(data) == 0 :
						print("This marker {} has no data {}".format(marker,data))
						
					entry.append([marker,data])
					previous_cell = cell
			sfm.append(entry)
		#print("Returning sfm,markers and no_slash_cells, lengths are {}, {} and {} respectively.\n".format(len(sfm),len(markers),len(no_slash_cells)))
		#print("sfm is: \n {}".format(sfm))
		#exit()
	return sfm , markers, no_slash_cells

def readcsv_with_headers(filename):

	print("\nReading csv file: {}\nLooking for markers in the first line.\n".format(filename))
	markers = []
	sfm = []
	#These 'vital markers' are added to the entry even when they contain no data.
	#Other empty markers are not added to the entry.
	vital_markers = ["\lx","\ps","\sn"]
	
	with open(filename, 'r', encoding="utf8") as infile:
		datareader = csv.reader(infile, dialect='default')
		firstline = next(datareader)
		for i, marker in enumerate(firstline):
			if marker == empty:
				raise ValueError("\nColumn heading for column {} is empty.".format(i+1))
			elif len(marker) > 0 and marker[0] != slash:
				raise ValueError("\nThe column heading for column {} doesn't begin with a slash.\nHeading is {}\n".format(i+1,marker))
			elif len(marker) > 1 and marker[0] == slash:
				markers.append(marker)
			else:
				raise ValueError("\nSeems like a logic error in the code in the function readcsv_with_headers!\n")

		print(firstline)
		print(markers)
		
		# print("{} cells were found on the first line.".format(len(firstline)))
		# print("{} markers were found before the first empty cell.".format(empty_header_cell[0]))
		# print("{} empty header cells were found.".format(len(empty_header_cell)))
		# if len(firstline) == len(empty_header_cell) + empty_header_cell[0] :
			# print("No cells had data after the first empty header cell. {}".format(len(empty_header_cell)))
		
		for i,row in enumerate(datareader):
			entry = []
			for j,data in enumerate(row):
				if j+1 > len(markers):
					print("Found the {}th data item: {} and there are only {} markers".format(j+1,data,len(markers)))
					exit()
				marker = markers[j]
				if len(data) > 0:
					entry.append([marker,data])		
				elif data == empty :
					if marker in vital_markers:
						entry.append([marker,empty])
					else:
						continue
				else:
					raise ValueError("Don't know what happened here!\n Marker is {} and data is {} line no. is {}".format(marker,data,j))
					
			sfm.append(entry)
	return sfm, markers
	
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