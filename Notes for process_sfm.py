These python scripts require Python v 3.x or later.
They were developed using Python 3.6.1 and as of today have only been used with that version.

The following plugins are required for some of the functions, they are listed with the version currently used for development.
alphabet-detector (0.0.7)
binaryornot (0.4.3)
chardet (3.0.4)
easygui (0.98.1)



Read an SFM file into a list of lists.
Treat the first word after a newline as a marker.
If there are markers without a backslash, tell the user the line number so they can fix it.
DONE

Then we can know which markers are duplicates of others.
If there are duplicate markers, ask the user which marker to replace with which other marker.
Do a find replace on duplicate markers.

Only allow 'known' fields and named custom fields. 
Get the user to name every field marker by choosing from a list of MDF fields and languages and scripts.
By filling in a list in a csv file!

Find the fields that contain a lot of duplicates. These are most likely to be 'range fields' in Toolbox, or 'List fields' in FLEx.
Allow the user to inspect the List Fields and clarify the valid list data for each list field.
Find and replace data that doesn't fit the list for that column.
Create objects from the Entries, Senses, Examples, and Subentries.

Read in a CSV file with markers in each cell so that it can be converted into an SFM file.
Provide the ability to write out SFM files in this format too.



Work to do:

Fix problems with markers being consider 'expected' and 'unexpected' at the same time.
Change the term to 'MDF' standard marker.
Include info about what MDF markers usually mean.

Get Cross reference information working.

Deal with \_sh at the begining of a file well, without removing the info.

Count populated and emtpy markers.



