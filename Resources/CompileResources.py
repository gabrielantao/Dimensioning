#!/usr/bin/env python2
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
Create resources python file (*_rc.py)
"""
import os 
import glob

py_filename = "Dimensioning_rc.py" 
qrc_filename = "Dimensioning.qrc"
main_path = os.path.dirname(os.getcwd())

if os.path.exists(qrc_filename):
	os.remove(qrc_filename)

if os.path.exists(py_filename):
	os.remove(os.path.join(main_path, py_filename))

qrc = "<RCC>\n\t<qresource>"
#TODO: substituir a lista para mandar procurar por toda a pasta resources?
for fn in glob.glob("icons/*.svg") + glob.glob("ui/*.ui") + glob.glob("fonts/*.ttf") + glob.glob("icons/*.png"): 
    qrc = qrc + "\n\t\t<file>%s</file>" % fn
qrc = qrc + "\n\t</qresource>\n</RCC>"

print(qrc)

f = open(qrc_filename, "w")
f.write(qrc)
f.close()

os.system("pyside-rcc -o {} {}".format(py_filename, qrc_filename))
os.rename(py_filename, os.path.join(main_path, py_filename)) #move file
#os.remove(qrc_filename)
