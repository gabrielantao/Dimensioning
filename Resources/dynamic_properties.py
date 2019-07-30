# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (c) 2019 Gabriel Antao <gabrielantao@poli.ufrj.br>          *   
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with Dimensioning FreeCAD Workbench.                            *
#*   If not, see <https://www.gnu.org/licenses/>                           * 
#*                                                                         *
#***************************************************************************/

"""
Script to insert Dynamic Properties in edited PrefsTemplate.ui.

TODO:
    1) verify if filechooser save preferences properly.
    2) create step-by-step document.
"""

from xml.dom import minidom
import sys

DEFAULT_COLOR = {"red": 0, "green": 0, "blue": 0}

if len(sys.argv) != 3:
    print("You must type\n\n\tpython script.py filename prefPath\n")    
    sys.exit()

workbench = "Dimensioning"
filename = sys.argv[1]
prefPath = "Mod/{}/{}".format(workbench, sys.argv[2])

# remove all \n and spaces characters
with open(filename, "r") as orig_file:
	input_xml = "".join([line.strip() for line in orig_file.read().splitlines()])

document = minidom.parseString(input_xml)

for elem in document.getElementsByTagName("widget"):
    widget = elem.getAttribute("class")
    ignore_widget = False
    for prop in elem.getElementsByTagName("property"):
        if prop.getAttribute("name") == "prefPath":
            ignore_widget = True
            break 
    if ignore_widget:
        continue    
    if widget == "Gui::PrefColorButton":
        # add color property
        color_prop = document.createElement("property")
        color_prop.setAttribute("name", "color")
        elem.appendChild(color_prop)
        # add color elem
        color_elem = document.createElement("color")
        color_prop.appendChild(color_elem)
        # add colors values
        for color in ["red", "green", "blue"]:
            new_color = document.createElement(color)
            color_value = document.createTextNode("{}".format(DEFAULT_COLOR[color]))
            new_color.appendChild(color_value)
            color_elem.appendChild(new_color)
    if widget[:9] == "Gui::Pref":
        # add prefEntry property
        pref_entry = document.createElement("property")
        pref_entry.setAttribute("name", "prefEntry")
        pref_entry.setAttribute("stdset", "0")
        elem.appendChild(pref_entry)
        # add prefEntry name
        str_elem = document.createElement("cstring")
        var_name = document.createTextNode(elem.getAttribute("name"))
        str_elem.appendChild(var_name)
        pref_entry.appendChild(str_elem)
        # add prefPath
        pref_path = document.createElement("property")
        pref_path.setAttribute("name", "prefPath")
        pref_path.setAttribute("stdset", "0")
        elem.appendChild(pref_path)
        # add prefPath name
        str_elem = document.createElement("cstring")
        var_name = document.createTextNode(prefPath)
        str_elem.appendChild(var_name)
        pref_path.appendChild(str_elem)
  
with open("new" + filename, "w") as new_file:
	new_file.write(document.toprettyxml(indent=" "))
	

