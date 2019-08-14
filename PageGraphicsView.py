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
    def __init__(self, template):
        super(PageScene, self).__init__()
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.setBackgroundBrush(brush)
        self.clear()
        # Create drawing paper 
        self.m_svgItem = QtSvg.QGraphicsSvgItem(template)
        self.m_svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.m_svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.m_svgItem.setZValue(0)
        # Create paper background 
        rect = self.m_svgItem.boundingRect()
        self.m_backgroundItem = QtGui.QGraphicsRectItem(rect)
        self.m_backgroundItem.setBrush(QtGui.QColor(255, 255, 255))
        self.m_backgroundItem.setPen(QtCore.Qt.NoPen)
        self.m_backgroundItem.setZValue(-1)
        # Add items
        self.addItem(self.m_backgroundItem)
        self.addItem(self.m_svgItem)
        
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
        super(PageGraphicsView, self).__init__()
        self.setScene(PageScene(template))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.resetTransform()
        # Attach widget to FreeCAD MDI
        mw =  FreeCADGui.getMainWindow()
        mdi = mw.centralWidget()
        mdi.addSubWindow(self)   
        # Set active document when subwindow is active
        self.document_name = FreeCAD.ActiveDocument.Name
        def setActiveDocument():
            FreeCAD.setActiveDocument(self.document_name)
        subwindow = self.parentWidget()
        subwindow.aboutToActivate.connect(setActiveDocument)
        self.show() #https://forum.freecadweb.org/viewtopic.php?t=9892
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)
        subwindow.setWindowIcon(QtGui.QIcon(":/icons/window_icon.svg"))

    # NOTE: This could be used to build a name just like Drawing WB does...
    #       "Doc_name : Page". However, new workbenchs like Spreadsheet
    #       and Techdraw give just the name of Feature to MDI title.    
    #       This method probably won't be used anymore.
    def setPageTitle(self, title):
        doc_name = FreeCAD.ActiveDocument.Label
        self.setWindowTitle("{} : {}".format(doc_name, title))

    def setActive(self):
        mw =  FreeCADGui.getMainWindow()
        mdi = mw.centralWidget()
        mdi.setActiveSubWindow(self.parentWidget())
        
    def getDocument(self):
        """Get page's document."""
        return FreeCAD.getDocument(self.document_name)
    
    def getPage(self):
        """Get page object."""
        document = FreeCAD.getDocument(self.document_name)
        return document.getObject(self.windowTitle())
    
    def wheelEvent(self, event):
        delta = event.delta()
        factor = pow(1.2, delta / 240.0)
        self.scale(factor, factor)
        event.accept()
        
    def closeEvent(self,event):
        event.ignore() #dont close

