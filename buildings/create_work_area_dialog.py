import os
import re

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout, \
    QCheckBox, QMessageBox
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject

from .draw_vectors_tools import DrawRedVectorTool
from .draw_work_region_tool import DrawWorkRegionTool
from .run_console_command_tool import ConsoleCommandTool
from .work_area_manager import WorkAreaManager


class Ui_CreateWorkAreaDialog(object):
    def setupUi(self, CreateWorkAreaDialog):
        CreateWorkAreaDialog.setObjectName("CreateWorkAreaDialog")
        CreateWorkAreaDialog.setFixedSize(475, 825)
        self.verticalLayout = QVBoxLayout(CreateWorkAreaDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(10)

        self.labelTitle = QLabel("Create Work Area", CreateWorkAreaDialog)
        self.labelTitle.setObjectName("labelTitle")
        font = QtGui.QFont()
        font.setPointSize(16)
        self.labelTitle.setFont(font)
        self.verticalLayout.addWidget(self.labelTitle)

        self.labelName = QLabel("1. Work Area Name", CreateWorkAreaDialog)
        self.labelName.setObjectName("labelName")
        self.verticalLayout.addWidget(self.labelName)

        self.lineEditName = QLineEdit(CreateWorkAreaDialog)
        self.lineEditName.setObjectName("lineEditName")
        self.verticalLayout.addWidget(self.lineEditName)

        self.pushButtonSaveName = QPushButton("Save Name", CreateWorkAreaDialog)
        self.pushButtonSaveName.setObjectName("pushButtonSaveName")
        self.verticalLayout.addWidget(self.pushButtonSaveName)

        self.labelImages = QLabel("2. Add Images and Draw Vectors", CreateWorkAreaDialog)
        self.labelImages.setObjectName("labelImages")
        self.verticalLayout.addWidget(self.labelImages)

        self.imageLayouts = []
        self.imageLabels = []
        self.vectorDrawButtons = []
        self.addImageButtons = []
        self.vectorCheckboxes = []

        for i in range(5):
            imageLayout = QHBoxLayout()
            imageLabel = QLabel(CreateWorkAreaDialog)
            imageLabel.setObjectName(f"labelImagePath_{i}")
            imageLabel.setFixedWidth(200)
            self.imageLabels.append(imageLabel)
            addImageButton = QPushButton("Browse Image...", CreateWorkAreaDialog)
            addImageButton.setObjectName(f"pushButtonImage_{i}")
            self.addImageButtons.append(addImageButton)

            drawVectorButton = QPushButton("Draw Vector...", CreateWorkAreaDialog)
            drawVectorButton.setObjectName(f"pushButtonDrawVector_{i}")
            self.vectorDrawButtons.append(drawVectorButton)

            vectorCheckbox = QCheckBox(CreateWorkAreaDialog)
            vectorCheckbox.setObjectName(f"checkBoxVector_{i}")
            vectorCheckbox.setEnabled(False)
            self.vectorCheckboxes.append(vectorCheckbox)

            imageLayout.addWidget(imageLabel)
            imageLayout.addWidget(addImageButton)
            imageLayout.addWidget(drawVectorButton)
            imageLayout.addWidget(vectorCheckbox)

            self.imageLayouts.append(imageLayout)
            self.verticalLayout.addLayout(imageLayout)

        self.labelWorkArea = QLabel("3. Specify Work Area", CreateWorkAreaDialog)
        self.labelWorkArea.setObjectName("labelWorkArea")
        self.verticalLayout.addWidget(self.labelWorkArea)

        self.horizontalLayoutWorkArea = QHBoxLayout()
        self.labelWorkAreaPath = QLabel(CreateWorkAreaDialog)
        self.labelWorkAreaPath.setObjectName("labelWorkAreaPath")
        self.labelWorkAreaPath.setFixedWidth(200)
        self.horizontalLayoutWorkArea.addWidget(self.labelWorkAreaPath)
        self.pushButtonWorkArea = QPushButton("Draw...", CreateWorkAreaDialog)
        self.pushButtonWorkArea.setObjectName("pushButtonWorkArea")
        self.horizontalLayoutWorkArea.addWidget(self.pushButtonWorkArea)
        self.verticalLayout.addLayout(self.horizontalLayoutWorkArea)

        self.labelMode = QLabel("4. Work Mode", CreateWorkAreaDialog)
        self.labelMode.setObjectName("labelMode")
        self.verticalLayout.addWidget(self.labelMode)

        self.comboBoxMode = QComboBox(CreateWorkAreaDialog)
        self.comboBoxMode.setObjectName("comboBoxMode")
        self.comboBoxMode.addItems(["Manual", "Automatic", "Semiautomatic"])
        self.verticalLayout.addWidget(self.comboBoxMode)

        self.labelVectors = QLabel("5. Select Reference Map (OSM)", CreateWorkAreaDialog)
        self.labelVectors.setObjectName("labelVectors")
        self.verticalLayout.addWidget(self.labelVectors)

        self.horizontalLayoutVectors = QHBoxLayout()
        self.labelVectorsPath = QLabel(CreateWorkAreaDialog)
        self.labelVectorsPath.setObjectName("labelVectorsPath")
        self.labelVectorsPath.setFixedWidth(200)
        self.labelVectorsPath.setText("")
        self.horizontalLayoutVectors.addWidget(self.labelVectorsPath)
        self.pushButtonVectors = QPushButton("Browse OSM...", CreateWorkAreaDialog)
        self.pushButtonVectors.setObjectName("pushButtonVectors")
        self.horizontalLayoutVectors.addWidget(self.pushButtonVectors)
        self.verticalLayout.addLayout(self.horizontalLayoutVectors)

        self.horizontalLayoutSegmentAnything = QHBoxLayout()
        self.useSegmentAnythingCheckbox = QCheckBox(CreateWorkAreaDialog)
        self.useSegmentAnythingCheckbox.setObjectName("useSegmentAnythingCheckbox")
        self.labelSegmentAnything = QLabel("Use Neural Networks", CreateWorkAreaDialog)

        self.horizontalLayoutSegmentAnything.addWidget(self.useSegmentAnythingCheckbox)
        self.horizontalLayoutSegmentAnything.addWidget(self.labelSegmentAnything)
        self.horizontalLayoutSegmentAnything.addStretch()
        self.verticalLayout.addLayout(self.horizontalLayoutSegmentAnything)

        self.horizontalLayoutPredict = QHBoxLayout()
        self.predictCheckbox = QCheckBox(CreateWorkAreaDialog)
        self.predictCheckbox.setObjectName("predictCheckbox")
        self.labelPredict = QLabel("Make Predict", CreateWorkAreaDialog)

        self.horizontalLayoutPredict.addWidget(self.predictCheckbox)
        self.horizontalLayoutPredict.addWidget(self.labelPredict)
        self.horizontalLayoutPredict.addStretch()
        self.verticalLayout.addLayout(self.horizontalLayoutPredict)

        self.pushButtonSave = QPushButton("Save", CreateWorkAreaDialog)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.pushButtonSave.setStyleSheet("background-color: lightblue;")
        self.verticalLayout.addWidget(self.pushButtonSave)

        self.pushButtonCalculate = QPushButton("Start workflow", CreateWorkAreaDialog)
        self.pushButtonCalculate.setObjectName("pushButtonCalculate")
        self.pushButtonCalculate.setStyleSheet("background-color: lightgreen;")
        self.verticalLayout.addWidget(self.pushButtonCalculate)

        QtCore.QMetaObject.connectSlotsByName(CreateWorkAreaDialog)


class CreateWorkAreaDialog(QDialog):
    def __init__(self, work_area, iface, parent=None):
        super().__init__(parent)
        self.ui = Ui_CreateWorkAreaDialog()
        self.ui.setupUi(self)
        self.work_area = work_area
        self.iface = iface
        self.work_area_manager = WorkAreaManager(os.path.dirname(__file__))
        self.work_area_manager.load_work_areas()

        self.image_paths = self.ensure_five_elements(work_area.image_path)
        self.vector_paths = self.ensure_five_elements(work_area.vector_path)
        self.image_layers = [None] * 5

        if self.work_area.name:
            self.load_work_area_data()
            self.ui.lineEditName.setText(self.work_area.name)
            self.ui.lineEditName.setEnabled(False)
            self.ui.pushButtonSaveName.setVisible(False)
            self.block_ui_elements(False)
        else:
            self.block_ui_elements(True)

        self.ui.pushButtonSaveName.clicked.connect(self.save_name)

        for i in range(5):
            self.ui.addImageButtons[i].clicked.connect(lambda checked, idx=i: self.select_image(idx))
            self.ui.vectorDrawButtons[i].clicked.connect(lambda checked, idx=i: self.draw_vector(idx))

        self.ui.pushButtonWorkArea.clicked.connect(self.handle_start_button_click)
        self.ui.pushButtonCalculate.clicked.connect(self.validate_and_calculate)
        self.ui.pushButtonSave.clicked.connect(self.save_work_area)
        self.ui.pushButtonVectors.clicked.connect(self.select_vector)

        self.ui.comboBoxMode.currentIndexChanged.connect(self.update_work_mode)

    def block_ui_elements(self, block):
        elements = [
            self.ui.pushButtonWorkArea,
            self.ui.pushButtonCalculate,
            self.ui.pushButtonSave,
            self.ui.pushButtonVectors,
            self.ui.comboBoxMode,
            self.ui.useSegmentAnythingCheckbox,
            self.ui.predictCheckbox,
        ]
        for i in range(5):
            elements.append(self.ui.addImageButtons[i])
            elements.append(self.ui.vectorDrawButtons[i])
        for element in elements:
            element.setEnabled(not block)

    def save_name(self):
        name = self.ui.lineEditName.text()
        if not self.is_valid_name(name):
            QMessageBox.warning(self, "Invalid Name", "The name contains invalid characters or spaces.")
            return
        if self.work_area_manager.work_area_exists_by_name(name):
            QMessageBox.warning(self, "Invalid Name", f"Work area with name '{name}' already exists.")
            return

        self.ui.lineEditName.setEnabled(False)
        self.ui.pushButtonSaveName.setVisible(False)
        self.block_ui_elements(False)
        self.work_area.name = name
        self.work_area_manager.update_work_area(self.work_area)

    def is_valid_name(self, name):
        return bool(re.match(r'^[^\\/:*?"<>| ]+$', name))

    def ensure_five_elements(self, arr):
        while len(arr) < 5:
            arr.append("")
        return arr[:5]

    def load_work_area_data(self):
        self.ui.lineEditName.setText(self.work_area.name)
        for i in range(5):
            if i < len(self.work_area.image_path):
                image_path = self.work_area.image_path[i]
                if image_path:
                    image_name = os.path.basename(image_path)
                    self.ui.imageLabels[i].setText(self.elide_text(image_name))
                    if not self.is_layer_loaded(image_path, i):
                        self.load_raster_layer(image_path, i)
            if i < len(self.work_area.vector_path):
                if len(self.work_area.vector_path[i]) > 0:
                    self.ui.vectorCheckboxes[i].setChecked(True)

        self.ui.comboBoxMode.setCurrentText(self.work_area.work_mode)
        self.ui.labelWorkAreaPath.setText(self.elide_text(self.work_area.work_area))
        self.ui.labelVectorsPath.setText(self.elide_text(self.work_area.vectors) if self.work_area.vectors else "")
        self.ui.useSegmentAnythingCheckbox.setChecked(self.work_area.use_segment_anything)
        self.ui.predictCheckbox.setChecked(self.work_area.predict)

    def update_work_mode(self):
        self.work_area.work_mode = self.ui.comboBoxMode.currentText()

    def is_layer_loaded(self, file_path, index):
        layer_name = os.path.basename(file_path)
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layer_name:
                self.image_layers[index] = layer
                return True
        return False

    def validate_and_calculate(self):
        if not self.ui.labelWorkAreaPath.text():
            QMessageBox.warning(self, "Validation Error", "Please specify the work area.")
            return

        if not any(self.image_paths):
            QMessageBox.warning(self, "Validation Error", "Please select at least one image.")
            return

        for i in range(5):
            if self.image_paths[i] and not self.ui.vectorCheckboxes[i].isChecked():
                QMessageBox.warning(self, "Validation Error", f"Please draw a vector for image {i + 1}.")
                return

        if not self.ui.comboBoxMode.currentText():
            QMessageBox.warning(self, "Validation Error", "Please select a work mode.")
            return

        if not self.ui.labelVectorsPath.text():
            QMessageBox.warning(self, "Validation Error", "Please select at least one vector file.")
            return

        if self.ui.useSegmentAnythingCheckbox.isChecked():
            print("Use Segment Anything is enabled.")
        if self.ui.predictCheckbox.isChecked():
            print("Prediction mode is enabled.")

        self.calculate()

    def select_image(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.tiff *.tif *.png *.jpg *.jpeg)")
        if file_path in self.image_paths:
            QMessageBox.warning(self, "Duplicate Image",
                                "This image has already been added. Please select a different image.")
            self.bring_to_front()
            return
        if file_path:
            self.image_paths[index] = file_path
            image_name = os.path.basename(file_path)
            self.ui.imageLabels[index].setText(self.elide_text(image_name))
            self.load_raster_layer(file_path, index)
            self.bring_to_front()

    def load_raster_layer(self, file_path, index):
        layer_name = os.path.basename(file_path)
        raster_layer = QgsRasterLayer(file_path, layer_name)
        if not raster_layer.isValid():
            print(f"Failed to load raster layer: {file_path}")
            return
        QgsProject.instance().addMapLayer(raster_layer)
        self.image_layers[index] = raster_layer
        print(f"Raster layer loaded: {file_path}")

    def select_vector(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Vector", "", "Vectors (*.shp)")
        if file_path:
            self.work_area.vectors = file_path
            self.ui.labelVectorsPath.setText(self.elide_text(file_path))
            self.load_vector_layer(file_path)
            self.bring_to_front()

    def elide_text(self, text, max_width=200):
        font_metrics = QtGui.QFontMetrics(self.ui.labelName.font())
        return font_metrics.elidedText(text, QtCore.Qt.ElideMiddle, max_width)

    def load_vector_layer(self, file_path):
        layer_name = os.path.basename(file_path)
        vector_layer = QgsVectorLayer(file_path, layer_name, "ogr")
        if not vector_layer.isValid():
            print(f"Failed to load vector layer: {file_path}")
            return
        QgsProject.instance().addMapLayer(vector_layer)
        print(f"Vector layer loaded: {file_path}")

    def calculate(self):
        self.save_work_area()
        self.block_ui_elements(True)
        ConsoleCommandTool(self.work_area).execute(self.iface)
        self.remove_layers_by_name()
        self.accept()

    def remove_layers_by_name(self):
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if self.work_area.id in layer.name():
                QgsProject.instance().removeMapLayer(layer)
        self.iface.mapCanvas().refresh()

    def save_work_area(self):
        self.work_area.image_path = self.image_paths
        self.work_area.vector_path = self.vector_paths
        self.work_area.use_segment_anything = self.ui.useSegmentAnythingCheckbox.isChecked()
        self.work_area.predict = self.ui.predictCheckbox.isChecked()
        self.work_area.work_mode = self.ui.comboBoxMode.currentText()
        self.work_area_manager.update_work_area(self.work_area)
        print(f"Work area '{self.work_area.name}' has been saved.")

    def handle_start_button_click(self):
        self.tool = DrawWorkRegionTool(self.iface.mapCanvas(), self.iface, self.work_area, self)
        self.iface.mapCanvas().setMapTool(self.tool)
        self.show_qgis_main_window()

    def draw_vector(self, index):
        if not self.image_paths[index]:
            QMessageBox.warning(self, "No Image Selected", "Please select an image before drawing a vector.")
            return

        self.activate_image_layer(index)
        self.tool = DrawRedVectorTool(self.iface.mapCanvas(), self.iface, self.work_area, self, index)
        self.iface.mapCanvas().setMapTool(self.tool)
        self.show_qgis_main_window()

    def activate_image_layer(self, index):
        for layer in QgsProject.instance().mapLayers().values():
            active_image_id = self.image_layers[index].id()
            if layer.id() == active_image_id:
                QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
            else:
                QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)

    def bring_to_front(self):
        self.activateWindow()
        self.raise_()

    def show_qgis_main_window(self):
        main_window = self.iface.mainWindow()
        main_window.activateWindow()
        main_window.raise_()
