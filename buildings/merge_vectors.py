import json
import os

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem
)


class VectorLayerProcessor:
    def __init__(self, work_area_folder):
        print("VectorLayerProcessor initialized", work_area_folder)
        self.work_area_folder = work_area_folder
        self.crs = QgsCoordinateReferenceSystem('EPSG:3395')
        self.roof_layers = {}

    def create_layer(self, map_folder):
        file_path = os.path.join(self.work_area_folder, map_folder, 'roofs.shp')
        if os.path.exists(file_path):
            print(f"Loading existing layer: {file_path}")
            layer = QgsVectorLayer(file_path, 'roof_layer', 'ogr')
            if not layer.isValid():
                print(f"Failed to load layer: {file_path}")
                return None, None
            else:
                provider = layer.dataProvider()
                return layer, provider
        else:
            print(f"Creating new in-memory layer for: {map_folder}")
            layer = QgsVectorLayer(f'MultiPolygon?crs={self.crs.authid()}', 'roof_layer', 'memory')
            provider = layer.dataProvider()
            provider.addAttributes([QgsField('FID', QVariant.Int)])
            layer.updateFields()
            return layer, provider

    def add_features_from_wkt_file(self, wkt_file, provider, folder_id):
        if os.path.exists(wkt_file):
            try:
                with open(wkt_file, 'r') as file:
                    wkt = file.read().strip()
                    geom = QgsGeometry.fromWkt(wkt)
                    if not geom.isNull():
                        feature = QgsFeature()
                        feature.setGeometry(geom)
                        feature.setAttributes([folder_id])
                        provider.addFeature(feature)
                    else:
                        print(f"Invalid geometry: {wkt}")
            except Exception as e:
                print(f"Error reading {wkt_file}: {e}")
        else:
            print(f"File does not exist: {wkt_file}")

    def process_roof_files(self, selection_data):
        for entry in selection_data:
            map_folder = entry["map_folder"]
            image_path = entry.get("image_path")
            folder_id = parent_directory_name = os.path.basename(os.path.dirname(image_path))
            if image_path:
                roof_file = os.path.splitext(image_path)[0] + '.roof'
                print(f"Processing roof file: {roof_file}")

                if map_folder not in self.roof_layers:
                    self.roof_layers[map_folder], _ = self.create_layer(map_folder)

                layer, provider = self.roof_layers[map_folder], self.roof_layers[map_folder].dataProvider()
                self.add_features_from_wkt_file(roof_file, provider, folder_id)

    def save_layer(self, layer, output_directory):
        file_path = os.path.join(self.work_area_folder, output_directory, 'roofs.shp')
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            file_path,
            QgsProject.instance().transformContext(),
            options
        )
        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error saving roof layer: {error}")
        else:
            print(f"Roof layer saved successfully at {file_path}")

    def load_selection_file(self):
        selection_file_path = os.path.join(self.work_area_folder, 'selection_results.json')
        if os.path.exists(selection_file_path):
            with open(selection_file_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"Error loading selection file: {selection_file_path}")
                    return []
        else:
            print(f"Selection file not found: {selection_file_path}")
            return []

    def delete_selection_file(self):
        selection_file_path = os.path.join(self.work_area_folder, 'selection_results.json')
        if os.path.exists(selection_file_path):
            try:
                os.remove(selection_file_path)
                print(f"Selection file {selection_file_path} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete selection file {selection_file_path}: {e}")
        else:
            print(f"Selection file {selection_file_path} not found for deletion.")

    def run(self):
        selection_data = self.load_selection_file()
        if not selection_data:
            print("No selection data found. Exiting.")
            return

        self.process_roof_files(selection_data)

        for map_folder, layer in self.roof_layers.items():
            self.save_layer(layer, map_folder)

        self.delete_selection_file()

        print("All roof layers processed and saved successfully!")
