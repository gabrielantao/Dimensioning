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
This module creates a new page for drawing.
"""
from Utils import getParam
import FreeCAD, FreeCADGui

from PySide import QtGui

from PageGraphicsView import PageGraphicsView 

import GraphicItem

# NOTA: as orthoviews sao grupos de objetos (DocumentObjectGroupPython ?)
class Page:
    """
    Container for technical pages objects (DocumentObjectGroupPython).
    Armazena as views, carrega template, le e armazena captions, salva temp.svg,
    

    ProjectionType: "first angle" # pega das preferencias
    TemplateName: "" # pega das preferencias
    CaptionText: "" # pega do arquivo template
    Views: Lista dos views (funcao de container da PAge)

    PaperSize: A0, A1, A2, A3, A4, A5 #pega do arquivo svg do template
    PaperOrientation: landscape or portrait
    PaperMargins: #pega do arquivo svg do template
    ProjSymbolPositon: #posicao do rect onde deve ficar o simbolo de angulo PEGA do arquivo template

    ShowGrid: on off
    GridSpacing: distancia entre duas linhas
    """
    paper_sizes = {"landscape": {"A0":[]}, "portrait": {"A0":[]}}
    def __init__(self, obj):
        # general properties
        obj.addProperty("App::PropertyEnumeration", "ProjectionAngle", "Base",
                        "Projection angle").ProjectionAngle = ["first", "tird"] #getParam("ProjAngle", "General") 
        obj.addProperty("App::PropertyString", "TemplateName", "Base",
                        "Name of svg template").TemplateName = "template2.svg"#getParam("TemplateName", "General")
        obj.addProperty("App::PropertyStringList", "CaptionText", "Base",
                        "Editable texts list")
        
        ##self.views = [] #TODO: adicionar
        # Paper properties (read only)
#        obj.addProperty("App::PropertyString", "PaperSize", "Page",
#                        "Paper size code", True)
#        obj.addProperty("App::PropertyString", "PaperOrientation", "Page",
#                        "Paper orientation", True)
#        obj.addProperty("App::PropertyFloat", "PaperWidth", "Page",
#                        "Paper width in mm", True)
#        obj.addProperty("App::PropertyFloat", "PaperHeight", "Page",
#                        "Paper hight in mm", True)
#        obj.addProperty("App::PropertyFloatList", "Top", "Margin",
#                        "Paper top, bottom, left and right margins in mm", 0, True)#TODO: AGRUPAR TIPO O PLACEMENT separar em 4 propriedades
#        obj.addProperty("App::PropertyFloatList", "ProjSymbolPositon", "Page",
#                        "Rect of proj angle x, y, width, height in mm", 0, True) #TODO: AGRUPAR TIPO O PLACEMENT separar em 4 propriedades
        obj.Proxy = self
#        self.Type = "Page"
        
#    def onBeforeChange(self, prop):
#        #TODO: colocar aqui lidar com um line edit para escala que verifica o formato 10:1 por exemplo
#        #      verifica se tem os dois pontos
#        if prop == "scale":
#            pass

    def onChanged(self, fp, prop):
        pass
        

    def execute(self, obj):
        pass
#        FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")
        

    def hasValidTemplate(self):
        pass

    def getPageWidth(self):
        pass

    def getPageHeight(self):
        pass

    def getPageOrientation(self):
        pass

    def addView(self):
        pass

    def removeView(self):
        pass

    def getAllViews(self):
        pass

    def requestPaint(self):
        pass

    def onDocumentRestored(self):
        pass

    def unsetupObject(self):
        pass

    def getNextBalloonIndex(self):
        pass

    def restore(self):
        pass

    def getTemplate(self):
        """Read template document"""
        pass

class PageView:
#TODO: fechar janela de MDI de desenho quando fechar o documento
#TODO: alterar titulo da janela de MDI quando salvar o documento
    
#TODO: adicionar backgrond color, frame caption, show frame (no View)
#TODO: adicionar editable text color, font, size (no View)

#TODO: acidionar thickness e color (no View) 
#TODO: adionar page caption 
#TODO: adicionar backgrond color, frame caption, show frame (no View)
#TODO: adicionar editable text color, font, size (no View)
    def __init__(self, vobj):
        """Set this object to the proxy object of the actual view provider""" 
        # general properties
        vobj.addProperty("App::PropertyBool", "AutoUpdate", "Base",
                         "Keep page sync with model").AutoUpdate=True#getParam("AutoUpdate", "General")
        vobj.addProperty("App::PropertyBool", "ShowUnit", "Base",
                         "Show dimensions units")#.ShowUnit = getParam("ShowUnit", "General") 
        vobj.addProperty("App::PropertyBool", "ShowViewFrame", "Base",
                         "Show view frame")#.ShowFrame = getParam("ShowViewFrame", "General")
        vobj.addProperty("App::PropertyBool", "ShowViewFrameCaption", "Base",
                         "Show view frame caption")#.ShowFrameCaption = getParam("ShowFrameCaption", "General")
        # grid properties
        vobj.addProperty("App::PropertyBool", "ShowGrid", "Grid",
                         "Show background grid")
        vobj.addProperty("App::PropertyFloat", "GridSpacing", "Grid",
                         "Grid spacing in mm")
        vobj.Proxy = self
#        self.Type = "Page"

        
    def attach(self, vp):
        """Create and configure a new QSubWindow in FreeCAD MDIArea"""
        self.showPage()
    
    def onChanged(self, vp, prop):
        """Called when PageView property changes"""
        pass
#        if prop == "Visibility": #NOTE: usar visibilidade para esconder os views e nao esconder a janela, esta eh estatica (nao pode ser fechada)
#            if vp.getPropertyByName("Visibility"): #FIXME: cria varias vezes a janela se clicar varias vezes em show
#                self.showPage()
#            else: #hide page
#                self.hidePage()
                
    def updateData(self, fp, prop):
        """Called when Page property changes"""
        if prop == "Label":
            self.relabel(fp.getPropertyByName("Label"))
        pass
    
    def onDelete(self, vp, subname):
        """Delete page"""
        #TODO: salvar o arquivo temp?
        if vp.getPropertyByName("Visibility"):
            self.hidePage() 
        return True
   
    def relabel(self, title):
        """a"""
        self.graphics_view.setPageTitle(title)
    
#    def onRelabel(self, pDoc):
#        cap = "{} : {}".format(pDoc.getDocument().Label.getValue(), "page")  
#        self.relabel(cap)
        
    def showPage(self):
        self.graphics_view = PageGraphicsView()
            
    def hidePage(self):
        self.graphics_view.parentWidget().deleteLater() #schedule for deletion

#    def __getstate__(self):
#        """When saving the document this object gets stored using Python"s json module.\
#                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
#                to return a tuple of all serializable objects or None."""
#        return None
# 
#    def __setstate__(self,state):
#        """When restoring the serialized object from document we have the chance to set some internals here.\
#                Since no data were serialized nothing needs to be done here."""
#        return None

    def getIcon(self):
        return ":/icons/page.svg" # FIXME: O icone demora para aparecer. Porque?

    
class PageCommand:
    """Command for creating new page"""
# NOTA: se basear no metodo CmdDrawingOpen
#https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Drawing/Gui/Command.cpp
    def IsActive(self):
        if FreeCADGui.ActiveDocument == None:
            return False
        return not FreeCADGui.Control.activeDialog()
    
    def openTemplate(self):
        pass
    
    def getEditableText(self):
        pass
    
    def Activated(self):
        # 1) abre janela para escolher qual arquivo escolher
        page = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "Page")
        Page(page)
        PageView(page.ViewObject)
        
        FreeCAD.ActiveDocument.recompute()
       # return fpo

    def GetResources(self):
        return {
            "Pixmap" : ":/icons/new_page.svg",
            "Accel" : "Shift+N",
            "MenuText": "NewPage",
            "ToolTip": "Open a new drawing page."
            }

FreeCADGui.addCommand("Dimensioning_Page", PageCommand())
