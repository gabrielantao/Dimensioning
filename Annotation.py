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
Local notes to drawing.
"""

from PySide import QtGui, QtCore
import FreeCAD, FreeCADGui
from Utils import getGraphicsView, mmtopt, setButtonColor

from GraphicItem import Arrow, PointCatcher
### TODO LIST
# () implement text horizontal alignment 
# () implement functionality to delete arrows (delete button)
# () implement "save as default" functionality
# () criar feature e view 

class AnnotationTask:
    """Create and handle annotation task dialog"""
    # https://mandeep7.wordpress.com/2017/05/07/using-qt-ui-files-with-pyside-in-freecad/
    INSERT_MODE, EDIT_MODE = range(2)
    def __init__(self, graphics_view):
        self.mode = self.INSERT_MODE
        self.annotation_item = None
        self.form = FreeCADGui.PySideUic.loadUi(":/ui/annotation_task.ui")
        self.form.font_family.setCurrentFont(QtGui.QFont("ISO 3098"))
        setButtonColor(self.form.font_color_button, QtGui.QColor(0, 0, 0, 255))
        self.createColorDialog()
        self.createSymbolButton()
#        self.form.default_button.clicked.connect(a) #TODO: implementar salvar como padrao
#        self.setDefaultConfig()
        # Handle scene objects
        self.graphics_view = graphics_view
        self.changeCursor(QtCore.Qt.PointingHandCursor)
        self.scene = self.graphics_view.scene()
        self.scene.mousePressSignal.connect(self.mousePress)
        self.scene.keyPressSignal.connect(self.keyPress)
    
    ## DIALOG METHODS ##
    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True
        
    def getStandardButtons(self):
        """Config only close button"""
        #https://forum.freecadweb.org/viewtopic.php?t=11801
        return QtGui.QDialogButtonBox.Close 
    
    def clicked(self, index):
        """Called when close dialog button is clicked. Exit annotation command."""
        self.scene.mousePressSignal.disconnect(self.mousePress)
        self.scene.keyPressSignal.disconnect(self.keyPress)
        self.changeCursor(QtCore.Qt.ArrowCursor)
        if self.mode == self.EDIT_MODE:
            self.scene.removeItem(self.annotation_item)
            for arrow in self.annotation_item.arrows:
                self.scene.removeItem(arrow)
            for catcher in self.annotation_item.point_catchers:
                self.scene.removeItem(catcher)
   
    ## SLOTS ##
    def mousePress(self, event):
        """Handle the mouse press event inside scene"""
        # FIXME: When click over another item the cursor doesn't change to arrowcursor
        pos = event.scenePos()
        if self.mode == self.INSERT_MODE:
            self.mode = self.EDIT_MODE
            self.annotation_item = AnnotationItem()
            self.connectSlots()
            self.configFont()
            self.configLeaderLine()
            self.annotation_item.setPos(pos)
            self.scene.addItem(self.annotation_item)
        self.changeCursor(QtCore.Qt.ArrowCursor)
     
    def keyPress(self, event):
        """Handle the key press event inside scene"""
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return: 
            if self.form.text_widget.toPlainText().strip() == "":
                QtGui.QMessageBox.warning(self.form, "Dimensioning Workbench",
                                          "Text should not be empty.")
                return
            if self.mode == self.EDIT_MODE:
                self.mode = self.INSERT_MODE
                FreeCAD.Console.PrintMessage("Text added.\n")
                self.annotation_item.setEditMode(False) 
                for catcher in self.annotation_item.point_catchers:
                    self.scene.removeItem(catcher)
                self.annotation_item.update()
                self.disconnectSlots()
                self.annotation_item = None
                self.changeCursor(QtCore.Qt.PointingHandCursor)
        
    def colorDialogAccepted(self, color):
        """Slot cancel color dialog. Reset actual color."""
        setButtonColor(self.form.font_color_button, color)
        self.form.font_color_lineEdit.clear()
        self.form.font_color_lineEdit.insert(str(color.getRgb()).strip("()"))
    
    def colorDialogRejected(self):
        """Slot to return color to color before open color dialog."""
        colorRGBA = map(int, self.form.font_color_lineEdit.text().split(","))
        color = QtGui.QColor(*colorRGBA)
        self.annotation_item.setFontColor(color)
    

    def fontChanged(self, font):
        """Set new font when it has changed."""
        size = self.form.font_size.value() 
        self.annotation_item.setFont(font)
        self.annotation_item.setFontSize(size) #ensure same size
        
    def textChanged(self):
        """Set new text when it has changed."""
        text = self.form.text_widget.toPlainText()
        self.annotation_item.setText(text)
        for arrow in self.annotation_item.arrows:
            self.annotation_item.setPivot(arrow)
    
    def createArrow(self):
        """Add arrow to scene."""
        self.annotation_item.addArrow()
        self.scene.addItem(self.annotation_item.arrows[-1])
        self.scene.addItem(self.annotation_item.point_catchers[-1])
        
    ## METHODS ##
    def connectSlots(self):
        """Connect all slot functions to dialog widgets"""
        self.form.font_family.currentFontChanged.connect(self.fontChanged)
        self.form.font_size.valueChanged.connect(self.annotation_item.setFontSize)
        self.form.text_widget.textChanged.connect(self.textChanged)
        self.dialog.currentColorChanged.connect(self.annotation_item.setFontColor)
        self.dialog.rejected.connect(self.colorDialogRejected)
        self.form.orientation_angle.valueChanged.connect(self.annotation_item.setRotation)
        self.form.leader_add.clicked.connect(self.createArrow)
        self.form.leader_type.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_side.currentIndexChanged.connect(self.configLeaderLine)
        self.form.horizontal_align.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_valign.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_head.currentIndexChanged.connect(self.configLeaderLine)
    
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.font_family.currentFontChanged.disconnect(self.fontChanged)
        self.form.font_size.valueChanged.disconnect(self.annotation_item.setFontSize)
        self.form.text_widget.textChanged.disconnect(self.textChanged)
        self.dialog.currentColorChanged.disconnect(self.annotation_item.setFontColor)
        self.dialog.rejected.disconnect(self.colorDialogRejected)
        self.form.orientation_angle.valueChanged.disconnect(self.annotation_item.setRotation)
        self.form.leader_add.clicked.disconnect(self.createArrow)
        self.form.leader_type.currentIndexChanged.disconnect(self.configLeaderLine)
        self.form.leader_side.currentIndexChanged.disconnect(self.configLeaderLine)
        self.form.horizontal_align.currentIndexChanged.disconnect(self.configLeaderLine)
        self.form.leader_valign.currentIndexChanged.disconnect(self.configLeaderLine)
        self.form.leader_head.currentIndexChanged.disconnect(self.configLeaderLine)
    
    def changeCursor(self, cursor):
        """Change mouse cursor denpending on mode."""
        self.graphics_view.viewport().setCursor(cursor)
        
    # NOTE: This following two methods can be reimplemented as inherited methods. 
    def saveDefaultConfig(self):
        """Save default configs as a json temporary file. 
        Each document has its own configs"""
        import json
        UID = FreeCAD.ActiveDocument.Uid
        default_config = {}
        # TODO: get actual configs from widgets here
        with open("/Temp/Annotation_{}".format(UID), "w") as config:
            config.write(json.dumps(default_config, indent=4, sort_keys=True))
    
    def setDefaultConfig(self):
        """Set default confis from json temp file"""
        import os, json
        UID = FreeCAD.ActiveDocument.Uid
        if os.path.exists("/Temp/Annotation_{}".format(UID)):
            with open("/Temp/Annotation_{}".format(UID), "r") as config:
                default_config = json.load(config)
            #TODO: configure here all widgets 
    
    def configFont(self):
        """Configure font."""
        font = self.form.font_family.currentFont()
        size = self.form.font_size.value()
        colorRGBA = map(int, self.form.font_color_lineEdit.text().split(","))
        color = QtGui.QColor(*colorRGBA)
        text = self.form.text_widget.toPlainText()
        angle = self.form.orientation_angle.value()
        self.annotation_item.setFont(font)
        self.annotation_item.setFontSize(size)
        self.annotation_item.setFontColor(color)
        self.annotation_item.setText(text)
        self.annotation_item.setRotation(angle)
        
    def configLeaderLine(self, index=0):
        """Configure leader line."""
        type_ = self.form.leader_type.currentText()
        side = self.form.leader_side.currentText()
        halign = self.form.horizontal_align.currentText()
        valign = self.form.leader_valign.currentText()
        head = self.form.leader_head.currentText()
        self.annotation_item.configAnnotation(type_=type_, 
                                              side=side, halign=halign,
                                              valign=valign, head=head)

    def createColorDialog(self):
        """Create a new dialog for color."""
        color = map(int, self.form.font_color_lineEdit.text().split(","))
        color = QtGui.QColor(*color)
        self.dialog = QtGui.QColorDialog(color, self.form)
        self.dialog.setOption(QtGui.QColorDialog.ShowAlphaChannel)
        self.dialog.colorSelected.connect(self.colorDialogAccepted)
        self.form.font_color_button.clicked.connect(self.dialog.show)
    
    # TODO: In future, change this for a button to a character map.
    # https://doc.qt.io/qt-5/qtwidgets-widgets-charactermap-example.html    
    def createSymbolButton(self):
        """Create a symbol toolbutton menu"""
        import Dimensioning_rc
        def insert_symbol(unicode_):
            def func():
                return self.form.text_widget.insertPlainText(unicode_)
            return func
        symbol_list = [[":/symbols/registered.svg", "Registered", u"\u00AE"], 
                       [":/symbols/plus_minus.svg", "Plus-Minus", u"\u00B1"],
                       [":/symbols/one_quarter.svg", "One Quarter", u"\u00BC"], 
                       [":/symbols/one_half.svg", "One Half", u"\u00BD"],
                       [":/symbols/three_quarters.svg", "Three Quarters", u"\u00BE"], 
                       [":/symbols/one_eighth.svg", "One Eighth", u"\u215B"], 
                       [":/symbols/three_eighths.svg", "Three Eighths", u"\u215C"], 
                       [":/symbols/five_eighths.svg", "Five Eighths", u"\u215D"], 
                       [":/symbols/seven_eighths.svg", "Seven Eighths", u"\u215E"], 
                       [":/symbols/per_thousand.svg", "Per Thousand", u"\u2030"],
                       [":/symbols/trademark.svg", "Trademark", u"\u2122"], 
                       [":/symbols/center_line.svg", "Center Line", u"\u2104"],
                       [":/symbols/hole_depth.svg", "Hole depth", u"\u21A7"], 
                       [":/symbols/counterbore.svg", "Counterbore", u"\u2334"],
                       [":/symbols/countersink.svg", "Countersink", u"\u2335"], 
                       [":/symbols/diameter.svg", "Diameter", u"\u2300"],
                       [":/symbols/square.svg", "Square", u"\u25A1"], 
                       [":/symbols/conical_taper.svg", "Conical Taper", u"\u2332"],
                       [":/symbols/slope.svg", "Slope", u"\u2333"], 
                       [":/symbols/continous_feature.svg", "Continous Feature", u"\uE000"], 
                       [":/symbols/statistical_tolerance.svg", "Statistical Tolerance", u"\uE001"], 
                       [":/symbols/copyleft.svg", "Copyleft", u"\u2183"],
                       [":/symbols/copyright.svg", "Copyright", u"\u00A9"]]
        menu = QtGui.QMenu()
        for symbol in symbol_list:
            icon = QtGui.QIcon(symbol[0])
            action = QtGui.QAction(symbol[1], self.form.insert_symbol)
            action.setIcon(icon)
            action.triggered.connect(insert_symbol(symbol[2]))
            menu.addAction(action)
        self.form.insert_symbol.setMenu(menu)
        self.form.insert_symbol.setDefaultAction(action)
        self.form.insert_symbol.triggered.connect(self.form.insert_symbol.setDefaultAction)

          
# TODO: implement horizontal alignment. Maybe using QTextItem instead of 
#       SimpleTextItem and HTML.
class AnnotationItem(QtGui.QGraphicsSimpleTextItem):
#    ALIGNMENT = {"Left":    QtCore.Qt.AlignLeft,
#                 "Right":   QtCore.Qt.AlignRight,
#                 "Center":  QtCore.Qt.AlignHCenter,
#                 "Justify": QtCore.Qt.AlignJustify}
    def __init__(self, parent=None, scene=None):
        super(AnnotationItem, self).__init__(parent, scene)
        self.config = {}
        self.editModeOn = True
        self.arrows = []
        self.point_catchers = []
        self.setLinePen(QtCore.Qt.black)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setCursor(QtCore.Qt.OpenHandCursor)
    
    def configAnnotation(self, **kwargs):
        """Configure some annotation properties. These are used to paint lines"""
        self.config["type"] = kwargs.get("type_")
        self.config["side"] = kwargs.get("side")
        self.config["halign"] = kwargs.get("halign")
        self.config["valign"] = kwargs.get("valign")
        self.config["head"] = kwargs.get("head")
        self.update()
        for arrow in self.arrows:
            self.setPivot(arrow)
            arrow.setHead(self.config["head"])
    
    def addArrow(self):
        """Slot for arrow creation"""
        if not self.editModeOn:
            return
        arrow = Arrow()
        # Set tail
        self.setPivot(arrow) 
        # Set head
        arrow.setHead(self.config["head"])
        if len(self.arrows) > 0:
            last_arrow = self.arrows[-1]
            arrow.setHeadPos(last_arrow.getHeadPos()+QtCore.QPointF(0, 20))
        else:
            arrow.setHeadPos(arrow.getTailPos()+QtCore.QPointF(-40, -40))
        self.arrows.append(arrow)
        self.point_catchers.append(PointCatcher(arrow))
   
    def getPivot(self):
        """Get pivot point in Annotation coordinate system."""
        rect = self.boundingRect()
        # TODO: Use dict instead of all these if's?
        if self.config["side"] == "Left":
            if self.config["type"] == "Straight Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topLeft() + QtCore.QPointF(12, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.left()+12, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomLeft() + QtCore.QPointF(12, -6)
            elif self.config["type"]  == "End Bent Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topLeft() + QtCore.QPointF(2, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.left()+2, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomLeft() + QtCore.QPointF(2, -6)
            elif self.config["type"]  == "Bent Leader": 
                pivot = QtCore.QPointF(rect.left()+12, rect.bottom()-6)
        elif self.config["side"] == "Right":
            if self.config["type"] == "Straight Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topRight() + QtCore.QPointF(-12, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.right()-12, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomRight() + QtCore.QPointF(-12, -6)
            elif self.config["type"]  == "End Bent Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topRight() + QtCore.QPointF(-2, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.right()-2, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomRight() + QtCore.QPointF(-2, -6)
            elif self.config["type"]  == "Bent Leader":
                pivot = QtCore.QPointF(rect.right()-12, rect.bottom()-6)
        return pivot
    
    def setPivot(self, arrow):
        """Set pivot point to arrow tail and to annotation
        in scene coordinate system."""
        pivot = self.getPivot()
        self.setTransformOriginPoint(pivot)
        tail = self.mapToScene(pivot)
        arrow.setTailPos(tail)
        self.update()
        arrow.update()
        
    def setFontSize(self, size):
        """Set font size in millimeter. It converts mm in pt."""
        font = self.font()
        font.setPointSizeF(mmtopt(size))
        self.setFont(font)
        for arrow in self.arrows:
            self.setPivot(arrow)
        
    def setFontColor(self, color):
        """Set font color"""
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        brush.setColor(color)
        self.setBrush(brush)
    
    def setLinePen(self, color, width=0.5):
        """Set line to draw shoulder line."""
        self.pen = QtGui.QPen(color)
        self.pen.setCapStyle(QtCore.Qt.RoundCap)
        self.pen.setWidthF(mmtopt(0.5))
        
    def setEditMode(self, value):
        """Edit mode, true when editing (or creating) the annotation"""
        self.editModeOn = value
    
    def boundingRect(self):
        rect = super(AnnotationItem, self).boundingRect()
        return rect.adjusted(-20, -10, 20, 10)
    
    def hoverEnterEvent(self, event):
        self.color = self.brush().color() #remember my actual color
        if self.editModeOn == False:
            self.setFontColor(QtCore.Qt.darkGreen)
            self.setLinePen(QtCore.Qt.darkGreen)
            for arrow in self.arrows:
                arrow.setPen(QtGui.QPen(QtCore.Qt.darkGreen))
                arrow.setBrush(QtCore.Qt.darkGreen)
    
    def hoverLeaveEvent(self, event):
        if self.editModeOn == False:
            self.setFontColor(self.color)
            self.setLinePen(QtCore.Qt.black)
            for arrow in self.arrows:
                arrow.setPen(QtGui.QPen(QtCore.Qt.black))
                arrow.setBrush(QtCore.Qt.black)
        
    def mouseDoubleClickEvent(self, event):
        FreeCAD.Console.PrintMessage("annotation dclick %s\n" % self.boundingRect())
       
    def mouseMoveEvent(self, event):
        for arrow in self.arrows:
            self.setPivot(arrow)
        super(AnnotationItem, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        for arrow in self.arrows:
            self.setPivot(arrow)
        super(AnnotationItem, self).mouseReleaseEvent(event)
        
    def paint(self, painter, option, widget=None):
        rect = self.boundingRect()
        # Draw rect
        if self.editModeOn: 
            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.DotLine)
            pen.setColor(QtCore.Qt.gray)
            pen.setWidthF(2)
            painter.setPen(pen)
            painter.drawRect(-5, -5, rect.width()-20, rect.height()-8)
        # Draw shoulder line
        painter.setPen(self.pen)
        if len(self.arrows) > 0:
            if self.config["type"] == "Bent Leader":
                painter.drawLine(rect.left()+12, rect.bottom()-6,
                                 rect.right()-11.8, rect.bottom()-6)
            elif self.config["type"] == "End Bent Leader":
                if self.config["valign"] == "Top":
                    y = rect.top() + 6
                elif self.config["valign"] == "Center":
                    y = rect.center().y()
                elif self.config["valign"] == "Bottom":
                    y = rect.bottom() - 6
                if self.config["side"] == "Left":
                    painter.drawLine(rect.left()+2, y,
                                 rect.left()+15, y)
                elif self.config["side"] == "Right":
                    painter.drawLine(rect.right()-2, y,
                                 rect.right()-15, y)
        super(AnnotationItem, self).paint(painter, option, widget) 
        
    
class Annotation:
    """Feature for a text annotation in draw"""
    def __init__(self, obj):
        self.text = ""
        self.arrowline = None #ArrowLine
   
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, obj):
        FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")

class AnnotationView:
    """View for a text annotation in draw"""
    def __init__(self, vobj):
        vobj.Proxy = self
        
    def attach(self, vp):
        pass
    
    def onChanged(self, vp, prop):
        pass
                
    def updateData(self, fp, prop):
        pass
    
        
class AnnotationCommand:
    """Command for creating new note"""   
    def IsActive(self):
        if FreeCADGui.ActiveDocument == None:
            return False
        return not FreeCADGui.Control.activeDialog()
        
    def Activated(self):  
        graphics_view = getGraphicsView()
        if not graphics_view: # page is not active
            return 
        FreeCADGui.Control.showDialog(AnnotationTask(graphics_view))
        FreeCAD.ActiveDocument.recompute()

    def GetResources(self):
        return {
            "Pixmap" : ":/icons/annotation.svg",
            "Accel" : "Shift+A",
            "MenuText": "Annotation",
            "ToolTip": "Create a note."
            }

FreeCADGui.addCommand("Dimensioning_Annotation", AnnotationCommand())
