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
Based on DrawingView.cpp and DrawingView.h
https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Drawing/Gui/DrawingView.cpp
https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Drawing/Gui/DrawingView.h
"""

from PySide import QtCore, QtGui, QtSvg
from FreeCADGui import MDIView

class SvgView(QtGui.QGraphicsView):
    """Insert visualization of page."""
    def __init__(self, parent):
        QtGui.QGraphicsView.__init__(self, parent)
        
        self.m_renderer = None
        self.m_svgItem = None #QGraphicsItem
        self.m_backgroundItem = None #QGraphicsRectItem
        self.m_outlineItem = None #QGraphicsRectItem
        self.m_image = None #QImage
        self.m_invertZoom = False 
        
        self.setScene(QtGui.QGraphicsScene(self))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.setBackgroundBrush(brush)
        
    def drawBackground(self, painter, rect):
        #"If all you want is to define a color, texture or gradient for the background, you can call PySide.QtGui.QGraphicsView.setBackgroundBrush() instead."
        # https://srinikom.github.io/pyside-docs/PySide/QtGui/QGraphicsView.html#PySide.QtGui.PySide.QtGui.QGraphicsView.drawBackground
        pass
    
    def openFile(self, filename):
        #TODO: verificar aqui se o arquivo existe
        scene = self.scene()
        scene.clear()
        self.resetTransform()
        # create drawing paper 
        self.m_svgItem = QtSvg.QGraphicsSvgItem(filename)
        self.m_svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.m_svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.m_svgItem.setZValue(0)
        # create paper background 
        rect = self.m_svgItem.boundingRect()
        m_backgroundItem = QtGui.QGraphicsRectItem(rect)
        m_backgroundItem.setBrush(QtGui.QColor(255, 255, 255))
        m_backgroundItem.setPen(QtCore.Qt.NoPen)
        m_backgroundItem.setVisible(True) #NOTA: precisa disso?
        m_backgroundItem.setZValue(-1)
        #TODO: add here outline
        # add itens to scene
        scene.addItem(self.m_backgroundItem)
        scene.addItem(self.m_svgItem)
        #scene.setSceneRect(self.m_outlineItem.boundingRect())
        
    def setRenderer(self, renderer_name):
        self.setViewport(QtGui.QWidget())
    
    def setHighQualityAntialiasing(highQualityAntialiasing):
        pass
    
    def setViewBackground(enable):
        pass
    
    def setViewOutline(enable):
        pass
    
    def paintEvent(self, event):
        QtGui.QGraphicsView.paintEvent(event)
    
    def wheelEvent(self, event):
        pass


    
class DrawingView(MDIView):
    def __init__(self, document, parent):
        MDIView.__init__(self, document, parent)
        self.m_view = SvgView(self) #NOTA: seria parent ou self mesmo???
        self.setCentralWidget(self.m_view)
    
        self.m_orientation = QtGui.QPrinter.Landscape 
        self.m_pageSize = QtGui.QPrinter.A4
    
    def load(self, filename):
        #TODO: testa se arquivo existe, se nao existe desabilita o fundo e  outline
        self.m_view.openFile(filename)
        #TODO: pega o nome do arquivo
        self.m_currentPath = filename
        self.findPrinterSettings("") #TODO: substitui "" por nome do arquivo
        
    def findPrinterSettings(self, filename):
        #TODO: pegar o tipo partrait ou landscape 
        #      pegar o tipo de papel A0, A1,A2... pelo xml do arquivo (ou pelo nome)
        pass
    
    def setDocumentObject(self, name):
        self.objectName = name
      
    def closeEvent(self, event):
        #TODO: implementar
        pass
    
#    def onMsg(pMsg):
#        return False
#    def onHasMsg(pMsg):
#        return False 
    
    def onRelabel(self, pDoc):
        #TODO: implementar 
        self.setWindowTitle("DRAW1")
        
    def printPDF(self):
        pass #NOTA: ver todas os metodos associados
    
    def printPreview():
        pass
    
    def print_(printer):
        pass #NOTA: HA DUAS FUNCOES ASSIM!!!
    
    def getPageSize(w, h):
        pass
    
    def viewAll(self):
        self.m_view.fitInView(self.m_view.scene().sceneRect(), 
                              QtCore.Qt.KeepAspectRatio)

   