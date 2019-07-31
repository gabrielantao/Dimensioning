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
from Utils import mmtopt


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
        self.editModeOn = True
#        self.force_angle = True #only if one head_point is set
        self.default_angle = 45 # degree


    def getTailPos(self):
        return self.line().p1()
    
    def getHeadPos(self):
        return self.line().p2()
    
    def setTailPos(self, point):
        """Set line P1 as tail."""
        line = self.line()
        line.setP1(point)
        self.setLine(line)
    
    def setHeadPos(self, point):
        """Set line P2 as head."""
        line = self.line()
        line.setP2(point)
        self.setLine(line)
    
#    def setColor():
#        pass

    def setEditMode(self, value):
        """Edit mode, true when editing"""
        self.editModeOn = value
        
    def boundingRect(self):
        rect = super(Arrow, self).boundingRect()
        return rect.adjusted(-5, -5, 5, 5)
        
    def paint(self, painter, option, widget=None):
        pen = self.pen()
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(mmtopt(0.5))
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.black)
        painter.drawLine(self.line())


class PointCatcher(QtGui.QGraphicsRectItem):
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
        
        
#Linha de chamada (leader line)
# Essa linha de chamada pode servir de base para anotacoes, solda, tolerancias geometricas...
# Alguns features tem opcao de escolher uma linha de extensao ou nao

# Comecar por esse simbolo
class SurfaceFinishingItem(GraphicItem):
    """Build surface finishing symbols"""
    # Como funciona
    # 1) clica numa linha qualquer tipo (line, path, elipse, etc)
    # 2) desenha o simbolo base padrao
    # 3) insere as anotacoes do acabamento no simbolo (setadas na janela dialog)
    # 3) clica na posicao que deve ficar e da enter para inserir
    def __init__(self):
        self.show_leader_line = False
        self.arrowline = None #ArrowLine

class WeldingItem(GraphicItem):
    """Build welding symbols"""
    pass
