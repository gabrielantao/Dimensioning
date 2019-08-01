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
from Utils import mmtopt, rotate

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
        pen.setColor(QtCore.Qt.darkGray)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(2)
        painter.setPen(pen)
        painter.drawRect(item_pos.x()-4, item_pos.y()-4, 9, 9)
        

