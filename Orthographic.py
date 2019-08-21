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
from SvgParser import svgParser
import Drawing

from math import pi as PI

class OrthographicTask:
    """Create and handle orthographic projection task dialog."""
    def __init__(self, graphics_view):
        self.form = FreeCADGui.PySideUic.loadUi(":/ui/task_orthographic.ui")
        self.orthographic_views = {} #item groups (view frames)
        self.parts = [] #parts to be drawn
        # Handle scene objects
        self.graphics_view = graphics_view
        self.scene = self.graphics_view.scene()
        self.scene.keyPressSignal.connect(self.keyPress)
#        self.front_center = self.scene.sceneRect().center()
        self.connectSlots()
        # Populate PartList
        root_obj = self.graphics_view.getDocument().RootObjects
        self.createTreeWidget(root_obj, self.form.treeWidget)
        # TODO: review this form to configure
        self.setPlane(0)
        self.setDirection(0)
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
        for view in self.orthographic_views.values():
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
    
    def setPlane(self, index):
        """Plane where shape must be projected."""
        self.plane = self.form.projection_plane.currentText()
        self.drawOrthographic()
        
    def setDirection(self, index):
        """Direction where eyes look to."""
        if self.form.projection_direction.currentText() == "Positive Direction":
            self.front_direction = FreeCAD.Vector(0, 0, -1)
        elif self.form.projection_direction.currentText() == "Negative Direction":
            self.front_direction = FreeCAD.Vector(0, 0, 1)
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
                if len(self.parts) == 1: #if I had 0 selected
                    self.drawOrthographic(True)
                    return
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
        self.form.projection_plane.currentIndexChanged.connect(self.setPlane)
        self.form.projection_direction.currentIndexChanged.connect(self.setDirection)
        self.form.treeWidget.itemChanged.connect(self.changeParts)
        self.form.show_hidden.stateChanged.connect(self.changeHidden) 
        self.form.show_smooth.stateChanged.connect(self.changeSmooth)
        
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.projection_plane.currentIndexChanged.disconnect(self.setPlane)
        self.form.projection_direction.currentIndexChanged.disconnect(self.setDirection)
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

    def drawOrthographic(self, center_scene=False):
        """Create and add a orthographic projection items."""
        document = self.graphics_view.getDocument()
        for view in self.orthographic_views.values():
            self.scene.removeItem(view)
        if len(self.orthographic_views) > 0 and center_scene == False:
            pos = self.orthographic_views["Front"].pos()
        self.orthographic_views = {}
        if len(self.parts) == 0:
            return
        
        elif len(self.parts) == 1:
            shape = document.getObjectsByLabel(self.parts[0])[0].Shape
            # # # 
            #TODO: reposicionar esse trecho de codigo depois dos ifs para evitar repeticao 
            paths, vertices = self.getView(shape)
            view = OrthographicItem(paths, vertices)
            self.scene.addItem(view)
            view.drawView(self.scene)
            view.flipVertical()
            self.orthographic_views["Front"] = view
            # # #
        elif len(self.parts) > 1:
            shape = document.getObjectsByLabel(self.parts[0])[0].Shape
            for part in self.parts[1:]:
                next_shape = document.getObjectsByLabel(part)[0].Shape
                shape = shape.fuse(next_shape) #make a union with shapes
            paths, vertices = self.getView(shape)
            view = OrthographicItem(paths, vertices)
            self.scene.addItem(view)
            view.drawView(self.scene)
            view.flipVertical()
            self.orthographic_views["Front"] = view
        if center_scene:
            center = self.scene.sceneRect().center()
            self.orthographic_views["Front"].centralize(center)
        else: 
            self.orthographic_views["Front"].setPos(pos)
        # TODO: recalcula a posicao de todas as vistas    
        # TODO: pega as direcoes a serem projetadas e gera cada view
      
    def getView(self, shape, direction="Front"):
        """Return lines checked in task dialog.
        direction is view direction (Front, Right, Top...)
        Projection are made always over xy plane (z direction), shapes are 
        rotated 90° and then projected. 
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
        paths = {"visible": [], "hidden": []}
        vertices = []
        edge_visible = [True, self.show_smooth, False, True, False] 
        edge_hidden = [self.show_hidden, 
                       True if self.show_hidden and self.show_smooth else False, 
                       False, 
                       True if self.show_hidden else False, 
                       False] 
        # Change projection plane
        if self.plane == "XZ":
            matrix = FreeCAD.Base.Matrix()
            matrix.rotateX(PI/2)
            matrix.rotateZ(PI/2)
            shape = shape.transformGeometry(matrix)
        elif self.plane == "YZ":
            matrix = FreeCAD.Base.Matrix()
            matrix.rotateY(-PI/2)
            matrix.rotateZ(-PI/2)
            shape = shape.transformGeometry(matrix)
        # TODO: VERIFICAR A DIREACO CERTA PARA O REAR 
        #      dependendo vai ser valor de -180° ou 180°
        # TODO: Acrescentar first angle
        # Generate required view
        rotate = {"Third Angle": {"Front": lambda m: None, 
                                  "Rear": lambda m: m.rotateY(PI),
                                  "Left": lambda m: m.rotateY(PI/2),
                                  "Right": lambda m: m.rotateY(-PI/2),
                                  "Top": lambda m: m.rotateX(PI/2),
                                  "Bottom": lambda m: m.rotateX(-PI/2)}}
        matrix = FreeCAD.Base.Matrix()
        rotate["Third Angle"][direction](matrix)
        shape = shape.transformGeometry(matrix) #rotated shape
        shape_list = Drawing.projectEx(shape, self.front_direction)
        shape_visible = shape_list[:5]
        shape_hidden = shape_list[5:]
        for edge, shape in zip(edge_visible, shape_visible):
            if edge:
                svg = Drawing.projectToSVG(shape, self.front_direction)
                path, vertex = svgParser(svg) #lists
                paths["visible"].extend(path)
                vertices.extend(vertex)
        for edge, shape in zip(edge_hidden, shape_hidden):
            if edge:
                svg = Drawing.projectToSVG(shape, self.front_direction)
                path, vertex = svgParser(svg) #lists
                paths["hidden"].extend(path)
                vertices.extend(vertex)
        return (paths, vertices)

    def configLines(self, view, hidden=False, thick=0.35):
        """Configure view hidden, tickness and color line."""
        pass
    
    def configViews(self):
        """Configure all Views"""
        pass

# TODO: alterar esse nome para OrthographicItemGroup ou algo assim
class OrthographicItem(QtGui.QGraphicsItemGroup):
    """Group all paths in a view"""
    def __init__(self, paths, vertices, **config):
        super(OrthographicItem, self).__init__(parent=None, scene=None)
        self.editModeOn = False
        self.visible_lines = paths["visible"]
        self.hidden_lines = paths["hidden"]
        self.addItems(self.visible_lines)
        self.addItems(self.hidden_lines)
#        self.configVisible(config)
#        self.configHidden(config)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
#        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setCursor(QtCore.Qt.OpenHandCursor)
    
    def setEditMode(self, value):
        """Edit mode, true when editing (or creating) the image."""
        self.editModeOn = value
    
#    def boundingRect(self):
#        margin=10
#        rect = super(OrthographicItem, self).boundingRect()
#        rect.adjust(-self.margin, -self.margin, self.margin, self.margin)
#        return rect
    
    def addItems(self, items):
        """Add a list of items to group."""
        for item in items:
            self.addToGroup(item)

    def removeItems(self, items):
        """Remove a list of items from group."""
        for item in items:
            self.removeFromGroup(item)
            
    def flipVertical(self):
        """Flip the group verticaly."""
        pos = self.pos()
        self.scale(1,-1)
        self.setPos(pos) #ensure same position
        
    def centralize(self, pos):
        """Center group at pos."""
        rect = self.boundingRect()
        rect.moveCenter(pos)
        self.setPos(rect.topLeft())
    
    def drawView(self, scene):
        """Draw lines in view."""
        # NOTE: hidden first because visible should overlap hidden
        for path in self.hidden_lines:
            path.setHidden()
            scene.addItem(path)
        for path in self.visible_lines:
            scene.addItem(path)
            
    # TODO: implementar configuracao de espessura e cor
    def configVisible(self, config):
        pass
    
    def configHidden(self, config):
        pass
    
    #TODO: implementar esse metodo 
#    def paint(self, painter, option, widget=None):
#        rect = self.boundingRect()
#        # Draw rect
#        # FIXME: rect should not be affected by scale
#        if self.editModeOn == False: 
#            pen = QtGui.QPen()
#            pen.setStyle(QtCore.Qt.DotLine)
#            pen.setColor(QtCore.Qt.gray)
#            pen.setWidthF(2)
#            painter.setPen(pen)
#            painter.drawRect(0, 0, rect.width(), rect.height())
#        super(OrthographicItem, self).paint(painter, option, widget) 
        

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
