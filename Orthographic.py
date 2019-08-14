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
Generate a orthographic view.
"""

from PySide import QtGui, QtCore, QtSvg
import FreeCAD, FreeCADGui
from Utils import getGraphicsView

class OrthographicTask:
    """Create and handle orthographic projection task dialog."""
    def __init__(self, graphics_view):
        self.form = FreeCADGui.PySideUic.loadUi(":/ui/task_orthographic.ui")
        self.orthographic = None
        # Handle scene objects
        self.graphics_view = graphics_view
        self.scene = self.graphics_view.scene()
        
    ## DIALOG METHODS ##
    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True
        
    def reject(self):
        self.scene.removeItem(self.orthographic)
        return True #close dialog
        
    def accept(self):
        if True:#self.orthographic:
            import Drawing, Part
            Part.show(Part.makeBox(100,100,100).cut(Part.makeCylinder(80,100)).cut(Part.makeBox(90,40,100)).cut(Part.makeBox(20,85,100)))
            Shape = FreeCAD.ActiveDocument.Shape.Shape
            svg = Drawing.projectToSVG(Shape, FreeCAD.Vector(0, 0, -1))
            item = QtSvg.QGraphicsSvgItem("/home/gabrielantao/Documents/Projetos/Dimensioning_Sandbox/svgteste.svg")#QtGui.QGraphicsPathItem()
            item.setPos(QtCore.QPointF(0, 0))
            item.setScale(2)
            self.scene.addItem(item)
            FreeCAD.Console.PrintMessage("Orthographic projection created.\n")
            return True #close dialog
        return False

    ## SLOTS ##
    
        
    ## METHODS ##
    def connectSlots(self):
        """Connect all slot functions to dialog widgets"""
        pass
    
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        pass
    
    def createOrthographic(self, filepath):
        """Create and add a orthographic projection."""
        pass
    
class OrthographicItem(QtSvg.QGraphicsSvgItem):
    def __init__(self, filepath):
        super(OrthographicItem, self).__init__(filepath)
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setCursor(QtCore.Qt.OpenHandCursor)
    
    def setEditMode(self, value):
        """Edit mode, true when editing (or creating) the image."""
        self.editModeOn = value

    def paint(self, painter, option, widget=None):
        rect = self.boundingRect()
        # Draw rect
        # FIXME: rect should not be affected by scale nor opacity 
        if self.editModeOn: 
            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.DotLine)
            pen.setColor(QtCore.Qt.gray)
            pen.setWidthF(2)
            painter.setPen(pen)
            painter.drawRect(0, 0, rect.width(), rect.height())
        super(OrthographicItem, self).paint(painter, option, widget) 
        

class Orthographic:
    """Feature for a Orthographic Projection in draw."""
    def __init__(self, obj):
        
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass # Let ImageView handle this
    
    def execute(self, obj):
        pass


class OrthographicView:
    """View for a orthographic projection in draw."""
    def __init__(self, vobj, graphics_item):
        self.orthographic = graphics_item
        vobj.Proxy = self
        
    def attach(self, vp):
        # NOTE: it must be done to show coulored icon in tree view 
        # https://forum.freecadweb.org/viewtopic.php?t=12139
        from pivy import coin
        vp.addDisplayMode(coin.SoGroup(), "Standard") 
        # Set feature properties
#        feature = vp.Object
#        feature.File = self.image.filepath
#        feature.Scale = self.image.scale()
#        feature.Rotation = self.image.rotation()
#        feature.Opacity = self.image.opacity()
#        feature.Zvalue = self.image.zValue()
    
    def getGraphicsView(self, vp):
        page = vp.Object.getParentGroup() #feature
        page_view = page.ViewObject.Proxy
        return page_view.graphics_view
    
#    def setEdit(self, mode):
#        #https://www.freecadweb.org/wiki/Std_Edit
#        """Enter in task dialog to edit annotation."""
#        FreeCADGui.Control.showDialog(AnnotationTask(getGraphicsView()))
#        return True
    
    def onDelete(self, vp, subname):
        """Delete the annotation itens."""
        graphics_view = self.getGraphicsView(vp)
        scene = graphics_view.scene()
        scene.removeItem(self.orthographic)
        return True
        
    def doubleClicked(self, vp):
        """Called when double click in object in treeview."""
        page_view = self.getGraphicsView(vp)
        page_view.graphics_view.setActive()
        return True
    
    def onChanged(self, vp, prop):
        """Called when OrthographicView property changes"""
        if prop == "Visibility":
            visibility = vp.getPropertyByName("Visibility")
            self.image.setVisible(visibility)
                
    def updateData(self, fp, prop):
        """Called when Orthographic property changes"""
        pass

    def getIcon(self):
        return ":/icons/orthoviews.svg"
    
    def getDisplayModes(self,obj):
        """Return a list of display modes."""
        return ["Standard"]

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. 
        It must be defined in getDisplayModes."""
        return "Standard"
     
    
class OrthographicCommand:
    """Command for creating Orthographic Projection."""   
    def IsActive(self):
        if FreeCADGui.ActiveDocument == None:
            return False
        return not FreeCADGui.Control.activeDialog()
        
    def Activated(self):  
        graphics_view = getGraphicsView()
        if not graphics_view: # page is not active
            return 
        FreeCADGui.Control.showDialog(OrthographicTask(graphics_view))

    def GetResources(self):
        return {"Pixmap" : ":/icons/orthographic.svg",
                "Accel" : "Shift+O",
                "MenuText": "Orthographic", 
                "ToolTip": "Insert a orthographic projection."}

FreeCADGui.addCommand("Dimensioning_Orthographic", OrthographicCommand())
