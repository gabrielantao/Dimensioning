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
Insert svg image into drawing.
"""

from PySide import QtGui, QtCore, QtSvg
import FreeCAD, FreeCADGui
from Utils import getGraphicsView

class ImageTask:
    """Create and handle image task dialog"""
    def __init__(self, graphics_view):
        self.form = FreeCADGui.PySideUic.loadUi(":/ui/image_task.ui")
        self.svgImage = None
        self.createFileDialog()
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
        self.scene.removeItem(self.svgImage)
        return True #close dialog
        
    def accept(self):
        FreeCAD.Console.PrintMessage("Svg image created.\n")
        if self.svgImage:
            self.svgImage.setEditMode(False)
            self.svgImage.update()
            # TODO: create feature here
            return True #close dialog
        return False

    ## SLOTS ##
    def fileDialogAccepted(self, filepath):
        self.form.path.clear()
        self.form.path.insert(filepath)
        self.createImage(filepath)
        
    ## METHODS ##
    def connectSlots(self):
        """Connect all slot functions to dialog widgets"""
        self.form.scale.valueChanged.connect(self.svgImage.setScale)
        self.form.rotation.valueChanged.connect(self.svgImage.setRotation)
        self.form.opacity.valueChanged.connect(self.svgImage.setOpacity)
        
    
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.scale.valueChanged.disconnect(self.svgImage.setScale)
        self.form.rotation.valueChanged.disconnect(self.svgImage.setRotation)
        self.form.opacity.valueChanged.disconnect(self.svgImage.setOpacity)
    
    # NOTE: initial path should use QStandardPaths::PicturesLocation
    #       Does it work on all systems (Unix, Windows, OSX) ?
    #       (using expanduser)
    def createFileDialog(self):
        import os
        self.dialog = QtGui.QFileDialog(self.form, 
                                        "Open svg image", 
                                        os.path.expanduser("~/Pictures"),
                                        "Scalable Vector Graphics (*.svg)")
        self.form.search.clicked.connect(self.dialog.show)
        self.dialog.fileSelected.connect(self.fileDialogAccepted)
    
    def createImage(self, filepath):
        """Create and add a svg image."""
        pos = QtCore.QPointF(0, 0)
        if self.svgImage:
            pos = self.svgImage.pos()
            self.scene.removeItem(self.svgImage)
            self.disconnectSlots()
        self.svgImage = ImageItem(filepath)
        self.connectSlots()
        scale = self.form.scale.value()
        rotation = self.form.rotation.value()
        opacity = self.form.opacity.value()
        self.svgImage.setPos(pos)
        self.svgImage.setScale(scale)
        self.svgImage.setRotation(rotation)
        self.svgImage.setOpacity(opacity)
        center = self.svgImage.boundingRect().center()
        self.svgImage.setTransformOriginPoint(center)
        self.scene.addItem(self.svgImage)
        
    
class ImageItem(QtSvg.QGraphicsSvgItem):
    def __init__(self, filepath):
        super(ImageItem, self).__init__(filepath)
        self.editModeOn = True
        self.filename = filepath
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setCursor(QtCore.Qt.OpenHandCursor)
    
    def setOpacity(self, opacity):
        """Change opacity."""
        super(ImageItem, self).setOpacity(opacity/100.0)
        
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
        super(ImageItem, self).paint(painter, option, widget) 
        

class Image:
    """Feature for a svg image in draw."""
    def __init__(self, obj):
        self.path = ""
        self.scale = 1.0
   
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, obj):
        FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")


class ImageView:
    """View for a svg image in draw."""
    def __init__(self, vobj):
        vobj.addProperty("App::PropertyFloat", "Opacity", "General",
                         "Image opacity")
        vobj.Proxy = self
        
    def attach(self, vp):
        pass
    
    def onChanged(self, vp, prop):
        pass
                
    def updateData(self, fp, prop):
        pass
    
        
class ImageCommand:
    """Command for creating svg image."""   
    def IsActive(self):
        if FreeCADGui.ActiveDocument == None:
            return False
        return not FreeCADGui.Control.activeDialog()
        
    def Activated(self):  
        graphics_view = getGraphicsView()
        if not graphics_view: # page is not active
            return 
        FreeCADGui.Control.showDialog(ImageTask(graphics_view))
        FreeCAD.ActiveDocument.recompute()

    def GetResources(self):
        return {
            "Pixmap" : ":/icons/image.svg",
            "Accel" : "Shift+I",
            "MenuText": "Image",
            "ToolTip": "Insert a svg image."
            }

FreeCADGui.addCommand("Dimensioning_Image", ImageCommand())
