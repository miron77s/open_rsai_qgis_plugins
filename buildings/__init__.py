import os.path

from PyQt5.QtWidgets import QAction, QDialog, QVBoxLayout, QPushButton, QMessageBox
from qgis.core import QgsProject

from .settings_picker_dialog import SettingsPickerDialog
from .work_areas_dialog import WorkAreasDialog
from .json_settings import JsonSettings

class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.settings = JsonSettings()

    def add_action(self, text, callback, enabled_flag=True, add_to_toolbar=True, status_tip=None, parent=None):
        action = QAction(text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        self.actions.append(action)
        return action

    def initGui(self):
        print("Initializing GUI")
        self.add_action(
            text='🏠',
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def run(self):
        print("Running plugin")
        self.dialog = MinimalDialog(self.iface, self.settings)
        self.dialog.setFixedSize(200, 100)
        self.dialog.show()

    def unload(self):
        print("Unloading plugin")
        for action in self.actions:
            self.iface.removeToolBarIcon(action)


class MinimalDialog(QDialog):
    def __init__(self, iface, settings, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.settings = settings
        self.setWindowTitle('Buildings Detector')
        layout = QVBoxLayout()

        self.create_sample_button = QPushButton('Workflow')
        self.settings_button = QPushButton('Settings')
        self.clear_layers_button = QPushButton('Clear Layers')

        layout.addWidget(self.create_sample_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.clear_layers_button)

        self.setLayout(layout)

        self.update_training_button_state()

        self.create_sample_button.clicked.connect(self.create_sample)
        self.settings_button.clicked.connect(self.open_settings)
        self.clear_layers_button.clicked.connect(self.clear_layers)

    def create_sample(self):
        self.close()
        self.work_areas_dialog = WorkAreasDialog(self.iface)
        self.work_areas_dialog.show()

    def open_settings(self):
        self.close()
        self.settings_dialog = SettingsPickerDialog(self)
        self.settings_dialog.exec_()
        self.update_training_button_state()
        self.show()

    def clear_layers(self):
        reply = QMessageBox.question(self, 'Confirm Clear Layers',
                                     'Are you sure you want to remove all layers?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            root = QgsProject.instance().layerTreeRoot()
            root.removeAllChildren()
        else:
            print("Clear layers canceled")

    def update_training_button_state(self):
        keys_to_check = ['raster_inliers_extractor', 'objects_bounds_finder', 'roof_locator', 'multiview_building_reconstructor', 'result_folder']
        if self.settings.check_keys_have_values(keys_to_check):
            self.create_sample_button.setEnabled(True)
        else:
            self.create_sample_button.setEnabled(False)


def classFactory(iface):
    return MinimalPlugin(iface)
