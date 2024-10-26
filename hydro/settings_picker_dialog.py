from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QFileDialog
import os
import json
from .json_settings import JsonSettings

class Ui_SettingsPickerDialog(object):
    def setupUi(self, SettingsPickerDialog):
        SettingsPickerDialog.setObjectName("SettingsPickerDialog")
        SettingsPickerDialog.setFixedSize(400, 300)

        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsPickerDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.labelPythonScript = QtWidgets.QLabel("Path for Python script:", SettingsPickerDialog)
        self.labelPythonScript.setObjectName("labelPythonScript")
        self.verticalLayout.addWidget(self.labelPythonScript)

        self.lineEditPythonScript = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditPythonScript.setObjectName("lineEditPythonScript")
        self.verticalLayout.addWidget(self.lineEditPythonScript)

        self.pushButtonBrowsePythonScript = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowsePythonScript.setObjectName("pushButtonBrowsePythonScript")
        self.verticalLayout.addWidget(self.pushButtonBrowsePythonScript)

        self.separator1 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator1.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator1)

        self.labelWeights = QtWidgets.QLabel("Path for weights:", SettingsPickerDialog)
        self.labelWeights.setObjectName("labelWeights")
        self.verticalLayout.addWidget(self.labelWeights)

        self.lineEditWeights = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditWeights.setObjectName("lineEditWeights")
        self.verticalLayout.addWidget(self.lineEditWeights)

        self.pushButtonBrowseWeights = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseWeights.setObjectName("pushButtonBrowseWeights")
        self.verticalLayout.addWidget(self.pushButtonBrowseWeights)

        self.separator2 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator2.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator2)

        self.labelResultFolder = QtWidgets.QLabel("Path for result folder:", SettingsPickerDialog)
        self.labelResultFolder.setObjectName("labelResultFolder")
        self.verticalLayout.addWidget(self.labelResultFolder)

        self.lineEditResultFolder = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditResultFolder.setObjectName("lineEditResultFolder")
        self.verticalLayout.addWidget(self.lineEditResultFolder)

        self.pushButtonBrowseResultFolder = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseResultFolder.setObjectName("pushButtonBrowseResultFolder")
        self.verticalLayout.addWidget(self.pushButtonBrowseResultFolder)

        QtCore.QMetaObject.connectSlotsByName(SettingsPickerDialog)


class SettingsPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsPickerDialog()
        self.ui.setupUi(self)
        self.settings = JsonSettings()

        self.ui.lineEditPythonScript.setText(self.settings.value("python_script", ""))
        self.ui.lineEditWeights.setText(self.settings.value("weights", ""))
        self.ui.lineEditResultFolder.setText(self.settings.value("result_folder", ""))

        self.ui.pushButtonBrowsePythonScript.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditPythonScript, "python_script"))
        self.ui.pushButtonBrowseWeights.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditWeights, "weights"))
        self.ui.pushButtonBrowseResultFolder.clicked.connect(
            lambda: self.browse_folder(self.ui.lineEditResultFolder, "result_folder"))

    def browse_file(self, line_edit, key):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            line_edit.setText(file_path)
            self.settings.setValue(key, file_path)

    def browse_folder(self, line_edit, key):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            line_edit.setText(folder_path)
            self.settings.setValue(key, folder_path)
