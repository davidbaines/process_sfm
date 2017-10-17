#!/usr/bin/env python
# -*- coding: utf-8 -*-
#title			: menu.py
#description	: This program displays an interactive menu on CLI
#author			: 
#date			: 
#version		: 0.1
#usage			: python menu.py
#notes			: 
#python_version : 3.6  
#=======================================================================
 
#Functions to be accessed via these menus are :
# 0) Read in an sfm file or CSV file and convert it to a list of lists.
# 1) Replace one marker with another, or with some other marker.
# 2) In a given field find the whole field and replace the data with some other data.
# 3) Save the modified SFM file.
# 4) Write to another file summary information about the input file.
# 5) Split the entries into two files depending on whether they are simple to import or not.
# 6) Write the simple entries out to a file with their fields consistently ordered.
 
# Import the modules needed to run the script.
import sys, os

# =======================
#	 MENUS FUNCTIONS
# =======================

#Show a pre-defined menu
def show_menu(rubric,lines,quit): 
 
#	os.system('cls' if os.name == 'nt' else 'clear')
	valid_choices = [str(x) for x in range(1,len(lines)+1)]
	print("Valid choices are {}.\n".format(valid_choices))
	
	for line in rubric :
		print(line)

	for i,line in enumerate(lines):
		print(i+1, ') ' + line)

	print("Valid choices are :")
	for ch in valid_choices:
		print("{}".format(ch),end='  ')
	
	print("or {} to {}".format(quit[0],quit[1]))
	
	choice = input(" >>  ")
	print("\n" * 15) 
	
	if choice == str(quit[0]):
		exit()
		
	while choice not in valid_choices:
		choice = show_menu(rubric,lines,quit)
	return choice
 
# Define a menu with a rubric, list of options and option to quit.

def main_menu():
	rubric = [
	"To process sfm or csv data.\n",\
	"Please choose what you would like to do."\
	]
	lines = [
	"Show information about the file.",\
	"Change a marker.",\
	"Change data in a given field.",\
	"Save the changes to an SFM file.",\
	"Write summary information about the file.",\
	"Write information about the sfm file to a file.",\
	"Save the changes to an SFM file omitting most empty markers.",\
	"List the unique data in a given marker.",\
	"Split the file into simple-to-import and otherwise.",\
	"Split marker according to script.\n"]

	quit = [0, "Quit\n"]
	return (rubric,lines,quit)


# =======================
#	  MAIN PROGRAM
# =======================
 
# Main Program
if __name__ == "__main__":
	# Launch main menu
	main_menu = main_menu()
	choice = show_menu(*main_menu)
	