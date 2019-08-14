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
Superclasses for all graphic items on page.
"""

from PySide import QtGui, QtCore
from Utils import mmtopx, mmtopt, rotate, angleBetween
import FreeCAD

# https://doc.qt.io/qt-5/qtwidgets-graphicsview-diagramscene-example.html
# https://doc.qt.io/archives/qt-4.8/qt-graphicsview-diagramscene-arrow-cpp.html
# http://www.richelbilderbeek.nl/CppQtExample34.htm
class GraphicItem(QtGui.QGraphicsItem):
    """Basic Graphic Item that reimplements all relevant events"""
    pass

class GarphicItemGroup(QtGui.QGraphicsItemGroup):
    """Group all elements in a view"""
    pass

#classe base para desenhar setas de guia para solda, acabamento, anotacao, etc.
# Nao usada para as dimensoes, para elas usar outro metodo (?)
class Arrow(QtGui.QGraphicsLineItem):
    """Base class for lines that guide welding symbols, surf finishing symbols,
       local note, etc."""
    def __init__(self, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)
        self.head = "" # head name
        self.tail = "" # tail name
        self.setBrush(QtCore.Qt.black)
    
    def setTail(self, name):
        """Set tail type name."""
        self.tail = name
    
    
    def setHead(self, name):
        """Set head type name."""
        self.head = name
        
    def setBrush(self, color):
        """Set brush for paint arrow head and tail."""
        self.brush = QtGui.QBrush(color)

    def getTailPos(self):
        """Get scene point P1 as tail."""
        return self.line().p1()
    
    def getHeadPos(self):
        """Get scene point P2 as head."""
        return self.line().p2()
    
    def setTailPos(self, point):
        """Set scene point P1 as tail."""
        line = self.line()
        line.setP1(point)
        self.setLine(line)
    
    def setHeadPos(self, point):
        """Set scene point P2 as head."""
        line = self.line()
        line.setP2(point)
        self.setLine(line)
   
    def boundingRect(self):
        rect = super(Arrow, self).boundingRect()
        return rect.adjusted(-5, -5, 5, 5)
        
    def paint(self, painter, option, widget=None):
        # Draw line
        pen = self.pen()
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(mmtopt(0.5))
        painter.setPen(pen)
        painter.setBrush(self.brush)
        painter.drawLine(self.line())
        # Draw tail
        # TODO: implement tail
        # Draw head
        pos = self.mapFromScene(self.getHeadPos())
        angle = self.line().angle()
        if self.head == "Filled Arrow":
            polygon = QtGui.QPolygonF()
            polygon.append(pos - rotate(QtCore.QPointF(12, -2), angle))
            polygon.append(pos + QtCore.QPointF(0, 0))
            polygon.append(pos - rotate(QtCore.QPointF(12, 2), angle))
            painter.drawPolygon(polygon)
        elif self.head == "Open Arrow":
            polyline = QtGui.QPolygonF()
            polyline.append(pos - rotate(QtCore.QPointF(12, -3), angle))
            polyline.append(pos + QtCore.QPointF(0, 0))
            polyline.append(pos - rotate(QtCore.QPointF(12, 3), angle))
            painter.drawPolyline(polyline)
        elif self.head == "Dot":
            painter.drawEllipse(pos, 2, 2)


class PointCatcher(QtGui.QGraphicsRectItem):
    """This class implements a tiny region to move arrow head or tail."""
    def __init__(self, arrow, parent=None, scene=None):
        super(PointCatcher, self).__init__(parent, scene)
        self.arrow = arrow # associated arrow
        self.setPos(arrow.getHeadPos()+QtCore.QPointF(-3, -3))
        self.setRect(0,0,10,10)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
    
    def mouseMoveEvent(self, event):
        point = self.mapToScene(self.rect().center())
        self.arrow.setHeadPos(point)
        super(PointCatcher, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(self.rect().center())
        self.arrow.setHeadPos(point)
        super(PointCatcher, self).mouseReleaseEvent(event)
        
    def paint(self, painter, option, widget=None):
        pos = self.arrow.getHeadPos()
        item_pos = self.mapFromScene(pos)
        pen = QtGui.QPen()
        if self.isSelected():
            pen.setColor(QtCore.Qt.magenta)
        else:
            pen.setColor(QtCore.Qt.darkGray)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(2)
        painter.setPen(pen)
        painter.drawRect(item_pos.x()-4, item_pos.y()-4, 9, 9)
        
#TODO LIST
# () Refazer a shape circulo
# () Refazer a shape elipse
# () Refazer a shape arc        
# 1) () acertar o arco
class PathItem(QtGui.QGraphicsPathItem):
    """Generic class to all paths."""
    def __init__(self, path_type, start_point, *data):
        super(PathItem, self).__init__()
#        self.editModeOn = False
        self.type = path_type
        self.start_point = start_point #QPoint
        self.data = data #tuple
        # Set pen
        self.pen = QtGui.QPen(QtCore.Qt.black)
        self.pen.setWidthF(2) # TODO: alterar a espessura
        self.setPen(self.pen)
        self.setAcceptHoverEvents(True)
        # Create path
        path = QtGui.QPainterPath()
        path.moveTo(mmtopx(self.start_point))
        if self.type == "line":
            path.lineTo(mmtopx(self.data[0]))
        elif self.type == "arc":
            path.arcTo(*self.convertArc(data))
        elif self.type == "cubic":
            data = [mmtopx(p) for p in self.data]
            path.cubicTo(*data)
        elif self.type == "circle" or self.type == "ellipse":
            data = [mmtopx(p) for p in self.data]
            path.addEllipse(*data)
        self.setPath(path)
    
    def convertArc(self, data):
        """Convert parameterization from endpoint to center.
        https://www.w3.org/TR/SVG/implnote.html#ArcConversionEndpointToCenter
        """
        from math import radians, sin, cos, sqrt
        import numpy as np
        x_1 = self.start_point.x()
        y_1 = self.start_point.y()
        r_x = data[0]
        r_y = data[1]
        phi = radians(data[2]) #rotation
        f_a = data[3] #large arc
        f_s = data[4] #sweep
        x_2 = data[5]
        y_2 = data[6]
        # NOTE: It seems that FreeCAD never apply rotation to the arcs.
        #       FreeCAD recalculate new values to the arc instead.
        xy_prime = np.mat([[cos(phi), sin(phi)], [-sin(phi), cos(phi)]]) * \
                   np.array([[(x_1-x_2)/2], [(y_1-y_2)/2]])
        x_prime = xy_prime.item((0, 0))
        y_prime = xy_prime.item((1, 0))
        factor = -1 if f_a == f_s else 1 #if large_arc == sweep
        c_prime = factor*sqrt(((r_x*r_y)**2-(r_x*y_prime)**2-(r_y*x_prime)**2) / \
                              ((r_x*y_prime)**2+(r_y*x_prime)**2))
        c_prime *= np.array([[r_x*y_prime/r_y], [-r_y*x_prime/r_x]])
        c = np.mat([[cos(phi), -sin(phi)], [sin(phi), cos(phi)]])*c_prime + \
            np.array([[(x_1+x_2)/2], [(y_1+y_2)/2]])
        c_x_prime = c_prime.item((0, 0))
        c_y_prime = c_prime.item((1, 0))
        start_angle = angleBetween(np.array([[1], [0]]), 
                                   np.array([[(x_prime-c_x_prime)/r_x],
                                             [(y_prime-c_y_prime)/r_y]]))
        arc_angle = angleBetween(np.array([[(x_prime-c_x_prime)/r_x],
                                           [(y_prime-c_y_prime)/r_y]]),
                                 np.array([[(-x_prime-c_x_prime)/r_x],
                                           [(-y_prime-c_y_prime)/r_y]])) % 360   
#        if f_s == 0 and arc_angle > 0:
#            arc_angle -= 360
#        elif f_s == 1 and arc_angle < 0:
#            arc_angle += 360
        if f_s == 0:
            arc_angle = abs(arc_angle)
        else:
            arc_angle = -abs(arc_angle)
        
        # NOTE: phi always zero
        # Real rect (dimensions in millimiters)
        rect = QtCore.QRectF()
        width = 2 * r_x
        height = 2 * r_y
        rect.setWidth(width)
        rect.setHeight(height)
        center = QtCore.QPointF(c.item((0, 0)), c.item((1, 0)))
        rect.moveCenter(center)
        self.data = (rect, start_angle, arc_angle)
        # Rect to be drawn (dimensions in pixels)
        rect = QtCore.QRectF()
        rect.setWidth(mmtopx(width))
        rect.setHeight(mmtopx(height))
        center = QtCore.QPointF(mmtopx(c.item((0, 0))), mmtopx(c.item((1, 0))))
        rect.moveCenter(center)
        # PRINTS
        FreeCAD.Console.PrintMessage(" {}\n".format(start_angle))
        FreeCAD.Console.PrintMessage("start {}\n".format(self.start_point))
        FreeCAD.Console.PrintMessage("end {} {}\n".format(x_2, y_2))
        return (rect, start_angle, arc_angle)
    
    def hoverEnterEvent(self, event):    
        pen = QtGui.QPen(QtGui.QColor(255, 150, 0))
        pen.setWidthF(2)
        self.setPen(pen)
    
    def hoverLeaveEvent(self, event):
        self.setPen(self.pen)
        
        
class VertexItem(QtGui.QGraphicsPathItem):
    def __init__(self, point):
        super(VertexItem, self).__init__()
        self.editModeOn = False
        self.point = QtCore.QPointF(mmtopx(point.x()), mmtopx(point.y()))
        self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        # Create path
        painter_path = QtGui.QPainterPath()
        painter_path.addEllipse(self.point, 5, 5)
        self.setPath(painter_path)

    def __eq__(self, other):
        return isinstance(other, VertexItem)
        
    def __hash__(self):
        return hash((self.point.x(), self.point.y()))
    
    def paint(self, painter, option, widget=None):
        brush = QtGui.QBrush(QtCore.Qt.darkGray)
        if self.isSelected():
            brush.setColor(QtCore.Qt.magenta)
        else:
            brush.setColor(QtCore.Qt.darkGray)
        painter.setBrush(brush)
        painter.drawPath(self.path())
#        super(VertexItem, self).paint(painter, option, widget)