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
Convinience functions.
"""

from math import sin, cos, radians, degrees  
import numpy as np

import json
import FreeCAD, FreeCADGui
from sys import version_info

from PySide import QtCore, QtGui, QtUiTools

# This is necessary for compatibility reasons
if version_info[0] == 2:
    is_str_instance = lambda value : isinstance(value, unicode)
else:
    is_str_instance = lambda value : isinstance(value, str)

def RGBtoUnsigned(color):
    """Convert rgb color list to unsigned value"""
    return (color[0] << 24) + (color[1] << 16) + (color[2] << 8) 

def unsignedtoRGB(value):
    """Convert unsigned value to rbg color list"""
    red = (value >> 24) & 0xFF
    green = (value >> 16) & 0xFF
    blue = (value >> 8) & 0xFF
    return [red, green, blue] 

def getParam(param, path):
    """Get default preference"""
    path = "User parameter:BaseApp/Preferences/Mod/Dimensioning/".format(path)
    pref = FreeCAD.ParamGet(path)
    with open("preferences.json", "r") as pref_file:
        default = json.loads(pref_file.read())[path][param]
    if isinstance(default, int):
        return pref.GetInt(param, default)
    elif is_str_instance(default): #str is always unicode here
        if default == "true" or default == "false":
            return pref.GetBool(param, default)
        return pref.GetString(param, default)
    elif isinstance(default, float):
        return pref.GetFloat(param, default)
    elif isinstance(default, list): #only color
        return pref.GetUnsigned(param, RGBtoUnsigned(default))

def setParam(param, value, path):
    """Set default preference"""
    path = "User parameter:BaseApp/Preferences/Mod/Dimensioning/".format(path)
    pref = FreeCAD.ParamGet(path)
    if isinstance(value, int):
        pref.SetInt(param, value)
    elif is_str_instance(value): #str is always unicode here
        if value == "true" or value == "false":
            pref.SetBool(param, value)
        else:
            pref.SetString(param, value)
    elif isinstance(value, float):
        pref.SetFloat(param, value)
    elif isinstance(value, list): #only color
        pref.SetUnsigned(param, RGBtoUnsigned(value))
    elif isinstance(value, bool):
        if value:
            pref.SetBool(param, "true")
        else:
            pref.SetBool(param, "false")
        
def mmtopx(value):
    """Convert dimension in millimiter into pixel"""
    DPI = 90.0 #Inkscape default
    if isinstance(value, QtCore.QPointF):
        x = value.x() * DPI / 25.4
        y = value.y() * DPI / 25.4
        return QtCore.QPointF(x, y)
    return value * DPI / 25.4 # 1 in -> 25.4 mm 

def mmtopt(value):
    """Convert dimension in millimiters to pt (font point)"""
    factor = 72.0 # 72 pt -> 25.4mm
    return value * factor / 25.4

def pttomm(value):
    """Convert dimension in pt (font point) to millimiters"""
    factor = 72.0
    return value * 25.4 / factor

def getGraphicsView():
    """Get reference to PageGraphicsView if active and None if not.
    This is used in command calls (except Page creation command)."""
    from PageGraphicsView import PageGraphicsView
    mw =  FreeCADGui.getMainWindow()
    mdi = mw.centralWidget()
    subwindow = mdi.activeSubWindow()
    return subwindow.findChild(PageGraphicsView)

def setButtonColor(button, color, width=32, height=24):
    #TODO: colocar um frame em volta do Pixmap
    colorPix = QtGui.QPixmap(width, height)
    colorPix.fill(color)
    button.setIcon(QtGui.QIcon(colorPix))

#TODO: use numpy functions here
def rotate(vector, angle):
    """Rotate a vector. Angle in degrees.
    M = [cos(a) sin(a)] * [v_x]
        [-sin(a cos(a)]   [v_y]
    """
    v_x = vector.x()
    v_y = vector.y()
    angle = radians(angle)
    return QtCore.QPointF( v_x*cos(angle) + v_y*sin(angle),
                          -v_x*sin(angle) + v_y*cos(angle))

def angleBetween(vector_1, vector_2):
    """Calculate the angle between two numpy column arrays in degrees.
    https://www.w3.org/TR/SVG/implnote.html#ArcConversionEndpointToCenter
    """
    num = np.vdot(vector_1, vector_2) #dot product
    num /= np.linalg.norm(vector_1) * np.linalg.norm(vector_2)
    factor = np.linalg.det(np.concatenate([vector_1, vector_2], axis=1).T)
    factor = 1 if factor >= 0 else -1
    return factor*degrees(np.arccos(num))
