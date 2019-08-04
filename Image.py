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
        self.image = None
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
        self.scene.removeItem(self.image)
        return True #close dialog
        
    def accept(self):
        if self.image:
            self.image.setEditMode(False)
            self.image.update()
            document = self.graphics_view.getDocument()
            image = document.addObject("App::FeaturePython", "Image")
            Image(image)
            ImageView(image.ViewObject, self.image)
            page = self.graphics_view.getPage()
            page.addObject(image)
            FreeCAD.ActiveDocument.recompute()
            FreeCAD.Console.PrintMessage("Svg image created.\n")
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
        self.form.scale.valueChanged.connect(self.image.setScale)
        self.form.rotation.valueChanged.connect(self.image.setRotation)
        self.form.opacity.valueChanged.connect(self.image.setOpacity)
    
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.scale.valueChanged.disconnect(self.image.setScale)
        self.form.rotation.valueChanged.disconnect(self.image.setRotation)
        self.form.opacity.valueChanged.disconnect(self.image.setOpacity)
    
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
        if self.image:
            pos = self.image.pos()
            self.scene.removeItem(self.image)
            self.disconnectSlots()
        self.image = ImageItem(filepath)
        self.connectSlots()
        scale = self.form.scale.value()
        rotation = self.form.rotation.value()
        opacity = self.form.opacity.value()
        self.image.setPos(pos)
        self.image.setScale(scale)
        self.image.setRotation(rotation)
        self.image.setOpacity(opacity)
        center = self.image.boundingRect().center()
        self.image.setTransformOriginPoint(center)
        self.scene.addItem(self.image)
        
    
class ImageItem(QtSvg.QGraphicsSvgItem):
    def __init__(self, filepath):
        super(ImageItem, self).__init__(filepath)
        self.editModeOn = True
        self.filepath = filepath
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setCursor(QtCore.Qt.OpenHandCursor)
    
    def opacity(self):
        return int(super(ImageItem, self).opacity()*100)
    
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
        obj.addProperty("App::PropertyFile", "File", "General", "File path", 1)
        obj.addProperty("App::PropertyFloat", "Scale", "General",
                         "Image scale")
        obj.addProperty("App::PropertyAngle", "Rotation", "General",
                         "Image rotation")
        obj.addProperty("App::PropertyPercent", "Opacity", "General",
                         "Image opacity")
        obj.addProperty("App::PropertyFloat", "Zvalue", "General",
                         "Image Z-value")
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass # Let ImageView handle this
    
    def execute(self, obj):
        pass


class ImageView:
    """View for a svg image in draw."""
    def __init__(self, vobj, graphics_item):
        self.image = graphics_item
        vobj.Proxy = self
        
    def attach(self, vp):
        # NOTE: it must be done to show coulored icon in tree view 
        # https://forum.freecadweb.org/viewtopic.php?t=12139
        from pivy import coin
        vp.addDisplayMode(coin.SoGroup(), "Standard") 
        # Set feature properties
        feature = vp.Object
        feature.File = self.image.filepath
        feature.Scale = self.image.scale()
        feature.Rotation = self.image.rotation()
        feature.Opacity = self.image.opacity()
        feature.Zvalue = self.image.zValue()
        
    def doubleClicked(self, vp):
        """Called when double click in object in treeview."""
        page = vp.Object.getParentGroup() #feature
        page_view = page.ViewObject.Proxy
        page_view.graphics_view.setActive()
        return True
   
    
    def onChanged(self, vp, prop):
        """Called when ImageView property changes"""
        if prop == "Visibility":
            visibility = vp.getPropertyByName("Visibility")
            self.image.setVisible(visibility)
                
    def updateData(self, fp, prop):
        """Called when Image property changes"""
        if prop == "Scale":
            scale = fp.getPropertyByName("Scale")
            if scale < 0:
                scale = -scale
                fp.Scale = scale
            self.image.setScale(scale)
        elif prop == "Rotation":
            rotation = fp.getPropertyByName("Rotation")
            self.image.setRotation(rotation)
        elif prop == "Opacity":
            opacity = fp.getPropertyByName("Opacity")
            self.image.setOpacity(opacity)
        elif prop == "Zvalue":
            zvalue = fp.getPropertyByName("Zvalue")
            if zvalue < 0:
                zvalue = 0
                fp.Zvalue = 0
            self.image.setZValue(zvalue)

    def getIcon(self):
        return ":/icons/image.svg"
    
    def getDisplayModes(self,obj):
        """Return a list of display modes."""
        return ["Standard"]

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. 
        It must be defined in getDisplayModes."""
        return "Standard"
     
    
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

    def GetResources(self):
        return {"Pixmap" : ":/icons/image.svg",
                "Accel" : "Shift+I",
                "MenuText": "Image", 
                "ToolTip": "Insert a svg image."}

FreeCADGui.addCommand("Dimensioning_Image", ImageCommand())
