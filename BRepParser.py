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
Boundary Representation (BRep) parser module. This module reads the output from 
Drawing Workbench and create the correspondent BRep objects.
"""
## TODO LIST
# () write methods to make ortographic projections
# () write conversion BSpline -> Bezier

# NOTE: This module should be implemented in order to have a better control
#       over updates in model. Once you have information about all curves in
#       FreeCAD model, you can track all updates then automatic link those
#       to the drawing. 

class BRepParser:
    def __init__(self, BRep):
        """Generate the objects from a BRep string"""
        BRep = BRep.split("\n")
        self.curves = []
        self.vertex = {}
        i = 0
        while i < len(BRep):
            # NOTE: ignore content type, version lines and Curves2ds
            line = BRep[i].strip()
            line = line.split()
            if len(line) == 0:
                i += 1
                continue
            if line[0] == "Curves":
                i += 1
                count = int(line[1])
                self.curves.extend([createCurve(record) for record in BRep[i:i+count]])
                i += count
            # NOTE: For now, ignore Polygon3D, PolygonOnTriangulations, 
            #       Surfaces and Triangulations.    
            elif line[0] == "TShapes":
                self.shape_id = int(line[1]) #shape number
                i += 1
            elif line[0] == "Ve":
                self.vertex[self.shape_id] = map(float, BRep[i+2].split())
                self.shape_id -= 1
                i += 6
            elif line[0] == "Ed":
                i += 1
                j = 0
                while True:
                    line = BRep[i+j].split()
                    if len(line) == 0:
                        j += 1
                        continue
                    if line[-1] == "*":
                        break
                    j += 1
                j += 1
                self.parseEdge(BRep[i:i+j])
                self.shape_id -= 1
                i += j
            # NOTE: For now, ignore Wire, Face, Shell, So, CS, Co  
            else: #ignore line
                i += 1
                
    def parseEdge(self, representation):
        subshape = representation[-1].split()
        ve_index_1 = abs(int(subshape[0])) #its vertex 1 index
        ve_index_2 = abs(int(subshape[2])) #its vertex 2 index
        for line in representation:
            if line.strip() == "0":
                break
            token_list = line.split()
            if token_list[0] == "1":
                curve_index = int(token_list[1]) - 1 # curve index in curves list
                param_min = float(token_list[3]) # min value param 
                param_max = float(token_list[4]) # max value param
                vertex_1 = self.vertex[ve_index_1]
                vertex_2 = self.vertex[ve_index_2]
                edge = Edge(vertex_1, vertex_2, param_min, param_max)
                self.curves[curve_index].setEdge(edge)

def createCurve(record):
    """Factory to create record."""
    curve_num = record[0]
    if curve_num == "1":
        return Line(record[2:])
    elif curve_num == "2":
        return Circle(record[2:])
    elif curve_num == "3": 
        return Ellipse(record[2:])
    elif curve_num == "6": 
        return Bezier(record[2:])
    elif curve_num == "7":
        return BSpline(record[2:])
    raise NotImplementedError("This curve is not implement for now.")


class Curve3D(object):
    def __init__(self, record):
        self.record = record
        # TODO: escrever o leitor para essa funcao 

    def setEdge(self, edge):
        self.edge = edge
        
    def printEdge(self):
        print("{}".format(str(self.edge)))
    
    def __repr__(self):
        return "{}".format(str(self.edge))


class Line(Curve3D):
    def __init__(self, record):
        super(Line, self).__init__(record)
        token_list = record.split()
        self.P = map(float, token_list[:3])
        self.D = map(float, token_list[3:])
        
    def printCurve(self):
        format_list = [self.P, self.D, self.edge.param_min, self.edge.param_max]
        print("C(u) = {} + u {}, u in [{}, {}]".format(*format_list))
        
    def __repr__(self):
        return "Line(P={}; D={})\n".format(self.P, self.D)

class Circle(Curve3D):
    def __init__(self, record):
        super(Circle, self).__init__(record)
        token_list = record.split()
        self.P = map(float, token_list[:3])
        self.N = map(float, token_list[3:6])
        self.Dx = map(float, token_list[6:9])
        self.Dy = map(float, token_list[9:12])
        self.r = float(token_list[12]) 
        
    def printCurve(self):
        list_ = [self.P, self.r, self.Dx, self.Dy, self.edge.param_min, self.edge.param_max]
        print("C(u) = {} + {} (cos(u) {} + sin(u) {}), u in [{}, {}]".format(*list_))
        
    def __repr__(self):
        list_ = [self.P, self.N, self.Dx, self.Dy, self.r]
        return "Circle(c = {}; N = {}; Dx = {}; Dy = {}; r = {})\n".format(*list_)

class Ellipse(Curve3D):
    pass

class Bezier(Curve3D):
    pass
#    def __init__(self, record):
#        super(Circle, self).__init__(record)
#        token_list = record.split()
#        self.r = float(token_list[0])
#        self.N = map(float, token_list[3:6])
#        self.Dx = map(float, token_list[6:9])
#        self.Dy = map(float, token_list[9:12])
#        self.r = float(token_list[12]) 
#        
#    def printCurve(self):
#        list_ = [self.P, self.r, self.Dx, self.Dy, self.edge.param_min, self.edge.param_max]
#        print("C(u) = {} + {} (cos(u) {} + sin(u) {}), u in [{}, {}]".format(*list_))
#        
#    def __repr__(self):
#        list_ = [self.P, self.N, self.Dx, self.Dy, self.r]
#        return "Circle(c = {}; N = {}; Dx = {}; Dy = {}; r = {})\n".format(*list_)


class BSpline(Curve3D):
    # TODO: It has to be converted into Bezier curves once svg can be just bezier
    # https://math.stackexchange.com/questions/417859/convert-a-b-spline-into-bezier-curves
    def __init__(self, record):
        super(Circle, self).__init__(record)
        token_list = record.split()
        self.r = float(token_list.pop()) # rational flag
        self.m = float(token_list.pop()) # degree
        self.n = float(token_list.pop()) # pole count
        self.k = float(token_list.pop()) # knot count
        self.B = []
        self.h = []
        for i in range(0, len(token_list), 4):
            self.B.append(map(float, token_list[i:i+3]))
            self.h.append(float(token_list[i+3]))
        
    def printCurve(self):
        list_ = [self.P, self.r, self.Dx, self.Dy, self.edge.param_min, self.edge.param_max]
        print("C(u) = {} + {} (cos(u) {} + sin(u) {}), u in [{}, {}]".format(*list_))
        
    def __repr__(self):
        list_ = [self.P, self.N, self.Dx, self.Dy, self.r]
        return "Circle(c = {}; N = {}; Dx = {}; Dy = {}; r = {})\n".format(*list_)



 
class Edge:
    def __init__(self, vertex_1, vertex_2, param_min, param_max):
        self.vertex_1 = vertex_1
        self.vertex_2 = vertex_2
        self.param_min = param_min
        self.param_max = param_max
                    
    def __repr__(self):
        return "Edge({}, {}), ".format(self.vertex_1, self.vertex_2) + \
               "u in [{}, {}]\n".format(self.param_min, self.param_max)
    
    def __str__(self):
        return "Edge({}, {}), ".format(self.vertex_1, self.vertex_2) + \
               "u in [{}, {}]\n".format(self.param_min, self.param_max)

    
if __name__ == "__main__":
    with open("./Test/cilinder45degree.brep", "r") as f:
        brep = BRepParser(f.read())
        for curve in brep.curves:
            curve.printCurve()
