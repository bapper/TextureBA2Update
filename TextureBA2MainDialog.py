# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TextureBA2MainDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TextureBA2MainDialog(object):
    def setupUi(self, TextureBA2MainDialog):
        TextureBA2MainDialog.setObjectName("TextureBA2MainDialog")
        TextureBA2MainDialog.resize(800, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(TextureBA2MainDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(TextureBA2MainDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.progressFrame = QtWidgets.QFrame(self.splitter)
        self.progressFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.progressFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.progressFrame.setObjectName("progressFrame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.progressFrame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.progressLabel = QtWidgets.QLabel(self.progressFrame)
        self.progressLabel.setFocusPolicy(QtCore.Qt.NoFocus)
        self.progressLabel.setObjectName("progressLabel")
        self.verticalLayout_2.addWidget(self.progressLabel)
        self.progressTextEdit = QtWidgets.QTextEdit(self.progressFrame)
        self.progressTextEdit.setObjectName("progressTextEdit")
        self.verticalLayout_2.addWidget(self.progressTextEdit)
        self.logFrame = QtWidgets.QFrame(self.splitter)
        self.logFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.logFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.logFrame.setObjectName("logFrame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.logFrame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.logLabel = QtWidgets.QLabel(self.logFrame)
        self.logLabel.setObjectName("logLabel")
        self.verticalLayout_3.addWidget(self.logLabel)
        self.logTextEdit = QtWidgets.QTextEdit(self.logFrame)
        self.logTextEdit.setObjectName("logTextEdit")
        self.verticalLayout_3.addWidget(self.logTextEdit)
        self.verticalLayout.addWidget(self.splitter)
        self.frame = QtWidgets.QFrame(TextureBA2MainDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.enableButton = QtWidgets.QPushButton(self.frame)
        self.enableButton.setObjectName("enableButton")
        self.horizontalLayout.addWidget(self.enableButton)
        self.updateButton = QtWidgets.QPushButton(self.frame)
        self.updateButton.setObjectName("updateButton")
        self.horizontalLayout.addWidget(self.updateButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(TextureBA2MainDialog)
        QtCore.QMetaObject.connectSlotsByName(TextureBA2MainDialog)

    def retranslateUi(self, TextureBA2MainDialog):
        _translate = QtCore.QCoreApplication.translate
        TextureBA2MainDialog.setWindowTitle(_translate("TextureBA2MainDialog", "TextureBA2Update"))
        self.progressLabel.setText(_translate("TextureBA2MainDialog", "Progress"))
        self.logLabel.setText(_translate("TextureBA2MainDialog", "Output Log"))
        self.enableButton.setToolTip(_translate("TextureBA2MainDialog", "Enable disabled textures in mods directory"))
        self.enableButton.setText(_translate("TextureBA2MainDialog", "Enable Textures"))
        self.updateButton.setToolTip(_translate("TextureBA2MainDialog", "Update default game BA2 files from enabled mods directory textures"))
        self.updateButton.setText(_translate("TextureBA2MainDialog", "Update BA2s"))
        self.cancelButton.setToolTip(_translate("TextureBA2MainDialog", "Stop the process and exit"))
        self.cancelButton.setText(_translate("TextureBA2MainDialog", "Cancel"))
