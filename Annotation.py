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
from Utils import getGraphicsView, mmtopt, pttomm, setButtonColor

from GraphicItem import Arrow, PointCatcher
### TODO LIST
# () implement text horizontal alignment 
# () implement functionality to delete arrows (delete button)
# () implement "save as default" functionality
# () implement editing functionality

class AnnotationTask:
    """Create and handle annotation task dialog"""
    # https://mandeep7.wordpress.com/2017/05/07/using-qt-ui-files-with-pyside-in-freecad/
    INSERT_MODE, EDIT_MODE = range(2)
    def __init__(self, graphics_view):
        self.mode = self.INSERT_MODE
        self.annotation = None
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
            self.scene.removeItem(self.annotation)
            for arrow in self.annotation.arrows:
                self.scene.removeItem(arrow)
            for catcher in self.annotation.point_catchers:
                self.scene.removeItem(catcher)
   
    ## SLOTS ##
    def mousePress(self, event):
        """Handle the mouse press event inside scene"""
        # FIXME: When click over another item the cursor doesn't change to arrowcursor
        pos = event.scenePos()
        if self.mode == self.INSERT_MODE:
            self.mode = self.EDIT_MODE
            self.annotation = AnnotationItem()
            self.connectSlots()
            self.configFont()
            self.configLeaderLine()
            self.annotation.setPos(pos)
            self.scene.addItem(self.annotation)
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
                self.annotation.setEditMode(False) 
                for catcher in self.annotation.point_catchers:
                    self.scene.removeItem(catcher)
                self.annotation.update()
                self.disconnectSlots()
                self.changeCursor(QtCore.Qt.PointingHandCursor)
                # Create a feature and view
                document = self.graphics_view.getDocument()
                annotation = document.addObject("App::FeaturePython", "Annotation")
                Annotation(annotation)
                AnnotationView(annotation.ViewObject, self.annotation)
                page = self.graphics_view.getPage()
                page.addObject(annotation)
                self.annotation = None
                FreeCAD.ActiveDocument.recompute()
                FreeCAD.Console.PrintMessage("Annotation created.\n")
        # TODO: implement close taskdialog with Escape key
        elif event.key() == QtCore.Qt.Key_Escape: #close
            pass 
        
    def colorDialogAccepted(self, color):
        """Slot cancel color dialog. Reset actual color."""
        setButtonColor(self.form.font_color_button, color)
        self.form.font_color_lineEdit.clear()
        self.form.font_color_lineEdit.insert(str(color.getRgb()).strip("()"))
    
    def colorDialogRejected(self):
        """Slot to return color to color before open color dialog."""
        colorRGBA = map(int, self.form.font_color_lineEdit.text().split(","))
        color = QtGui.QColor(*colorRGBA)
        self.annotation.setFontColor(color)

    # NOTE: PySide don't have a better QPlainTextEdit signal to do this
    def textChanged(self):
        """Set new text when it has changed."""
        text = self.form.text_widget.toPlainText()
        self.annotation.setText(text)
        for arrow in self.annotation.arrows:
            self.annotation.setPivot(arrow)
    
    def createArrow(self):
        """Add arrow to scene."""
        self.annotation.addArrow()
        self.scene.addItem(self.annotation.arrows[-1])
        self.scene.addItem(self.annotation.point_catchers[-1])
        
    ## METHODS ##
    def connectSlots(self):
        """Connect all slot functions to dialog widgets"""
        self.form.font_family.currentFontChanged.connect(self.annotation.setFontFamily)
        self.form.font_size.valueChanged.connect(self.annotation.setFontSize)
        self.form.text_widget.textChanged.connect(self.textChanged)
        self.dialog.currentColorChanged.connect(self.annotation.setFontColor)
        self.dialog.rejected.connect(self.colorDialogRejected)
        self.form.orientation_angle.valueChanged.connect(self.annotation.setRotation)
        self.form.leader_add.clicked.connect(self.createArrow)
        self.form.leader_type.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_side.currentIndexChanged.connect(self.configLeaderLine)
        self.form.horizontal_align.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_valign.currentIndexChanged.connect(self.configLeaderLine)
        self.form.leader_head.currentIndexChanged.connect(self.configLeaderLine)
    
    def disconnectSlots(self):
        """Disconnect all slot functions to dialog widgets"""
        self.form.font_family.currentFontChanged.disconnect(self.annotation.setFontFamily)
        self.form.font_size.valueChanged.disconnect(self.annotation.setFontSize)
        self.form.text_widget.textChanged.disconnect(self.textChanged)
        self.dialog.currentColorChanged.disconnect(self.annotation.setFontColor)
        self.dialog.rejected.disconnect(self.colorDialogRejected)
        self.form.orientation_angle.valueChanged.disconnect(self.annotation.setRotation)
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
        self.annotation.setFont(font)
        self.annotation.setFontSize(size)
        self.annotation.setFontColor(color)
        self.annotation.setText(text)
        self.annotation.setRotation(angle)
        
    def configLeaderLine(self, index=0):
        """Configure leader line."""
        kind = self.form.leader_type.currentText()
        side = self.form.leader_side.currentText()
        halign = self.form.horizontal_align.currentText()
        valign = self.form.leader_valign.currentText()
        head = self.form.leader_head.currentText()
        self.annotation.configAnnotation(kind=kind, 
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
    
    # TODO: In future, change this for a button to a character map dialog.
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
        for prop in ["kind", "side", "halign", "valign", "head"]:
            if prop in kwargs:
                self.config[prop] = kwargs[prop]
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
            if self.config["kind"] == "Straight Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topLeft() + QtCore.QPointF(12, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.left()+12, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomLeft() + QtCore.QPointF(12, -6)
            elif self.config["kind"]  == "End Bent Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topLeft() + QtCore.QPointF(2, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.left()+2, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomLeft() + QtCore.QPointF(2, -6)
            elif self.config["kind"]  == "Bent Leader": 
                pivot = QtCore.QPointF(rect.left()+12, rect.bottom()-6)
        elif self.config["side"] == "Right":
            if self.config["kind"] == "Straight Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topRight() + QtCore.QPointF(-12, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.right()-12, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomRight() + QtCore.QPointF(-12, -6)
            elif self.config["kind"]  == "End Bent Leader":
                if self.config["valign"] == "Top":
                    pivot = rect.topRight() + QtCore.QPointF(-2, 6)
                elif self.config["valign"] == "Center":
                    pivot = QtCore.QPointF(rect.right()-2, rect.center().y())
                elif self.config["valign"] == "Bottom":
                    pivot = rect.bottomRight() + QtCore.QPointF(-2, -6)
            elif self.config["kind"]  == "Bent Leader":
                pivot = QtCore.QPointF(rect.right()-12, rect.bottom()-6)
        return pivot
    
    def getFontFamily(self):
        """Get font family name."""
        return self.font().family()
    
    def getFontSize(self):
        """Get font size in millimiters."""
        return pttomm(self.font().pointSizeF())
    
    def getFontColor(self, colors="rgba", type_="float"):
        """Get font color rgba (0.0 - 1.0)"""
        color = self.brush().color()
        if type_ == "float":
            dic = {"r": color.redF(),  "g": color.greenF(), 
                   "b": color.blueF(), "a": color.alphaF()}
        elif type_ == "integer":
            dic = {"r": color.red(),  "g": color.green(), 
                   "b": color.blue(), "a": color.alpha()}
        out = [dic[c] for c in colors]
        if len(out) == 1:
            return out[0]
        return tuple(out)
    
    def getText(self, split=True):
        """Get font text. Split lines into list."""
        if split:
            return self.text().split("\n")
        return self.text()

    def setPivot(self, arrow):
        """Set pivot point to arrow tail and to annotation
        in scene coordinate system."""
        pivot = self.getPivot()
        self.setTransformOriginPoint(pivot)
        tail = self.mapToScene(pivot)
        arrow.setTailPos(tail)
        arrow.update()
    
    def setFont(self, font):
        """Override setFont(). Reset pivots"""
        super(AnnotationItem, self).setFont(font)
        for arrow in self.arrows:
            self.setPivot(arrow)
    
    def setText(self, text):
        super(AnnotationItem, self).setText(text)
        for arrow in self.arrows:
            self.setPivot(arrow)
        
    def setFontFamily(self, font):
        """Set family name."""
        actual_font = self.font()
        actual_font.setFamily(font.family())
        self.setFont(actual_font)
    
    def setFontByName(self, name):
        """Set font by family name. Convinience method."""
        font = self.font()
        font.setFamily(name)
        self.setFont(font)
    
    def setFontSize(self, size):
        """Set font size in millimeter. It converts mm in pt."""
        font = self.font()
        font.setPointSizeF(mmtopt(size))
        self.setFont(font)
        
    def setFontColor(self, color):
        """Set font color."""
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        brush.setColor(color)
        self.setBrush(brush)
        
    def setLinePen(self, color, width=0.5):
        """Set line to draw shoulder line."""
        self.pen = QtGui.QPen(color)
        self.pen.setCapStyle(QtCore.Qt.RoundCap)
        self.pen.setWidthF(mmtopt(0.5))
    
    def setVisible(self, visible):
        """Set visibility to annotation and its arrows."""
        super(AnnotationItem, self).setVisible(visible)
        for arrow in self.arrows:
            arrow.setVisible(visible)
            
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
        #TODO: must be implemented
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
            if self.config["kind"] == "Bent Leader":
                painter.drawLine(rect.left()+12, rect.bottom()-6,
                                 rect.right()-11.8, rect.bottom()-6)
            elif self.config["kind"] == "End Bent Leader":
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
        # Font
        obj.addProperty("App::PropertyFont", "FontFamily", 
                        "Font", "Font family")
        obj.addProperty("App::PropertyLength", "FontSize", 
                        "Font", "Font size")
        obj.addProperty("App::PropertyColor", "FontColor", 
                        "Font", "Font color")
        obj.addProperty("App::PropertyPercent", "Opacity", 
                        "Font", "Font opacity")
        # Content
        obj.addProperty("App::PropertyStringList", "Text",
                        "Content", "Annotation text")
        obj.addProperty("App::PropertyEnumeration", "HorizontalAlign", 
                        "Content", "Horizontal alignment")
        obj.HorizontalAlign = ["Left", "Center", "Right", "Justify"]
        obj.addProperty("App::PropertyEnumeration", "VerticalAlign", 
                        "Content", "Vertical alignment")
        obj.VerticalAlign = ["Top", "Center", "Bottom"]
        obj.addProperty("App::PropertyAngle", "Orientation",
                        "Content", "Text Orientation")
        # Leader Lines
        obj.addProperty("App::PropertyEnumeration", "LeaderType", 
                        "LeaderLine", "Leader line type")
        obj.LeaderType = ["Straight Leader", "Bent Leader", "End Bent Leader"]
        obj.addProperty("App::PropertyEnumeration", "Side", 
                        "LeaderLine", "Leader line side")
        obj.Side = ["Left", "Right"]
        obj.addProperty("App::PropertyEnumeration", "Head", "LeaderLine", 
                        "Leader line head")
        obj.Head = ["Filled Arrow", "Open Arrow", "Dot", "None"]
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, obj):
        pass


class AnnotationView:
    """View for a text annotation in draw"""
    def __init__(self, vobj, graphics_item):
        self.annotation = graphics_item
        vobj.Proxy = self
    
    def setEdit(self, mode):
        #https://www.freecadweb.org/wiki/Std_Edit
        """Enter in task dialog to edit annotation."""
        # TODO: implement this to edit a annotation
        return False
    
    def doubleClicked(self, vp):
        """Called when double click in object in treeview."""
        page = vp.Object.getParentGroup() #feature
        page_view = page.ViewObject.Proxy
        page_view.graphics_view.setActive()
        return True
    
    def attach(self, vp):
        # NOTE: it must be done to show coulored icon in tree view 
        # https://forum.freecadweb.org/viewtopic.php?t=12139
        from pivy import coin
        vp.addDisplayMode(coin.SoGroup(), "Standard")
        # Set feature properties
        feature = vp.Object
        alpha = self.annotation.getFontColor("a")
        feature.FontFamily = self.annotation.getFontFamily()
        feature.FontSize = self.annotation.getFontSize()
        feature.FontColor = self.annotation.getFontColor("rgb")
        feature.Opacity = int(alpha * 100) #percent
        feature.Text = self.annotation.getText()
        feature.HorizontalAlign = self.annotation.config["halign"]
        feature.VerticalAlign = self.annotation.config["valign"]
        feature.Orientation = self.annotation.rotation()
        feature.LeaderType = self.annotation.config["kind"]
        feature.Side = self.annotation.config["side"]
        feature.Head = self.annotation.config["head"]
    
    def onChanged(self, vp, prop):
        """Called when AnnotationView property changes"""
        if prop == "Visibility":
            visibility = vp.getPropertyByName("Visibility")
            self.annotation.setVisible(visibility)
                
    def updateData(self, fp, prop):
        """Called when Annotation property changes"""
        if prop == "FontFamily":
            family = fp.getPropertyByName("FontFamily")
            self.annotation.setFontByName(family)
        elif prop == "FontSize":
            size = fp.getPropertyByName("FontSize")
            self.annotation.setFontSize(size)
        elif prop == "FontColor" or prop == "Opacity":
            color = fp.getPropertyByName("FontColor")
            alpha = fp.getPropertyByName("Opacity")
            qcolor = QtGui.QColor()
            qcolor.setRgbF(color[0], color[1], color[2], alpha/100.0)
            self.annotation.setFontColor(qcolor)
        elif prop == "Text":
            text = fp.getPropertyByName("Text")
            text = "\n".join(text)
            if text.strip() == "":
                self.annotation.setText("Note")
                fp.Text = ["Note"]
                QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), 
                                          "Dimensioning Workbench",
                                          "Text should not be empty.")
            else:
                self.annotation.setText(text)
        elif prop == "HorizontalAlign":
            horizontal_align = fp.getPropertyByName("HorizontalAlign")
            self.annotation.configAnnotation(halign=horizontal_align)
        elif prop == "VerticalAlign":
            vertical_align = fp.getPropertyByName("VerticalAlign")
            self.annotation.configAnnotation(valign=vertical_align)
        elif prop == "Orientation":
            orientation = fp.getPropertyByName("Orientation")
            self.annotation.setRotation(orientation)
        elif prop == "LeaderType":
            leader_type = fp.getPropertyByName("LeaderType")
            self.annotation.configAnnotation(kind=leader_type)
        elif prop == "Side":
            side = fp.getPropertyByName("Side")
            self.annotation.configAnnotation(side=side)
        elif prop == "Head":
            head = fp.getPropertyByName("Head")
            self.annotation.configAnnotation(head=head)
            
    def getIcon(self):
        return ":/icons/annotation.svg"
    
    def getDisplayModes(self,obj):
        """Return a list of display modes."""
        return ["Standard"]

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. 
        It must be defined in getDisplayModes."""
        return "Standard"
    
        
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
        return {"Pixmap" : ":/icons/annotation.svg",
                "Accel" : "Shift+A",
                "MenuText": "Annotation",
                "ToolTip": "Create a note."}

FreeCADGui.addCommand("Dimensioning_Annotation", AnnotationCommand())
