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


### EXEMPLOS IMPORTANTES ###
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
        self.head_point = [] #TODO: change for QPointF
        self.middle_point = [] #TODO: change for QPointF
        self.tail_point = []  #TODO: change for QPointF
#        self.force_angle = True #only if one head_point is set
        self.default_angle = 45 # degree

    
    def setTailPos(self):
        pass
    
    def setColor():
        pass

#    def boundingRect(self):
#        # TODO: alterar os valores dos pontos
#        extra = (self.pen().width() + 20) / 2.0
#        p1 = self.line().p1()
#        p2 = self.line().p2()
#        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

#    def shape(self):
#        pass
        #TODO: consertar essa funcao nao existe self.arrowHead ainda
#        path = super(Arrow, self).shape()
#        path.addPolygon(self.arrowHead)
#        return path
#    def mouseMoveEvent(self, event):
#        if self.mode == "editing":
#            self.setPos(self.event.pos())
#            self.update()
        
    def paint(self, painter, option, widget=None):
        pen = self.pen()
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(mmtopt(0.5))
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.black)
        painter.drawLine(self.line())
        #TODO: draw arrow head
        
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
