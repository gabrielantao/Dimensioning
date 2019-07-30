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
Script to export preference variables from preference .ui files.
"""

from xml.dom import minidom
import sys, os
import json


preferences = {}

for filename in sys.argv[1:]:
    if not os.path.isfile(filename):
        print("File {} does not exit.".format(filename))
        continue
    document = minidom.parse(filename)
    for widget in document.getElementsByTagName("widget"):
        class_name = widget.getAttribute("class")
        widget_name = widget.getAttribute("name")
        for prop in widget.getElementsByTagName("property"):
            if prop.getAttribute("name") == "prefPath":
                path = prop.getElementsByTagName("cstring")[0].firstChild.data
                path = path.split("/")[-1]
                if not (path in preferences):
                    preferences[path] = {}
        # This is convenient for avoiding conflicts when importing preferences
#        if widget_name in preferences:
#            print("The variable {} in {} already exist. \
#            Change this name.".format(widget_name, filename))
#            sys.exit()
#        if class_name[:9] != "Gui::Pref":
#            continue
        # NOTE: This preference do not allow setting a default value. This is a
        #       problem of FreeCAD preferences and widget arquitecture.
        if class_name == "Gui::PrefFileChooser":
            preferences[path][widget_name] = ""
            print("Warning: Gui::PrefFileChooser do not implent the default " +
                  "filename or filepath names. <{}>".format(widget_name))
        elif class_name == "Gui::PrefSpinBox":
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "value":
                    num = prop.getElementsByTagName("number")[0].firstChild.data
                    preferences[path][widget_name] = num
        elif class_name == "Gui::PrefColorButton":
            red = widget.getElementsByTagName("red")[0].firstChild.data
            green = widget.getElementsByTagName("green")[0].firstChild.data
            blue = widget.getElementsByTagName("blue")[0].firstChild.data
            preferences[path][widget_name] = [red, green, blue]
        elif class_name == "Gui::PrefSlider":
            val = ""
            min = ""
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "value":
                    val = prop.getElementsByTagName("number")[0].firstChild.data
                if prop.getAttribute("name") == "minimum":
                    min = prop.getElementsByTagName("number")[0].firstChild.data
            if val != "":
                preferences[path][widget_name] = val
            elif min != "":
                preferences[path][widget_name] = min
            else:
                preferences[path][widget_name] = "0"
        # NOTE: Maybe this should be better handled because many PrefRadioButton
        #      are not linked to the same variable. This is a problem of FreeCAD
        #       preferences arquitecture itself. You can group PrefRadioButton
        #       with prefixed names and handle then in your app.
        elif class_name == "Gui::PrefRadioButton":
            preferences[path][widget_name] = "false"
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "checked":
                    check = prop.getElementsByTagName("bool")[0].firstChild.data
                    preferences[path][widget_name] = check
        elif class_name == "Gui::PrefCheckBox":
            preferences[path][widget_name] = "false"
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "checked":
                    check = prop.getElementsByTagName("bool")[0].firstChild.data
                    preferences[path][widget_name] = check
        elif class_name == "Gui::PrefComboBox":
            preferences[path][widget_name] = ""
            i = "0"
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "currentIndex":
                    i = prop.getElementsByTagName("number")[0].firstChild.data
            if i == "-1":
                preferences[path][widget_name] = ""
                continue
            else:
                item = widget.getElementsByTagName("item")[int(i)]
            for prop in item.getElementsByTagName("property"):
                if prop.getAttribute("name") == "text":
                    txt = prop.getElementsByTagName("string")[0].firstChild.data
            preferences[path][widget_name] = txt
        elif class_name == "Gui::PrefLineEdit":
            preferences[path][widget_name] = ""
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "text":
                    txt = prop.getElementsByTagName("string")[0].firstChild.data
                    preferences[path][widget_name] = txt
        elif class_name == "Gui::PrefDoubleSpinBox":
            for prop in widget.getElementsByTagName("property"):
                if prop.getAttribute("name") == "value":
                    num = prop.getElementsByTagName("double")[0].firstChild.data
                    preferences[path][widget_name] = num
        elif class_name == "Gui::PrefFontBox":
            font_prop = widget.getElementsByTagName("family") #only font name
            if len(font_prop) == 0:
                preferences[path][widget_name] = ""
            else:
                preferences[path][widget_name] = font_prop[0].firstChild.data

with open("preferences.json", "w") as new_file:
	new_file.write(json.dumps(preferences, indent=4, sort_keys=True))
