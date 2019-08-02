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
GraphicsView for page 
"""
from PySide import QtCore, QtGui, QtSvg
import FreeCAD, FreeCADGui


class PageScene(QtGui.QGraphicsScene):
    """This class handles page graphics scene"""
    mousePressSignal = QtCore.Signal(QtGui.QGraphicsSceneMouseEvent)
    keyPressSignal = QtCore.Signal(QtGui.QGraphicsSceneMouseEvent)
    def __init__(self):
        super(PageScene, self).__init__()
        # TODO: colocar aqui a configuracao da cena?
        
    def mousePressEvent(self, event):
        """Send mouse press event to command handlers"""
        self.mousePressSignal.emit(event)
        super(PageScene, self).mousePressEvent(event)

    def keyReleaseEvent(self, event):
        """Send key press event to command handlers"""
        self.keyPressSignal.emit(event)
        super(PageScene, self).keyReleaseEvent(event)


class PageGraphicsView(QtGui.QGraphicsView):
    """This class handles page graphics view"""
    def __init__(self, template="/home/gabrielantao/.FreeCAD/Mod/Dimensioning/Resources/templates/A4_Landscape.svg"):
        QtGui.QGraphicsView.__init__(self)
        self.setScene(PageScene())
        # TODO: Inserir o icone da pagina aqui 
#        import Dimensioning_rc
#        self.setWindowIcon(QtGui.QIcon(":/icons/page.svg"))
        #TODO: a pagina deve ser so deslocada com as setas do teclado,
        #      com scroolbar ou com atalho CTRL (aparece maozinha) e clique do mouse
        #      reservar a mao para deslocar as views da pagina 
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
#        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.setBackgroundBrush(brush)
        scene = self.scene()
        scene.clear()
        self.resetTransform()
        # create drawing paper 
        self.m_svgItem = QtSvg.QGraphicsSvgItem(template)
        self.m_svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.m_svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.m_svgItem.setZValue(0)
        # create paper background 
        rect = self.m_svgItem.boundingRect()
        self.m_backgroundItem = QtGui.QGraphicsRectItem(rect)
        self.m_backgroundItem.setBrush(QtGui.QColor(255, 255, 255))
        self.m_backgroundItem.setPen(QtCore.Qt.NoPen)
        self.m_backgroundItem.setVisible(True) #NOTA: precisa disso?
        self.m_backgroundItem.setZValue(-1)
        scene.addItem(self.m_backgroundItem)
        scene.addItem(self.m_svgItem)
        # attach widget to FreeCAD MDI
        mw =  FreeCADGui.getMainWindow()
        mdi = mw.centralWidget()
        mdi.addSubWindow(self)   
        self.show() #https://forum.freecadweb.org/viewtopic.php?t=9892
        self.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.nome = "Pagine"
        
    def setPageTitle(self, title):
        doc_name = FreeCAD.ActiveDocument.Label
        self.setWindowTitle("{} : {}".format(doc_name, title))
    
    def wheelEvent(self, event):
        delta = event.delta()
        factor = pow(1.2, delta / 240.0)
        self.scale(factor, factor)
        event.accept()
        
    def closeEvent(self,event):
        event.ignore() #dont close

