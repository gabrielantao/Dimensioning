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

import Drawing

from GraphicItem import ViewGroup, PathItem
from SvgParser import svgParser



#FIXME: CRITICAL! Sometimes this task crashes FreeCAD
class OrthographicTask:
    """Create and handle orthographic projection task dialog."""
    def __init__(self, graphics_view):
        self.form = FreeCADGui.PySideUic.loadUi(":/ui/task_orthographic.ui")
        self.orthographic_views = [] #item groups (view frames) TODO: transformar dict
        self.parts = [] #parts to be drawn
        # Handle scene objects
        self.graphics_view = graphics_view
        self.scene = self.graphics_view.scene()
        self.scene.keyPressSignal.connect(self.keyPress)
        self.connectSlots()
        # Populate PartList
        root_obj = self.graphics_view.getDocument().RootObjects
        self.createTreeWidget(root_obj, self.form.treeWidget)
        # TODO: review this form to configure
        self.setFrontPlane("")
        self.changeHidden(QtCore.Qt.Unchecked)
        self.changeSmooth(QtCore.Qt.Unchecked)
        
    ## DIALOG METHODS ##
    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True
        
    def reject(self):
        for view in self.orthographic_views:
            self.scene.removeItem(view) #TODO: reescreve isso
        self.disconnectSlots()
        return True #close dialog
        
    def accept(self):
        if len(self.orthographic_views) > 0:
#            if 
            #TODO: levanta erro se o objeto trocou o nome ou foi deletado
#            import Drawing, Part
#            Part.show(Part.makeBox(100,100,100).cut(Part.makeCylinder(80,100)).cut(Part.makeBox(90,40,100)).cut(Part.makeBox(20,85,100)))
#            Shape = FreeCAD.ActiveDocument.Shape.Shape
#            svg = Drawing.projectToSVG(Shape, FreeCAD.Vector(0, 0, -1))
#            item = QtSvg.QGraphicsSvgItem("/home/gabrielantao/Documents/Projetos/Dimensioning_Sandbox/svgteste.svg")#QtGui.QGraphicsPathItem()
#            item.setPos(QtCore.QPointF(0, 0))
#            item.setScale(2)
#            self.scene.addItem(item)
#            FreeCAD.Console.PrintMessage("Orthographic projection created.\n")
            self.disconnectSlots()
            return True #close dialog
        return False

    ## SLOTS ##
    def keyPress(self, event):
        if event.key() == QtCore.Qt.Key_Escape: #close
            self.reject()
            FreeCADGui.Control.closeDialog()
            
    def setFrontPlane(self, text):
        plane = {"XY": FreeCAD.Vector(0, 0, 1),
                 "XZ": FreeCAD.Vector(0, 1, 0),
                 "YZ": FreeCAD.Vector(1, 0, 0)}
        self.front_direction = plane[self.form.projection_plane.currentText()]
        if self.form.projection_direction.currentText() == "Negative":
            self.front_direction *= -1     
        self.drawOrthographic()
    
    def changeParts(self, item, column):
        """Handle treeview changes. Add or remove part names from part list."""
        document = self.graphics_view.getDocument()
        label = item.text(column)
        obj = document.getObjectsByLabel(label)
        if len(obj) == 0: #object not found
            msgBox = QtGui.QMessageBox(FreeCADGui.getMainWindow())
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            msgBox.setText("The object {} has been missed.".format(label))
            msgBox.setInformativeText("Maybe this object was deleted or it was relabeled recently.\n" + \
                                      "You should reopen this task dialog.")
            msgBox.show()
            if label in self.parts:
                self.parts.remove(label)
        # NOTE: Save label (string) ensure that I always have the reference.
        #       Labels are forced to be unique in a document.
        else:
            if obj[0].TypeId.split("::")[1] == "DocumentObjectGroup":
                return
            if item.checkState(0) == QtCore.Qt.Checked:
                self.parts.append(label)
            elif item.checkState(0) == QtCore.Qt.Unchecked:
                if label in self.parts:
                    self.parts.remove(label)
        self.drawOrthographic()
    
    def changeHidden(self, state):
        """When some edge visible or hidden line checkebox change state."""
        self.show_hidden = True if state == QtCore.Qt.Checked else False
        self.drawOrthographic()
        
    def changeSmooth(self, state):
        self.show_smooth = True if state == QtCore.Qt.Checked else False
        self.drawOrthographic()
        
    ## METHODS ##
    def connectSlots(self):
        """Connect all slot functions to dialog widgets"""
        self.form.projection_plane.currentIndexChanged.connect(self.setFrontPlane)
        self.form.projection_direction.currentIndexChanged.connect(self.setFrontPlane)
        self.form.treeWidget.itemChanged.connect(self.changeParts)
        self.form.show_hidden.stateChanged.connect(self.changeHidden) 
        self.form.show_smooth.stateChanged.connect(self.changeSmooth)
        
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.projection_plane.currentIndexChanged.disconnect(self.setFrontPlane)
        self.form.projection_direction.currentIndexChanged.disconnect(self.setFrontPlane)
        self.form.treeWidget.itemChanged.disconnect(self.changeParts)
        self.form.show_hidden.stateChanged.disconnect(self.changeHidden) 
        self.form.show_smooth.stateChanged.disconnect(self.changeSmooth)
        
    def createTreeWidget(self, objects, parent):
        """Add tree items recursively."""
        for part in objects:
            if part.TypeId.split("::")[0] == "Part" or part.TypeId.split("::")[0] == "PartDesign":
                item = QtGui.QTreeWidgetItem(parent)
                item.setText(0, part.Label)
                item.setIcon(0, part.ViewObject.Icon)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(0, QtCore.Qt.Unchecked)
            if part.TypeId.split("::")[1] == "DocumentObjectGroup":
                item = QtGui.QTreeWidgetItem(parent)
                item.setText(0, part.Label)
                item.setIcon(0, part.ViewObject.Icon)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
                item.setCheckState(0, QtCore.Qt.Unchecked)
                self.createTreeWidget(part.Group, item) #make recursive iter

    def drawOrthographic(self):
        """Create and add a orthographic projection items."""
        document = self.graphics_view.getDocument()
        for group in self.orthographic_views:
            self.scene.removeItem(group)
        self.orthographic_views = []
        if len(self.parts) == 1:
            shape = document.getObjectsByLabel(self.parts[0])[0].Shape
            paths, vertices = self.getView(shape)
            for path in paths:
                self.scene.addItem(path)
            group = ViewGroup(paths)
            self.scene.addItem(group)
            #TODO: move group para centro da pagina se for a frontal 
#            group.centralize(self.scene) 
#            self.vertices = vertices
            self.orthographic_views.append(group)
        elif len(self.parts) > 1:
            shape = document.getObjectsByLabel(self.parts[0])[0].Shape
            for part in self.parts[1:]:
                next_shape = document.getObjectsByLabel(part)[0].Shape
                shape = shape.fuse(next_shape) #make a union with shapes
            paths, vertices = self.getView(shape)
            for path in paths:
                self.scene.addItem(path)
            group = ViewGroup(paths)
            self.scene.addItem(group)
        # TODO: pega as direcoes a serem projetadas e gera cada view
      
    def getView(self, shape, direction="Front"):
        """Return lines checked in task dialog.
        direction is view direction (Front, Right, Top...)
        - VISIBLE
        V   hard edge 
        V1  smooth edges 
        VN  contour edges 
        VO  contours apparents 
        VI  isoparametric 
        
        - HIDDEN
        H   hard edge 
        H1  smooth edges 
        HN  contour edges 
        HO  contours apparents 
        HI  isoparametric
        """
        paths = []
        vertices = []
        edge_visible = [True,  
                        self.show_smooth,
                        False, 
                        True,  
                        False] 
        edge_hidden = [self.show_hidden, 
                       True if self.show_hidden and self.show_smooth else False, 
                       False, 
                       True if self.show_hidden else False, 
                       False] 
        #TODO: checar direcao, checa projection angle
        #      usar no lugar desse vetor constante
        shape_list = Drawing.projectEx(shape, FreeCAD.Vector(0, 0, 1))
        shape_visible = shape_list[:5]
        shape_hidden = shape_list[5:]
        # NOTE: hidden first because visible should overlap hidden
        for edge, shape in zip(edge_hidden, shape_hidden):
            if edge:
                svg = Drawing.projectToSVG(shape, FreeCAD.Vector(0, 0, 1))
                path, vertex = svgParser(svg, True) 
                paths.extend(path)
                vertices.extend(vertex)
        for edge, shape in zip(edge_visible, shape_visible):
            if edge:
                svg = Drawing.projectToSVG(shape, FreeCAD.Vector(0, 0, 1))
                path, vertex = svgParser(svg)
                paths.extend(path)
                vertices.extend(vertex)
        return (paths, vertices)

    
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
