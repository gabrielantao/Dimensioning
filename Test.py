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
MODULE FOR TESTS
"""


from PySide import QtGui, QtCore, QtSvg
import FreeCAD, FreeCADGui
from Utils import getGraphicsView

from SvgParser import SvgParser
from GraphicItem import ViewGroup

class TestCommand:
    """Command for test."""
    def IsActive(self):
        if FreeCADGui.ActiveDocument == None:
            return False
        return not FreeCADGui.Control.activeDialog()

    def Activated(self):
        graphics_view = getGraphicsView()
        if not graphics_view: # page is not active
            return
        with open("/home/gabrielantao/.FreeCAD/Mod/Dimensioning/Test/semicircle4.svg", "r") as f:
            parser = SvgParser(f.read())
            #group = QtGui.QGraphicsItemGroup()
            #group.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
            #group.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
#            group.setPos(QtCore.QPointF(0,0))
            for item in parser.vertices:
                graphics_view.scene().addItem(item)
                #group.addToGroup(item)
            for item in parser.paths:
                graphics_view.scene().addItem(item)
                #group.addToGroup(item)
            #graphics_view.scene().addItem(group)
#            FreeCAD.Console.PrintMessage("{}\n".format(group))


    def GetResources(self):
        return {"Pixmap" : ":/icons/test.svg",
                "Accel" : "Shift+T",
                "MenuText": "Test",
                "ToolTip": "Make a test."}

FreeCADGui.addCommand("Dimensioning_Test", TestCommand())
