from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QFileDialog
import os
import json
from .json_settings import JsonSettings

class Ui_SettingsPickerDialog(object):
    def setupUi(self, SettingsPickerDialog):
        SettingsPickerDialog.setObjectName("SettingsPickerDialog")
        SettingsPickerDialog.setFixedSize(400, 500)

        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsPickerDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.labelRasterInliersExtractor = QtWidgets.QLabel("Path for \"raster_inliers_extractor\":", SettingsPickerDialog)
        self.labelRasterInliersExtractor.setObjectName("labelRasterInliersExtractor")
        self.verticalLayout.addWidget(self.labelRasterInliersExtractor)

        self.lineEditRasterInliersExtractor = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditRasterInliersExtractor.setObjectName("lineEditRasterInliersExtractor")
        self.verticalLayout.addWidget(self.lineEditRasterInliersExtractor)

        self.pushButtonBrowseRasterInliersExtractor = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseRasterInliersExtractor.setObjectName("pushButtonBrowseRasterInliersExtractor")
        self.verticalLayout.addWidget(self.pushButtonBrowseRasterInliersExtractor)

        self.separator1 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator1.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator1)

        self.labelObjectsBoundsFinder = QtWidgets.QLabel("Path for \"objects_bounds_finder\":", SettingsPickerDialog)
        self.labelObjectsBoundsFinder.setObjectName("labelObjectsBoundsFinder")
        self.verticalLayout.addWidget(self.labelObjectsBoundsFinder)

        self.lineEditObjectsBoundsFinder = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditObjectsBoundsFinder.setObjectName("lineEditObjectsBoundsFinder")
        self.verticalLayout.addWidget(self.lineEditObjectsBoundsFinder)

        self.pushButtonBrowseObjectsBoundsFinder = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseObjectsBoundsFinder.setObjectName("pushButtonBrowseObjectsBoundsFinder")
        self.verticalLayout.addWidget(self.pushButtonBrowseObjectsBoundsFinder)

        self.separator2 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator2.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator2)

        self.labelRoofLocator = QtWidgets.QLabel("Path for \"roof_locator\":", SettingsPickerDialog)
        self.labelRoofLocator.setObjectName("labelRoofLocator")
        self.verticalLayout.addWidget(self.labelRoofLocator)

        self.lineEditRoofLocator = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditRoofLocator.setObjectName("lineEditRoofLocator")
        self.verticalLayout.addWidget(self.lineEditRoofLocator)

        self.pushButtonBrowseRoofLocator = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseRoofLocator.setObjectName("pushButtonBrowseRoofLocator")
        self.verticalLayout.addWidget(self.pushButtonBrowseRoofLocator)

        self.separator3 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator3.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator3)

        self.labelMultiviewBuildingReconstructor = QtWidgets.QLabel("Path for \"multiview_building_reconstructor\":", SettingsPickerDialog)
        self.labelMultiviewBuildingReconstructor.setObjectName("labelMultiviewBuildingReconstructor")
        self.verticalLayout.addWidget(self.labelMultiviewBuildingReconstructor)

        self.lineEditMultiviewBuildingReconstructor = QtWidgets.QLineEdit(SettingsPickerDialog)
        self.lineEditMultiviewBuildingReconstructor.setObjectName("lineEditMultiviewBuildingReconstructor")
        self.verticalLayout.addWidget(self.lineEditMultiviewBuildingReconstructor)

        self.pushButtonBrowseMultiviewBuildingReconstructor = QtWidgets.QPushButton("Browse...", SettingsPickerDialog)
        self.pushButtonBrowseMultiviewBuildingReconstructor.setObjectName("pushButtonBrowseMultiviewBuildingReconstructor")
        self.verticalLayout.addWidget(self.pushButtonBrowseMultiviewBuildingReconstructor)

        self.separator4 = QtWidgets.QFrame(SettingsPickerDialog)
        self.separator4.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.separator4)

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

        self.ui.lineEditRasterInliersExtractor.setText(self.settings.value("raster_inliers_extractor", ""))
        self.ui.lineEditObjectsBoundsFinder.setText(self.settings.value("objects_bounds_finder", ""))
        self.ui.lineEditRoofLocator.setText(self.settings.value("roof_locator", ""))
        self.ui.lineEditMultiviewBuildingReconstructor.setText(self.settings.value("multiview_building_reconstructor", ""))
        self.ui.lineEditResultFolder.setText(self.settings.value("result_folder", ""))

        self.ui.pushButtonBrowseRasterInliersExtractor.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditRasterInliersExtractor, "raster_inliers_extractor"))
        self.ui.pushButtonBrowseObjectsBoundsFinder.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditObjectsBoundsFinder, "objects_bounds_finder"))
        self.ui.pushButtonBrowseRoofLocator.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditRoofLocator, "roof_locator"))
        self.ui.pushButtonBrowseMultiviewBuildingReconstructor.clicked.connect(
            lambda: self.browse_file(self.ui.lineEditMultiviewBuildingReconstructor, "multiview_building_reconstructor"))
        self.ui.pushButtonBrowseResultFolder.clicked.connect(
            lambda: self.browse_folder(self.ui.lineEditResultFolder, "result_folder"))

    def browse_file(self, line_edit, key):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            line_edit.setText(file_path)
            self.settings.setValue(key, file_path)

    def browse_folder(self, line_edit, key):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            line_edit.setText(folder_path)
            self.settings.setValue(key, folder_path)
