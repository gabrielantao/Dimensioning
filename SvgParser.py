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
"""

from xml.dom import minidom
import re
from PySide import QtCore

from GraphicItem import PathItem, VertexItem
import FreeCAD

# TODO: 
# (X) recalcular o viewport {Usar o grupo para mover quando nao estiver no modo de edicao}
# () gerar o "frame" que eh o grupo de itens
class SvgParser:
    def __init__(self, svg, h_margin=10, v_margin=10):
        moveto = re.compile(r"(-?\d+\.\d*)\s*,?\s*(-?\d+\.\d*)?")
        self.vertices = set()
        self.paths = []
        if svg.strip() == "":
            return #avoid ExpatError    
        xml = minidom.parseString(svg)
        viewport = QtCore.QRectF(0, 0, 0, 0)
        for node in xml.getElementsByTagName("path"):
            attr = node.getAttribute("d")
            list_ = re.split("([M|m|L|l|H|h|V|v|A|a|Q|q|T|t|C|c|S|s])", attr)[1:]
            for i in range(0, len(list_), 2):
                type_ = list_[i].strip()
                if type_ == "M":
                    x, y = map(float, re.split("[,|\s]", list_[i+1].strip()))
                    current_point = QtCore.QPointF(x, y)
                elif type_ == "m":
                    x, y = map(float, moveto.match(list_[i+1]).groups())
                    current_point += QtCore.QPointF(x, y) 
                elif type_ == "L":
                    x, y = map(float, re.split("[,|\s]", list_[i+1].strip()))
                    new_point = QtCore.QPointF(x, y)
                    self.paths.append(PathItem("line", current_point, new_point))
                    current_point = QtCore.QPointF(x, y)
                elif type_ == "l":
                    x, y = map(float, moveto.match(list_[i+1]).groups())
                    new_point = current_point + QtCore.QPointF(x, y)
                    self.paths.append(PathItem("line", current_point, new_point))
                    current_point += QtCore.QPointF(x, y) 
                elif type_ == "H":
                    raise NotImplementedError("H command not implemented")
                elif type_ == "V":
                    raise NotImplementedError("V command not implemented")
                elif type_ == "A":
                    coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                    self.paths.append(PathItem("arc", current_point, *coord))                         
                    current_point = QtCore.QPointF(coord[5], coord[6])
                elif type_ == "Q":
                    points = []
                    coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                    for i in range(0, len(coord), 2):
                        x, y = coord[i:i+2]
                        points.append(QtCore.QPointF(x, y))                    
                    self.paths.append(PathItem("quadratic", current_point, *points))                         
                    current_point = QtCore.QPointF(x, y) 
                elif type_ == "T":
                    raise NotImplementedError("T command not implemented")
                elif type_ == "C":
                    points = []
                    coord = map(float, re.split("[,|\s]", list_[i+1].strip()))
                    for i in range(0, len(coord), 2):
                        x, y = coord[i:i+2]
                        points.append(QtCore.QPointF(x, y))                    
                    self.paths.append(PathItem("cubic", current_point, *points))                         
                    current_point = QtCore.QPointF(x, y) 
                elif type_ == "S":
                    raise NotImplementedError("S command not implemented")
                self.vertices.add(VertexItem(current_point))
        for node in xml.getElementsByTagName("circle"):
            points = []
            c_x = float(node.getAttribute("cx")) 
            c_y = float(node.getAttribute("cy"))
            r = float(node.getAttribute("r"))
            current_point = QtCore.QPointF(c_x, c_y)
            points.append(current_point) #center 
            points.append(r) #radius
            points.append(r) #idem
            self.paths.append(PathItem("circle", current_point, *points)) 
            self.vertices.add(VertexItem(current_point))
        for node in xml.getElementsByTagName("ellipse"):
            points = []
            c_x = float(node.getAttribute("cx")) 
            c_y = float(node.getAttribute("cy"))
            current_point = QtCore.QPointF(c_x, c_y)
            points.append(current_point) #center 
            points.append(float(node.getAttribute("rx"))) #radius_x
            points.append(float(node.getAttribute("ry"))) #radius_y
            transform = node.parentNode.getAttribute('transform')
            transform = re.split(r"[\(|\)|,]", transform)
            transform = map(float, transform[1:4])
            points.append(transform[0]) #rotation
            pivot = QtCore.QPointF(transform[1], transform[2])
            points.append(pivot) 
            self.paths.append(PathItem("ellipse", current_point, *points)) 
            self.vertices.add(VertexItem(current_point, [transform[0], pivot]))
   
        
    def resetViewport(self, viewport, x, y):
        if x < viewport.x():
            viewport.setX(x)
        elif x > viewport.width():
            viewport.setWidth(x)
        if y < viewport.y():
            viewport.setY(y)
        elif y > viewport.y():
            viewport.setHeight(y)
        
    def getVertices(self):
        return self.vertices
    
    def getPathItems(self):
        return self.paths
            