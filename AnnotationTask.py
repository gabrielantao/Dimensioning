# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'annotation_task.ui'
#
# Created: Thu Jul 25 18:53:53 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Annotation(object):
    def setupUi(self, Annotation):
        Annotation.setObjectName("Annotation")
        Annotation.resize(353, 747)
        self.gridLayout = QtGui.QGridLayout(Annotation)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(Annotation)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.font_family = QtGui.QFontComboBox(self.groupBox)
        self.font_family.setObjectName("font_family")
        self.horizontalLayout_2.addWidget(self.font_family)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setStyleSheet("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.font_color_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.font_color_lineEdit.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.font_color_lineEdit.sizePolicy().hasHeightForWidth())
        self.font_color_lineEdit.setSizePolicy(sizePolicy)
        self.font_color_lineEdit.setInputMask("")
        self.font_color_lineEdit.setReadOnly(True)
        self.font_color_lineEdit.setObjectName("font_color_lineEdit")
        self.horizontalLayout.addWidget(self.font_color_lineEdit)
        self.font_color_button = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.font_color_button.sizePolicy().hasHeightForWidth())
        self.font_color_button.setSizePolicy(sizePolicy)
        self.font_color_button.setStyleSheet("")
        self.font_color_button.setObjectName("font_color_button")
        self.horizontalLayout.addWidget(self.font_color_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.font_size = QtGui.QDoubleSpinBox(self.groupBox)
        self.font_size.setSingleStep(0.5)
        self.font_size.setProperty("value", 3.5)
        self.font_size.setObjectName("font_size")
        self.horizontalLayout_6.addWidget(self.font_size)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Annotation)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.insert_symbol = QtGui.QToolButton(self.groupBox_2)
        self.insert_symbol.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.insert_symbol.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.insert_symbol.setAutoRaise(False)
        self.insert_symbol.setArrowType(QtCore.Qt.NoArrow)
        self.insert_symbol.setObjectName("insert_symbol")
        self.horizontalLayout_3.addWidget(self.insert_symbol)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.text_widget = QtGui.QPlainTextEdit(self.groupBox_2)
        self.text_widget.setFrameShadow(QtGui.QFrame.Sunken)
        self.text_widget.setObjectName("text_widget")
        self.verticalLayout_2.addWidget(self.text_widget)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_4.addWidget(self.label_6)
        self.horizontal_align = QtGui.QComboBox(self.groupBox_2)
        self.horizontal_align.setObjectName("horizontal_align")
        self.horizontal_align.addItem("")
        self.horizontal_align.addItem("")
        self.horizontal_align.addItem("")
        self.horizontal_align.addItem("")
        self.horizontalLayout_4.addWidget(self.horizontal_align)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7)
        self.orientation_angle = QtGui.QSpinBox(self.groupBox_2)
        self.orientation_angle.setMaximum(359)
        self.orientation_angle.setObjectName("orientation_angle")
        self.horizontalLayout_5.addWidget(self.orientation_angle)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(Annotation)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_10 = QtGui.QLabel(self.groupBox_3)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 2, 0, 1, 1)
        self.leader_side = QtGui.QComboBox(self.groupBox_3)
        self.leader_side.setObjectName("leader_side")
        self.leader_side.addItem("")
        self.leader_side.addItem("")
        self.gridLayout_4.addWidget(self.leader_side, 2, 1, 1, 1)
        self.leader_type = QtGui.QComboBox(self.groupBox_3)
        self.leader_type.setObjectName("leader_type")
        self.leader_type.addItem("")
        self.leader_type.addItem("")
        self.leader_type.addItem("")
        self.leader_type.addItem("")
        self.gridLayout_4.addWidget(self.leader_type, 1, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox_3)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 3, 0, 1, 1)
        self.leader_number = QtGui.QSpinBox(self.groupBox_3)
        self.leader_number.setMinimum(1)
        self.leader_number.setProperty("value", 1)
        self.leader_number.setObjectName("leader_number")
        self.gridLayout_4.addWidget(self.leader_number, 0, 1, 1, 1)
        self.leader_valign = QtGui.QComboBox(self.groupBox_3)
        self.leader_valign.setObjectName("leader_valign")
        self.leader_valign.addItem("")
        self.leader_valign.addItem("")
        self.leader_valign.addItem("")
        self.gridLayout_4.addWidget(self.leader_valign, 3, 1, 1, 1)
        self.label_11 = QtGui.QLabel(self.groupBox_3)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 0, 0, 1, 1)
        self.label_12 = QtGui.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 4, 0, 1, 1)
        self.leader_head = QtGui.QComboBox(self.groupBox_3)
        self.leader_head.setObjectName("leader_head")
        self.leader_head.addItem("")
        self.leader_head.addItem("")
        self.leader_head.addItem("")
        self.gridLayout_4.addWidget(self.leader_head, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)

        self.retranslateUi(Annotation)
        QtCore.QMetaObject.connectSlotsByName(Annotation)

    def retranslateUi(self, Annotation):
        Annotation.setWindowTitle(QtGui.QApplication.translate("Annotation", "Annotation", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Annotation", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Annotation", "Family", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Annotation", "Color (RGBA)", None, QtGui.QApplication.UnicodeUTF8))
        self.font_color_lineEdit.setText(QtGui.QApplication.translate("Annotation", "255; 255; 255; 255", None, QtGui.QApplication.UnicodeUTF8))
        self.font_color_button.setText(QtGui.QApplication.translate("Annotation", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Annotation", "Size", None, QtGui.QApplication.UnicodeUTF8))
        self.font_size.setSuffix(QtGui.QApplication.translate("Annotation", " mm", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Annotation", "Content", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Annotation", "Text", None, QtGui.QApplication.UnicodeUTF8))
        self.insert_symbol.setText(QtGui.QApplication.translate("Annotation", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.text_widget.setPlainText(QtGui.QApplication.translate("Annotation", "Note", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Annotation", "Horizontal align", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontal_align.setItemText(0, QtGui.QApplication.translate("Annotation", "Left", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontal_align.setItemText(1, QtGui.QApplication.translate("Annotation", "Center", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontal_align.setItemText(2, QtGui.QApplication.translate("Annotation", "Right", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontal_align.setItemText(3, QtGui.QApplication.translate("Annotation", "Justify", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Annotation", "Orientation angle", None, QtGui.QApplication.UnicodeUTF8))
        self.orientation_angle.setSuffix(QtGui.QApplication.translate("Annotation", " °", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Annotation", "Leader line", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Annotation", "Side", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_side.setItemText(0, QtGui.QApplication.translate("Annotation", "Left", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_side.setItemText(1, QtGui.QApplication.translate("Annotation", "Right", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_type.setItemText(0, QtGui.QApplication.translate("Annotation", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_type.setItemText(1, QtGui.QApplication.translate("Annotation", "Straight Leader", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_type.setItemText(2, QtGui.QApplication.translate("Annotation", "Bent Leader", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_type.setItemText(3, QtGui.QApplication.translate("Annotation", "End Bent Leader", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Annotation", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Annotation", "Vertical align", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_valign.setItemText(0, QtGui.QApplication.translate("Annotation", "Top", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_valign.setItemText(1, QtGui.QApplication.translate("Annotation", "Center", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_valign.setItemText(2, QtGui.QApplication.translate("Annotation", "Bottom", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Annotation", "Number", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Annotation", "Head", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_head.setItemText(0, QtGui.QApplication.translate("Annotation", "Arrow", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_head.setItemText(1, QtGui.QApplication.translate("Annotation", "Dot", None, QtGui.QApplication.UnicodeUTF8))
        self.leader_head.setItemText(2, QtGui.QApplication.translate("Annotation", "None", None, QtGui.QApplication.UnicodeUTF8))

