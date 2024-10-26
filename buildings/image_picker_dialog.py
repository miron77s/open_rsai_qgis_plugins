import json
import os
import re

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, \
    QSpacerItem, QSizePolicy
from qgis.PyQt.QtCore import Qt

from .json_settings import JsonSettings


class ImagePicker:
    def __init__(self, iface, root_folder, work_area_id):
        self.iface = iface
        self.work_area_id = work_area_id
        self.settings = JsonSettings()
        self.root_folder = root_folder
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = None
        self.map_label = None
        self.image_label = None
        self.progress_label_subfolder = None
        self.pushButton_select = None
        self.pushButton_skip_image = None
        self.pushButton_next_image = None
        self.pushButton_prev_image = None
        self.pushButton_toggle_original = None
        self.pushButton_next_folder = None
        self.pushButton_prev_folder = None
        self.all_subfolders = []
        self.current_subfolder_index = 0
        self.current_image_index = 0
        self.all_images = []
        self.selected_images = {}
        self.processed_subfolders = set()
        self.showing_original = False
        self.selection_file_path = os.path.join(self.root_folder,
                                                'selection_results.json')

        self.load_subfolders()
        self.show_image_picker()

    def load_subfolders(self):
        for map_folder in os.listdir(self.root_folder):
            map_folder_path = os.path.join(self.root_folder, map_folder)
            if not os.path.isdir(map_folder_path):
                continue

            variants_roofs_folder = os.path.join(map_folder_path, "variants", "roofs")
            if os.path.exists(variants_roofs_folder):
                roof_folders = sorted(
                    [os.path.join(variants_roofs_folder, d) for d in os.listdir(variants_roofs_folder) if
                     os.path.isdir(os.path.join(variants_roofs_folder, d))],
                    key=self.natural_sort_key)

                for roof_folder in roof_folders:
                    self.all_subfolders.append({"map_folder": map_folder, "subfolder": roof_folder})

        print(f"All subfolders with images loaded: {self.all_subfolders}")

    def show_image_picker(self):
        if len(self.all_subfolders) == 0:
            return
        if not self.dlg:
            self.dlg = QDialog(self.iface.mainWindow())
            self.dlg.setFixedSize(500, 700)
            self.dlg.setWindowFlags(
                Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
            self.widget = QWidget()
            self.layout = QVBoxLayout(self.widget)

            self.map_label = QLabel(self.widget)
            self.map_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.map_label)

            self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.image_label = QLabel(self.widget)
            self.image_label.setFixedSize(400, 400)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.image_label, 0, Qt.AlignCenter)

            self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.progress_label_subfolder = QLabel(self.widget)
            self.progress_label_subfolder.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.progress_label_subfolder)

            self.button_layout = QHBoxLayout()
            self.pushButton_prev_image = QPushButton("<", self.widget)
            self.pushButton_prev_image.clicked.connect(self.prev_image)
            self.button_layout.addWidget(self.pushButton_prev_image)

            self.pushButton_next_image = QPushButton(">", self.widget)
            self.pushButton_next_image.clicked.connect(self.next_image)
            self.button_layout.addWidget(self.pushButton_next_image)

            self.layout.addLayout(self.button_layout)

            self.pushButton_select = QPushButton("Select Image", self.widget)
            self.pushButton_select.clicked.connect(self.select_image)
            self.layout.addWidget(self.pushButton_select)

            self.pushButton_skip_image = QPushButton("Skip Image", self.widget)
            self.pushButton_skip_image.clicked.connect(self.skip_image)
            self.layout.addWidget(self.pushButton_skip_image)

            self.pushButton_toggle_original = QPushButton("Show Original", self.widget)
            self.pushButton_toggle_original.clicked.connect(self.toggle_original)
            self.layout.addWidget(self.pushButton_toggle_original)

            folder_button_layout = QHBoxLayout()
            self.pushButton_prev_folder = QPushButton("Previous Folder", self.widget)
            self.pushButton_prev_folder.clicked.connect(self.prev_subfolder)
            folder_button_layout.addWidget(self.pushButton_prev_folder)

            self.pushButton_next_folder = QPushButton("Next Folder", self.widget)
            self.pushButton_next_folder.clicked.connect(self.next_subfolder)
            folder_button_layout.addWidget(self.pushButton_next_folder)

            self.layout.addLayout(folder_button_layout)

            self.dlg.setLayout(self.layout)

        self.update_ui()
        self.dlg.exec_()

    def update_ui(self):
        self.update_map_label()
        self.update_images()

    def update_map_label(self):
        current_entry = self.all_subfolders[self.current_subfolder_index]
        map_folder = current_entry["map_folder"]
        self.map_label.setText(f"Current Map: {map_folder}")

    def update_images(self):
        if self.current_subfolder_index < len(self.all_subfolders):
            current_entry = self.all_subfolders[self.current_subfolder_index]
            current_subfolder = current_entry["subfolder"]
            images = [os.path.join(current_subfolder, f) for f in os.listdir(current_subfolder) if
                      f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')) and f.lower() != 'src.jpg']
            self.all_images = sorted(images, key=self.natural_sort_key)

            self.update_map_label()

            if not self.all_images:
                self.next_subfolder()
            else:
                self.current_image_index = 0
                self.show_image()

    def show_image(self):
        if self.all_images:
            image_path = self.all_images[self.current_image_index]
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(
                pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.progress_label_subfolder.setText(
                f"Subfolder {self.current_subfolder_index + 1}/{len(self.all_subfolders)} - "
                f"Image: {self.current_image_index + 1}/{len(self.all_images)}")

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.all_images)
        self.show_image()

    def prev_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.all_images)
        self.show_image()

    def skip_image(self):
        current_entry = self.all_subfolders[self.current_subfolder_index]
        map_folder = current_entry["map_folder"]
        subfolder = current_entry["subfolder"]

        if map_folder not in self.selected_images:
            self.selected_images[map_folder] = {}

        self.selected_images[map_folder][subfolder] = "skipped"

        self.processed_subfolders.add(self.current_subfolder_index)
        self.check_all_subfolders_processed()
        self.next_subfolder()

    def select_image(self):
        if self.all_images:
            selected_image_path = self.all_images[self.current_image_index]
            current_entry = self.all_subfolders[self.current_subfolder_index]
            map_folder = current_entry["map_folder"]
            subfolder = current_entry["subfolder"]

            if map_folder not in self.selected_images:
                self.selected_images[map_folder] = {}

            self.selected_images[map_folder][subfolder] = selected_image_path

        self.processed_subfolders.add(self.current_subfolder_index)
        self.check_all_subfolders_processed()

        self.next_subfolder()

    def next_subfolder(self):
        self.current_subfolder_index = (self.current_subfolder_index + 1) % len(self.all_subfolders)
        self.update_ui()

    def prev_subfolder(self):
        self.current_subfolder_index = (self.current_subfolder_index - 1) % len(self.all_subfolders)
        self.update_ui()

    def check_all_subfolders_processed(self):
        if len(self.processed_subfolders) == len(self.all_subfolders):
            print("All subfolders processed.")
            self.save_selection()
            self.dlg.accept()

    def toggle_original(self):
        current_entry = self.all_subfolders[self.current_subfolder_index]
        original_image_path = os.path.join(current_entry["subfolder"], "src.jpg")

        if os.path.exists(original_image_path):
            if not self.showing_original:
                pixmap = QPixmap(original_image_path)
                self.image_label.setPixmap(
                    pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.pushButton_toggle_original.setText("Hide Original")
                self.showing_original = True
            else:
                self.show_image()
                self.pushButton_toggle_original.setText("Show Original")
                self.showing_original = False
        else:
            print(f"Original image {original_image_path} not found")

    def save_selection(self):
        json_path = os.path.join(self.root_folder, 'selection_results.json')
        selection_data = []

        for map_folder, subfolders in self.selected_images.items():
            for subfolder, status_or_image in subfolders.items():
                if status_or_image != "skipped":
                    entry = {
                        "map_folder": map_folder,
                        "image_path": status_or_image
                    }
                    selection_data.append(entry)

        with open(json_path, 'w') as f:
            json.dump(selection_data, f, indent=4)
        print(f"Selection saved to {json_path}")

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]
