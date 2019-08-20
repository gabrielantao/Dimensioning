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
Read a svg generated by Drawing WB projection and convert into Qt paths.

Note: Unfortunately FreeCAD crashes everytime you try to use xml.dom, so
      here is used only regular expressions to parse the svg string.
      This problem is reported here.
      https://forum.freecadweb.org/viewtopic.php?t=24268
      https://forum.freecadweb.org/viewtopic.php?f=15&t=23380&start=40
"""

from PySide import QtCore
from GraphicItem import PathItem, VertexItem
import re
import FreeCAD

def svgParser(svg, hidden=False):
    re_path = re.finditer(r"\sd=\"([\-|\w|\s|\.|\,]*)\"", svg)
    re_circle = re.finditer(r"cx ={0} cy ={0} r ={0}".format(r"\"([\-|\d|\.]*)\""), svg)
    re_ellipse = re.finditer(r"<g transform = \"rotate\({0},{0},{0}\)\">\s*" + \
                             r"<ellipse cx =\"{0}\" cy =\"{0}\" rx =\"{0}\"" + \
                             r"  ry =\"{0}\"/>".format(r"([\-|\d|\.]*)"), svg)
    vertices = set()
    paths = []
    if svg.strip() == "":
        return (paths, vertices) #avoid ExpatError    
    for attr in re_path:
        attr = attr.groups()[0]
        list_ = re.split("([M|m|L|l|H|h|V|v|A|a|Q|q|T|t|C|c|S|s])", attr)[1:]
        for i in range(0, len(list_), 2):
            type_ = list_[i].strip()
            if type_ == "M":
                x, y = map(float, re.split("[,|\s]", list_[i+1].strip()))
                current_point = QtCore.QPointF(x, y)
#            elif type_ == "m":
#                x, y = map(float, moveto.match(list_[i+1]).groups())
#                current_point += QtCore.QPointF(x, y) 
            elif type_ == "L":
                x, y = map(float, re.split("[,|\s]", list_[i+1].strip()))
                new_point = QtCore.QPointF(x, y)
                paths.append(PathItem("line", current_point, new_point))
                current_point = QtCore.QPointF(x, y)
#            elif type_ == "l":
#                x, y = map(float, moveto.match(list_[i+1]).groups())
#                new_point = current_point + QtCore.QPointF(x, y)
#                paths.append(PathItem("line", current_point, new_point))
#                current_point += QtCore.QPointF(x, y) 
            elif type_ == "H":
                raise NotImplementedError("H command not implemented")
            elif type_ == "V":
                raise NotImplementedError("V command not implemented")
            elif type_ == "A":
                coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                paths.append(PathItem("arc", current_point, *coord))                         
                current_point = QtCore.QPointF(coord[5], coord[6])
            elif type_ == "Q":
                points = []
                coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                for i in range(0, len(coord), 2):
                    x, y = coord[i:i+2]
                    points.append(QtCore.QPointF(x, y))                    
                paths.append(PathItem("quadratic", current_point, *points))                         
                current_point = QtCore.QPointF(x, y) 
            elif type_ == "T":
                raise NotImplementedError("T command not implemented")
            elif type_ == "C":
                points = []
                coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                for i in range(0, len(coord), 2):
                    x, y = coord[i:i+2]
                    points.append(QtCore.QPointF(x, y))                    
                paths.append(PathItem("cubic", current_point, *points))                         
                current_point = QtCore.QPointF(x, y) 
            elif type_ == "S":
                raise NotImplementedError("S command not implemented")
            vertices.add(VertexItem(current_point))
    for attr in re_circle:
        c_x, c_y, r = map(float, attr.groups()) 
        current_point = QtCore.QPointF(c_x, c_y) #center
        points = [current_point, r, r] 
        paths.append(PathItem("circle", current_point, *points)) 
        vertices.add(VertexItem(current_point))
    for attr in re_ellipse:
        rot, p_x, p_y, c_x, c_y, r_x, r_y = map(float, attr.groups()) 
        pivot = QtCore.QPointF(p_x, p_y)
        points = [QtCore.QPointF(c_x, c_y), r_x, r_y, rot, pivot]
        paths.append(PathItem("ellipse", current_point, *points)) 
        vertices.add(VertexItem(current_point, [rot, pivot]))
    if hidden: #TODO: passar essa responsabilidade para uma funcao do task
        for path in paths:
            path.setHidden()
#    #TODO: setar aqui a espessura (...e a cor?)
    return (paths, vertices)