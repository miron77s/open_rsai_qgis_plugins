import os
import re
import json
from PyQt5.QtGui import QPixmap
from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QGridLayout


class MultiImagePicker:
    def __init__(self, iface, root_folder, work_area_id):
        self.iface = iface
        self.work_area_id = work_area_id
        self.root_folder = root_folder
        self.dlg = None
        self.progress_label_subfolder = None
        self.pushButton_select = None
        self.pushButton_skip_image = None
        self.pushButton_next_image = None
        self.pushButton_prev_image = None
        self.pushButton_next_subfolder = None
        self.pushButton_prev_subfolder = None
        self.map_folders = []
        self.total_folders = 0
        self.image_matrix = []
        self.current_subfolder_index = 0
        self.current_image_index = 0
        self.selected_images = {}
        self.selection_file_path = os.path.join(self.root_folder, 'structure_selection_results.json')
        self.image_labels = []
        self.processed_subfolders = set()

        self.load_images_matrix()

        if not any(any(images for images in subfolder) for subfolder in self.image_matrix):
            print("No images found. Exiting.")
            return

        print(f"Total images loaded for processing: {sum(len(images) for subfolder in self.image_matrix for images in subfolder)}")
        self.show_image_picker()

    def load_images_matrix(self):
        root_contents = os.listdir(self.root_folder)
        self.map_folders = sorted(
            [os.path.join(self.root_folder, d) for d in root_contents if
             os.path.isdir(os.path.join(self.root_folder, d))],
            key=self.natural_sort_key)
        self.total_folders = len(self.map_folders)

        first_map_subfolders = []
        if self.total_folders > 0:
            first_map = self.map_folders[0]
            structures_path = os.path.join(first_map, "variants", "structures")

            if os.path.exists(structures_path):
                first_map_subfolders = sorted(
                    [d for d in os.listdir(structures_path) if
                     os.path.isdir(os.path.join(structures_path, d))],
                    key=self.natural_sort_key)
            else:
                print(f"Directory not found: {structures_path}")
                return

        for subfolder in first_map_subfolders:
            images_in_subfolder = []
            for map_folder in self.map_folders:
                current_subfolder_path = os.path.join(map_folder, "variants", "structures", subfolder)
                if os.path.exists(current_subfolder_path):
                    images = [os.path.join(current_subfolder_path, f) for f in os.listdir(current_subfolder_path) if
                              f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))]
                    images = sorted(images, key=self.natural_sort_key)
                    images_in_subfolder.append(images)
                else:
                    print(f"Subfolder not found: {current_subfolder_path}")
                    images_in_subfolder.append([])
            self.image_matrix.append(images_in_subfolder)

    def show_image_picker(self):
        if not self.dlg:
            self.dlg = QDialog(self.iface.mainWindow())
            self.dlg.setFixedSize(1200, 800)
            self.dlg.setWindowFlags(
                Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
            self.widget = QWidget()
            self.layout = QVBoxLayout(self.widget)

            self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.grid_layout = QGridLayout()
            self.image_labels = []

            max_images_in_first_row = 3
            num_labels = min(self.total_folders, max_images_in_first_row + 3)

            for i in range(num_labels):
                image_label = QLabel(self.widget)
                image_label.setFixedSize(300, 300)
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setStyleSheet("border: 1px solid black;")
                self.image_labels.append(image_label)

                row = 0 if i < max_images_in_first_row else 1
                col = i % max_images_in_first_row
                self.grid_layout.addWidget(image_label, row, col)

            self.layout.addLayout(self.grid_layout)

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

            self.pushButton_select = QPushButton("Select Images", self.widget)
            self.pushButton_select.clicked.connect(self.select_images)
            self.layout.addWidget(self.pushButton_select)

            self.pushButton_skip_image = QPushButton("Skip Images", self.widget)
            self.pushButton_skip_image.clicked.connect(self.skip_images)
            self.layout.addWidget(self.pushButton_skip_image)

            self.nav_button_layout = QHBoxLayout()
            self.pushButton_prev_subfolder = QPushButton("Previous Folders", self.widget)
            self.pushButton_prev_subfolder.clicked.connect(self.prev_subfolder)
            self.nav_button_layout.addWidget(self.pushButton_prev_subfolder)

            self.pushButton_next_subfolder = QPushButton("Next Folders", self.widget)
            self.pushButton_next_subfolder.clicked.connect(self.next_subfolder)
            self.nav_button_layout.addWidget(self.pushButton_next_subfolder)

            self.layout.addLayout(self.nav_button_layout)

            self.dlg.setLayout(self.layout)

        self.update_ui()
        self.dlg.exec_()

    def update_ui(self):
        self.show_images()

    def show_images(self):
        current_images = self.image_matrix[self.current_subfolder_index]
        for i, image_paths in enumerate(current_images[:len(self.image_labels)]):
            if image_paths and len(image_paths) > self.current_image_index:
                pixmap = QPixmap(image_paths[self.current_image_index])
                self.image_labels[i].setPixmap(
                    pixmap.scaled(self.image_labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        total_images = max(len(image_paths) for image_paths in current_images)
        self.progress_label_subfolder.setText(
            f"Subfolder {self.current_subfolder_index + 1}/{len(self.image_matrix)} - Image {self.current_image_index + 1}/{total_images}")

    def next_image(self):
        if not self.image_matrix[self.current_subfolder_index]:
            print("No images to flip through.")
            return

        max_images = max(len(image_paths) for image_paths in self.image_matrix[self.current_subfolder_index])
        self.current_image_index += 1
        if self.current_image_index >= max_images:
            self.current_image_index = 0

        self.update_ui()

    def prev_image(self):
        if not self.image_matrix[self.current_subfolder_index]:
            print("No images to flip through.")
            return

        max_images = max(len(image_paths) for image_paths in self.image_matrix[self.current_subfolder_index])
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = max_images - 1

        self.update_ui()

    def skip_images(self):
        for i, map_folder in enumerate(self.map_folders):
            self.selected_images[(map_folder, self.current_subfolder_index)] = {
                "status": "skipped"
            }
        self.processed_subfolders.add(self.current_subfolder_index)
        self.check_if_all_processed()
        self.next_subfolder()

    def select_images(self):
        for i, map_folder in enumerate(self.map_folders):
            if len(self.image_matrix[self.current_subfolder_index][i]) > self.current_image_index:
                self.selected_images[(map_folder, self.current_subfolder_index)] = {
                    "status": "selected",
                    "image_path": self.image_matrix[self.current_subfolder_index][i][self.current_image_index]
                }
        self.processed_subfolders.add(self.current_subfolder_index)
        self.check_if_all_processed()
        self.next_subfolder()

    def next_subfolder(self):
        self.current_subfolder_index += 1
        self.current_image_index = 0

        if self.current_subfolder_index >= len(self.image_matrix):
            self.current_subfolder_index = 0

        self.update_ui()

    def prev_subfolder(self):
        self.current_subfolder_index -= 1
        self.current_image_index = 0

        if self.current_subfolder_index < 0:
            self.current_subfolder_index = len(self.image_matrix) - 1

        self.update_ui()

    def check_if_all_processed(self):
        if len(self.processed_subfolders) == len(self.image_matrix):
            print("All subfolders processed.")
            self.save_selection()
            self.dlg.accept()

    def save_selection(self):
        json_path = os.path.join(self.root_folder, 'structure_selection_results.json')
        selection_data = []

        for (map_folder, subfolder_index), image_info in self.selected_images.items():
            if image_info.get("status") == "selected":
                entry = {
                    "map_folder": map_folder,
                    "image_path": image_info.get("image_path")
                }
                selection_data.append(entry)

        with open(json_path, 'w') as f:
            json.dump(selection_data, f, indent=4)

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]
