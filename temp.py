
from easygui import choicebox
empty = ''
slash ='\\'
markers = ['\\cf', '\\cn', '\\de', '\\dn', '\\lx', '\\nt', '\\pn', '\\ps', '\\sy', '\\xe', '\\xn', '\\xv']
# ask the user to choose a marker it return using easygui:
marker = choicebox('Choose the field you want to duplicate.', 'Field Markers',[' '+x+' ' for x in markers])

print("Marker chosen is {}".format(marker.strip()))
