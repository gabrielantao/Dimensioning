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

from Dimensioning import *

class DimensioningWorkbench(FreeCADGui.Workbench):
    def __init__(self):
		self.__class__.Icon = FreeCAD.getUserAppDataDir() + \
                      "Mod/Dimensioning/Resources/icons/page.svg"
		self.__class__.MenuText = "Dimensioning"
		self.__class__.ToolTip = "Technical drawing dimensioning tool"
        
    def Initialize(self):
        # copy the Drawing toolbar
        self.appendToolbar("Drawing Workbench Commands", 
                           ["Dimensioning_Page",
                            "Dimensioning_Orthographic",
                            "Dimensioning_Annotation",
                            "Dimensioning_Image",
                            "Dimensioning_Test"])

      
        FreeCADGui.addIconPath(':/icons')
        FreeCADGui.addPreferencePage( ":/ui/preferences_general.ui", 
                                     "Dimensioning")


FreeCADGui.addWorkbench(DimensioningWorkbench())


