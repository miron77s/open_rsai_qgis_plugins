import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsWkbTypes, QgsVectorFileWriter, QgsCoordinateTransformContext
)
from qgis.gui import QgsMapTool, QgsRubberBand

from .json_settings import JsonSettings

green_color = QColor(0, 255, 0, 100)


class DrawWorkRegionTool(QgsMapTool):
    def __init__(self, canvas, iface, work_area, parent_dialog):
        super().__init__(canvas)
        self.work_region_constructor_view = QgsRubberBand(iface.mapCanvas(), QgsWkbTypes.PolygonGeometry)
        self.work_region_constructor_view.setColor(green_color)
        self.work_region_points = []
        self.draw_finished = False
        self.canvas = canvas
        self.iface = iface
        self.work_area = work_area
        self.parent_dialog = parent_dialog
        self.layer_name = self.work_area.name + str(self.work_area.id) + "-work-region"
        self.remove_layer_by_name(self.layer_name)

    def canvasPressEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        if event.button() == Qt.RightButton and len(self.work_region_points) > 2:
            return self.create_and_save_work_region()
        self.work_region_points.append(point)
        self.draw_work_region_constructor(event)

    def draw_work_region_constructor(self, event):
        current_point = self.toMapCoordinates(event.pos())
        if self.work_region_points:
            self.work_region_constructor_view.reset(QgsWkbTypes.PolygonGeometry)
            temp_points = self.work_region_points + [current_point]
            for point in temp_points:
                self.work_region_constructor_view.addPoint(point)
            self.work_region_constructor_view.show()

    def canvasMoveEvent(self, event):
        if self.work_region_points:
            self.draw_work_region_constructor(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.deactivate()

    def deactivate(self):
        self.work_region_points.clear()
        self.work_region_constructor_view.hide()
        self.iface.mapCanvas().unsetMapTool(self)
        self.parent_dialog.activateWindow()
        self.parent_dialog.raise_()
        self.parent_dialog.show()

    def create_and_save_work_region(self):
        work_region_vector = QgsVectorLayer("Polygon?crs=EPSG:3395", self.layer_name, "memory")
        work_region_vector_provider = work_region_vector.dataProvider()

        feature = QgsFeature()
        geom = QgsGeometry.fromPolygonXY([self.work_region_points])
        feature.setGeometry(geom)
        work_region_vector_provider.addFeatures([feature])

        work_region_vector.updateExtents()
        QgsProject.instance().addMapLayer(work_region_vector)

        self.save_work_region_as_shapefile(work_region_vector)
        self.deactivate()

    def remove_layer_by_name(self, layer_name):
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if layer.name() == layer_name:
                QgsProject.instance().removeMapLayer(layer)
                self.canvas.refresh()
                print(f"Layer '{layer_name}' has been removed.")
                return

        print(f"Layer '{layer_name}' not found.")

    def save_work_region_as_shapefile(self, layer):
        settings = JsonSettings()
        save_folder = os.path.join(settings.value("result_folder"), self.work_area.name)

        if not save_folder:
            plugin_dir = os.path.dirname(__file__)
            save_folder = os.path.join(plugin_dir, "temp")

        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, "work_region.shp")

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"

        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer, save_path, QgsCoordinateTransformContext(), options
        )

        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error when saving shapefile: {error[1]}")
        else:
            print(f"Shapefile saved successfully at: {save_path}")
            self.work_area.work_area = save_path

            # Обновляем путь в форме
            self.parent_dialog.ui.labelWorkAreaPath.setText(self.parent_dialog.elide_text(save_path))

        self.parent_dialog.show_qgis_main_window()
