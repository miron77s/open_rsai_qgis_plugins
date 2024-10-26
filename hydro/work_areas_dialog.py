import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QWidget, QLabel, QHBoxLayout
import uuid
from .work_area_manager import WorkAreaManager
from .create_work_area_dialog import CreateWorkAreaDialog

class WorkArea:
    def __init__(self, id=None, name="", images_paths=None, work_area_path=""):
        self.id = id if id else str(uuid.uuid4())
        self.name = name
        self.images_paths = images_paths if images_paths else []
        self.work_area_path = work_area_path

    @staticmethod
    def from_dict(data):
        return WorkArea(
            id=data.get("id"),
            name=data.get("name"),
            images_paths=data.get("images_paths", []),
            work_area_path=data.get("work_area_path", "")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "images_paths": self.images_paths,
            "work_area_path": self.work_area_path
        }


class Ui_WorkAreasDialog(object):
    def setupUi(self, WorkAreasDialog):
        WorkAreasDialog.setObjectName("WorkAreasDialog")
        WorkAreasDialog.setFixedSize(400, 300)

        self.verticalLayout = QVBoxLayout(WorkAreasDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.listWidgetWorkAreas = QListWidget(WorkAreasDialog)
        self.listWidgetWorkAreas.setObjectName("listWidgetWorkAreas")
        self.verticalLayout.addWidget(self.listWidgetWorkAreas)

        self.pushButtonAddNew = QPushButton("Add new", WorkAreasDialog)
        self.pushButtonAddNew.setObjectName("pushButtonAddNew")
        self.verticalLayout.addWidget(self.pushButtonAddNew)

        WorkAreasDialog.setWindowTitle("Created work areas")
        QtCore.QMetaObject.connectSlotsByName(WorkAreasDialog)


class WorkAreasDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.ui = Ui_WorkAreasDialog()
        self.ui.setupUi(self)
        self.ui.pushButtonAddNew.clicked.connect(self.add_new_work_area)
        self.iface = iface
        self.work_area_manager = WorkAreaManager(os.path.dirname(__file__))
        self.work_areas = self.work_area_manager.get_all_work_areas()
        self.update_work_area_list()

    def add_new_work_area(self):
        new_work_area = WorkArea()
        self.create_work_area_dialog = CreateWorkAreaDialog(new_work_area, self.iface)
        self.create_work_area_dialog.finished.connect(self.update_work_area_list)
        self.close()
        self.create_work_area_dialog.show()

    def save_new_work_area(self, work_area):
        self.work_areas.append({
            "id": work_area.id,
            "name": work_area.name,
            "images_paths": work_area.images_paths,
            "work_area_path": work_area.work_area_path
        })
        self.work_area_manager.add_work_area(work_area)

    def edit_work_area(self, work_area_data):
        work_area = WorkArea.from_dict(work_area_data)
        self.create_work_area_dialog = CreateWorkAreaDialog(work_area, self.iface)
        self.create_work_area_dialog.finished.connect(self.update_work_area_list)
        self.close()
        self.create_work_area_dialog.show()

    def save_updated_work_area(self, work_area):
        for i, wa in enumerate(self.work_areas):
            if wa["id"] == work_area.id:
                self.work_areas[i] = {
                    "id": work_area.id,
                    "name": work_area.name,
                    "images_paths": work_area.images_paths,
                    "work_area_path": work_area.work_area_path
                }
                break
        self.work_area_manager.update_work_area(work_area)

    def remove_work_area(self, work_area_id):
        self.work_areas = [wa for wa in self.work_areas if wa["id"] != work_area_id]
        self.work_area_manager.remove_work_area(work_area_id)
        self.update_work_area_list()

    def update_work_area_list(self):
        self.ui.listWidgetWorkAreas.clear()
        for work_area_data in self.work_areas:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            label = QLabel(work_area_data.get("name", "Unnamed Work Area"))
            button_remove = QPushButton("X")
            button_remove.setMaximumWidth(20)

            layout.addWidget(label)
            layout.addWidget(button_remove)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.ui.listWidgetWorkAreas.addItem(item)
            self.ui.listWidgetWorkAreas.setItemWidget(item, widget)

            button_remove.clicked.connect(lambda _, wa_id=work_area_data["id"]: self.remove_work_area(wa_id))
            label.mousePressEvent = lambda event, wa_id=work_area_data["id"]: self.edit_work_area(
                self.work_area_manager.get_work_area(wa_id))
