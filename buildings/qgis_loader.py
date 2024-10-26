import os
from qgis.core import (
    QgsProject,
    QgsLayerTreeGroup,
    QgsVectorLayer,
    QgsRasterLayer
)
from PyQt5.QtWidgets import QMessageBox


class QGISLayerLoader:
    def __init__(self, root_folder):
        self.root_folder = root_folder
        self.project = QgsProject.instance()

    def find_map_folders(self):
        map_folders = [os.path.join(self.root_folder, folder) for folder in os.listdir(self.root_folder)
                       if os.path.isdir(os.path.join(self.root_folder, folder))]
        return map_folders

    def load_vector_layer(self, filepath, layer_name):
        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist.")
            return None

        layer = QgsVectorLayer(filepath, layer_name, "ogr")
        if not layer.isValid():
            print(f"Layer {layer_name} could not be loaded.")
            return None

        QgsProject.instance().addMapLayer(layer, False)
        return layer

    def find_existing_raster_layer(self, map_name):
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and map_name in layer.name():
                return layer
        return None

    def group_layers_with_raster(self, raster_layer, vector_layers):
        if raster_layer:
            group_name = raster_layer.name() + "_group"
            root = self.project.layerTreeRoot()

            group = root.findGroup(group_name)
            if not group:
                group = root.addGroup(group_name)

            for vector_layer in vector_layers:
                group.addLayer(vector_layer)

            group.addLayer(raster_layer)

            root_layer = root.findLayer(raster_layer.id())
            if root_layer:
                root.removeLayer(raster_layer)

            print(f"Group {group_name} created with layers.")
        else:
            print("Raster layer not found for grouping with vector layers.")

    def process_map_folders(self):
        map_folders = self.find_map_folders()
        if not map_folders:
            print("No map folders found.")
            return

        for map_folder in map_folders:
            map_name = os.path.basename(map_folder)

            projes_path = os.path.join(map_folder, "projes.shp")
            roofs_path = os.path.join(map_folder, "roofs.shp")
            shades_path = os.path.join(map_folder, "shades.shp")

            projes_layer = self.load_vector_layer(projes_path, f"{map_name}_projes")
            roofs_layer = self.load_vector_layer(roofs_path, f"{map_name}_roofs")
            shades_layer = self.load_vector_layer(shades_path, f"{map_name}_shades")

            raster_layer = self.find_existing_raster_layer(map_name)

            if raster_layer:
                vector_layers = [layer for layer in [projes_layer, roofs_layer, shades_layer] if layer]
                self.group_layers_with_raster(raster_layer, vector_layers)
            else:
                print(f"No raster layer found for {map_name}. Skipping group creation.")

    def run(self):
        try:
            self.process_map_folders()
            QMessageBox.information(None, "Success", "All layers loaded and grouped successfully.")
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")
