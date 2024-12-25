import os
import subprocess
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject

from .draw_work_region_tool import DrawWorkRegionTool
from .json_settings import JsonSettings
from .work_area_manager import WorkAreaManager


class Ui_CreateWorkAreaDialog(object):
    def setupUi(self, CreateWorkAreaDialog):
        CreateWorkAreaDialog.setObjectName("CreateWorkAreaDialog")
        CreateWorkAreaDialog.setFixedSize(475, 500)
        self.verticalLayout = QVBoxLayout(CreateWorkAreaDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(10)

        # Title label
        self.labelTitle = QLabel("Create Work Area", CreateWorkAreaDialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.labelTitle.setFont(font)
        self.verticalLayout.addWidget(self.labelTitle)

        # Name input
        self.labelName = QLabel("1. Work Area Name", CreateWorkAreaDialog)
        self.verticalLayout.addWidget(self.labelName)
        self.lineEditName = QLineEdit(CreateWorkAreaDialog)
        self.verticalLayout.addWidget(self.lineEditName)
        self.pushButtonSaveName = QPushButton("Save Name", CreateWorkAreaDialog)
        self.verticalLayout.addWidget(self.pushButtonSaveName)

        # Image upload section (initially disabled)
        self.labelImages = QLabel("2. Add Images", CreateWorkAreaDialog)
        self.verticalLayout.addWidget(self.labelImages)

        self.imageLayouts = []
        self.imageLabels = []
        self.addImageButtons = []

        for i in range(5):
            imageLayout = QHBoxLayout()
            imageLabel = QLabel(CreateWorkAreaDialog)
            imageLabel.setFixedWidth(200)
            self.imageLabels.append(imageLabel)
            addImageButton = QPushButton("Browse Image...", CreateWorkAreaDialog)
            self.addImageButtons.append(addImageButton)

            imageLayout.addWidget(imageLabel)
            imageLayout.addWidget(addImageButton)

            self.imageLayouts.append(imageLayout)
            self.verticalLayout.addLayout(imageLayout)
            addImageButton.setEnabled(False)  # Disable image buttons initially

        # Work area drawing (initially disabled)
        self.labelWorkArea = QLabel("3. Specify Work Area", CreateWorkAreaDialog)
        self.verticalLayout.addWidget(self.labelWorkArea)

        self.horizontalLayoutWorkArea = QHBoxLayout()
        self.labelWorkAreaPath = QLabel(CreateWorkAreaDialog)
        self.labelWorkAreaPath.setFixedWidth(200)
        self.horizontalLayoutWorkArea.addWidget(self.labelWorkAreaPath)
        self.pushButtonWorkArea = QPushButton("Draw...", CreateWorkAreaDialog)
        self.horizontalLayoutWorkArea.addWidget(self.pushButtonWorkArea)
        self.verticalLayout.addLayout(self.horizontalLayoutWorkArea)
        self.pushButtonWorkArea.setEnabled(False)  # Disable initially

        # Save and Calculate buttons (initially disabled)
        self.pushButtonSave = QPushButton("Save", CreateWorkAreaDialog)
        self.pushButtonSave.setStyleSheet("background-color: lightblue;")
        self.verticalLayout.addWidget(self.pushButtonSave)
        self.pushButtonSave.setEnabled(False)  # Disable initially

        self.pushButtonCalculate = QPushButton("Start workflow", CreateWorkAreaDialog)
        self.pushButtonCalculate.setStyleSheet("background-color: lightgreen;")
        self.verticalLayout.addWidget(self.pushButtonCalculate)
        self.pushButtonCalculate.setEnabled(False)  # Disable initially

        QtCore.QMetaObject.connectSlotsByName(CreateWorkAreaDialog)


class CreateWorkAreaDialog(QDialog):
    def __init__(self, work_area, iface, parent=None):
        super().__init__(parent)
        self.ui = Ui_CreateWorkAreaDialog()
        self.ui.setupUi(self)
        self.work_area = work_area
        self.iface = iface
        self.work_area_manager = WorkAreaManager(os.path.dirname(__file__))
        self.images_paths = self.ensure_five_elements(work_area.images_paths)
        self.image_layers = [None] * 5
        self.settings = JsonSettings()

        # Если рабочая зона уже имеет имя, разблокируем интерфейс
        if self.work_area.name:
            self.load_work_area_data()
            self.ui.lineEditName.setText(self.work_area.name)
            self.ui.lineEditName.setEnabled(False)  # Блокируем изменение имени
            self.ui.pushButtonSaveName.setVisible(False)  # Скрываем кнопку сохранения имени
            self.block_ui_elements(False)  # Разблокируем остальные элементы
        else:
            self.block_ui_elements(True)  # Блокируем элементы, пока не будет введено имя
            self.ui.pushButtonSaveName.clicked.connect(self.save_name)

        for i in range(5):
            self.ui.addImageButtons[i].clicked.connect(lambda checked, idx=i: self.select_image(idx))

        self.ui.pushButtonWorkArea.clicked.connect(self.handle_start_button_click)
        self.ui.pushButtonSave.clicked.connect(self.save_work_area)
        self.ui.pushButtonCalculate.clicked.connect(self.calculate)

    def ensure_five_elements(self, arr):
        while len(arr) < 5:
            arr.append("")
        return arr[:5]

    def block_ui_elements(self, block):
        """Blocks or unblocks UI elements based on the 'block' argument."""
        elements = [self.ui.pushButtonWorkArea, self.ui.pushButtonSave, self.ui.pushButtonCalculate]
        for i in range(5):
            elements.append(self.ui.addImageButtons[i])

        for element in elements:
            element.setEnabled(not block)

    def save_name(self):
        name = self.ui.lineEditName.text()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid name.")
            return
        if self.work_area_manager.work_area_exists_by_name(name):
            QMessageBox.warning(self, "Invalid Name", f"Work area with name '{name}' already exists.")
            return
        self.ui.lineEditName.setEnabled(False)  # Блокируем изменение имени
        self.ui.pushButtonSaveName.setVisible(False)  # Скрываем кнопку сохранения имени
        self.work_area.name = name
        self.work_area_manager.update_work_area(self.work_area)

        # Enable all other elements now that the name has been set
        self.block_ui_elements(False)

    def load_work_area_data(self):
        self.ui.lineEditName.setText(self.work_area.name)
        for i in range(5):
            if i < len(self.work_area.images_paths):
                image_path = self.work_area.images_paths[i]
                if image_path:
                    image_name = os.path.basename(image_path)
                    self.ui.imageLabels[i].setText(self.elide_text(image_name))
                    if not self.is_layer_loaded(image_path, i):
                        self.load_raster_layer(image_path, i)
        # Разблокируем интерфейс после загрузки существующей зоны
        self.ui.labelWorkAreaPath.setText(self.elide_text(self.work_area.work_area_path))
        self.block_ui_elements(False)

    def select_image(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.tiff *.tif *.png *.jpg *.jpeg)")
        if file_path in self.images_paths:
            QMessageBox.warning(self, "Duplicate Image",
                                "This image has already been added. Please select a different image.")
            self.bring_to_front()
            return

        if file_path:
            self.images_paths[index] = file_path
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

    def handle_start_button_click(self):
        self.tool = DrawWorkRegionTool(self.iface.mapCanvas(), self.iface, self.work_area, self)
        self.iface.mapCanvas().setMapTool(self.tool)
        self.show_qgis_main_window()

    def save_work_area(self):
        self.work_area.images_paths = self.images_paths
        self.work_area_manager.update_work_area(self.work_area)
        print(f"Work area '{self.work_area.name}' has been saved.")

    def calculate(self):
        # Проверка на наличие хотя бы одного изображения
        not_empty_images_paths = [path for path in self.images_paths if path]

        if not not_empty_images_paths:
            QMessageBox.warning(self, "Validation Error", "Please select at least one image.")
            return

        # Проверка на наличие рабочей области
        if not self.work_area.work_area_path:
            QMessageBox.warning(self, "Validation Error", "Please specify the work area.")
            return

        # Проверка на наличие всех обязательных настроек
        if not self.settings.value('python_script'):
            QMessageBox.warning(self, "Validation Error", "Python script path is missing.")
            return

        if not self.settings.value('weights'):
            QMessageBox.warning(self, "Validation Error", "Weights path is missing.")
            return

        if not self.settings.value('result_folder'):
            QMessageBox.warning(self, "Validation Error", "Result folder path is missing.")
            return

        self.save_work_area()
        self.delete_old_shapefiles()
        self.run_console_command()
        self.load_shapefile()
        self.accept()

    def delete_old_shapefiles(self):
        shapefiles = ['hydro']
        for shapefile in shapefiles:
            base_path = os.path.join(self.settings.value('result_folder'), self.work_area.name, shapefile)
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                file_path = base_path + ext
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Deleted {file_path}")
                    except OSError as e:
                        print(f"Error deleting {file_path}: {e}")

    def run_console_command(self):
        not_empty_images_paths = [path for path in self.images_paths if path]
        work_area_folder = os.path.join (self.settings.value('result_folder'), self.work_area.name)

        # Define the command to activate the Conda environment and run the script
        conda_activate_command = 'source ~/anaconda3/bin/activate'
        activate_env_command = 'conda activate open_rsai_detectors'
        deactivate_env_command = 'conda deactivate'
        script_path = f"{self.settings.value('python_script')}"
        script_args = [
            f"{work_area_folder}",
            f"{self.settings.value('weights')}",
            f"{self.work_area.work_area_path}",
            f"{' '.join(not_empty_images_paths)}"
        ]

        # Build the command to run
        command = f'{conda_activate_command} && {activate_env_command} && python {" ".join([script_path] + script_args)} && {deactivate_env_command}'

        # Use subprocess to run the command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            executable='/bin/bash'
        )

        # Communicate with the subprocess to get the output and errors
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f'Error: {stderr.decode().strip()}')
        else:
            print(f'Output: {stdout.decode().strip()}')

        print("console_command", command)

    def load_shapefile(self):
        result_folder = os.path.join(self.settings.value('result_folder'), self.work_area.name)
        hydro_shapefile_path = os.path.join(result_folder, 'hydro.shp')

        # Проверка наличия hydro.shp
        if os.path.exists(hydro_shapefile_path):
            self.load_vector_layer(hydro_shapefile_path, "Hydro Layer")
            print(f"hydro.shp loaded from {hydro_shapefile_path}")
        else:
            print(f"hydro.shp not found in {result_folder}")

    def load_vector_layer(self, shapefile_path, layer_name):
        """Загружает векторный слой из указанного файла."""
        vector_layer = QgsVectorLayer(shapefile_path, layer_name, "ogr")
        if not vector_layer.isValid():
            print(f"Failed to load {shapefile_path}")
            return
        QgsProject.instance().addMapLayer(vector_layer)
        print(f"{layer_name} loaded successfully.")

    def bring_to_front(self):
        self.activateWindow()
        self.raise_()

    def elide_text(self, text, max_width=200):
        font_metrics = QtGui.QFontMetrics(self.ui.labelName.font())
        return font_metrics.elidedText(text, QtCore.Qt.ElideMiddle, max_width)

    def is_layer_loaded(self, file_path, index):
        layer_name = os.path.basename(file_path)
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layer_name:
                self.image_layers[index] = layer
                return True
        return False

    def show_qgis_main_window(self):
        main_window = self.iface.mainWindow()
        main_window.activateWindow()
        main_window.raise_()
