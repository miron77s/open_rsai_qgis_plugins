import os

from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes,
    QgsField, QgsVectorFileWriter, QgsCoordinateTransformContext
)
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.utils import iface

from .json_settings import JsonSettings

blue_color = QColor(0, 0, 255, 100)
red_color = QColor(255, 0, 0, 100)


class DrawRedVectorTool(QgsMapTool):
    def __init__(self, canvas, iface, work_area, parent_dialog, index):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.work_area = work_area
        self.parent_dialog = parent_dialog
        self.start_point = None
        self.end_point = None
        self.index = index
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(red_color)
        self.rubber_band.setWidth(3)
        self.work_layer = None
        self.init_work_layer()
        self.draw_finished = False
        self.draw_blue_vector_tool = DrawBlueVectorTool(canvas, iface, self.work_layer, self.work_area,
                                                        self.parent_dialog, self.index)

    def init_work_layer(self):
        layer_name = self.work_area.name + str(self.work_area.id) + "-" + str(self.index)
        self.remove_layer_by_name(layer_name)
        self.work_layer = QgsVectorLayer("LineString?crs=EPSG:3395", layer_name, "memory")
        provider = self.work_layer.dataProvider()
        provider.addAttributes([QgsField("id", QVariant.Int), QgsField("type", QVariant.String)])
        self.work_layer.updateFields()
        QgsProject.instance().addMapLayer(self.work_layer)

    def remove_layer_by_name(self, layer_name):
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if layer.name() == layer_name:
                QgsProject.instance().removeMapLayer(layer)
                self.canvas.refresh()
                print(f"Layer '{layer_name}' has been removed.")
                return

        print(f"Layer '{layer_name}' not found.")

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.start_point:
                self.start_point = self.toMapCoordinates(event.pos())
            else:
                self.draw_finished = True
                self.end_point = self.toMapCoordinates(event.pos())
                self.create_vector(self.start_point, self.end_point, 0, "projection")
                self.rubber_band.reset()
                self.setup_next_step()

    def setup_next_step(self):
        self.draw_blue_vector_tool.set_start_point(self.start_point)
        iface.mapCanvas().setMapTool(self.draw_blue_vector_tool)

    def canvasMoveEvent(self, event):
        if self.start_point:
            self.end_point = self.toMapCoordinates(event.pos())
            self.draw_vector(self.start_point, self.end_point)

    def draw_vector(self, start_point, end_point):
        self.rubber_band.reset()
        self.rubber_band.setToGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(start_point), QgsPointXY(end_point)]),
                                       None)
        self.rubber_band.show()

    def create_vector(self, start_point, end_point, vector_id, vector_type):
        vector = QgsGeometry.fromPolylineXY([QgsPointXY(start_point), QgsPointXY(end_point)])
        feature = QgsFeature()
        feature.setGeometry(vector)
        feature.setAttributes([vector_id, vector_type])
        self.work_layer.startEditing()
        self.work_layer.dataProvider().addFeatures([feature])
        self.work_layer.commitChanges()

    def deactivate(self):
        if not self.draw_finished:
            self.rubber_band.reset()
            QgsProject.instance().removeMapLayer(self.work_layer)
        super().deactivate()


class DrawBlueVectorTool(QgsMapTool):
    def __init__(self, canvas, iface, work_layer, work_area, parent_dialog, index):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.work_layer = work_layer
        self.work_area = work_area
        self.parent_dialog = parent_dialog
        self.start_point = None
        self.end_point = None
        self.draw_finished = False
        self.index = index
        self.rubber_band = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(blue_color)
        self.rubber_band.setWidth(3)

    def set_start_point(self, start_point):
        self.start_point = start_point

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.start_point:
                return
            self.end_point = self.toMapCoordinates(event.pos())
            self.create_vector(self.start_point, self.end_point, 1, "shade")
            self.draw_finished = True
            self.rubber_band.reset()
            self.start_point = None
            self.end_point = None
            self.save_work_layer()

    def canvasMoveEvent(self, event):
        if self.start_point:
            self.end_point = self.toMapCoordinates(event.pos())
            self.draw_vector(self.start_point, self.end_point)

    def draw_vector(self, start_point, end_point):
        self.rubber_band.reset()
        self.rubber_band.setToGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(start_point), QgsPointXY(end_point)]),
                                       None)
        self.rubber_band.show()

    def create_vector(self, start_point, end_point, vector_id, vector_type):
        vector = QgsGeometry.fromPolylineXY([QgsPointXY(start_point), QgsPointXY(end_point)])
        feature = QgsFeature()
        feature.setGeometry(vector)
        feature.setAttributes([vector_id, vector_type])
        self.work_layer.startEditing()
        self.work_layer.dataProvider().addFeatures([feature])
        self.work_layer.commitChanges()

    def get_filename_without_extension(self, file_path):
        base_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        return file_name_without_ext

    def save_work_layer(self):
        settings = JsonSettings()
        save_folder = os.path.join(settings.value("result_folder"), self.work_area.name,
                                   self.get_filename_without_extension(self.parent_dialog.image_paths[self.index]))

        if not save_folder:
            plugin_dir = os.path.dirname(__file__)
            save_folder = os.path.join(plugin_dir, "temp")

        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, f"shadow_and_projection-{self.index}.shp")

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"

        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            self.work_layer, save_path, QgsCoordinateTransformContext(), options
        )

        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error when saving shapefile: {error[1]}")
        else:
            print(f"Shapefile saved successfully at: {save_path}")
            self.parent_dialog.vector_paths[self.index] = save_path

        self.canvas.unsetMapTool(self)
        self.parent_dialog.bring_to_front()
        self.parent_dialog.ui.vectorCheckboxes[self.index].setChecked(True)

    def deactivate(self):
        if not self.draw_finished:
            self.rubber_band.reset()
            QgsProject.instance().removeMapLayer(self.work_layer)
            self.canvas.refresh()

        super().deactivate()
