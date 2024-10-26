import os
import json
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


class ShadesAndProjectionsLayerProcessor:
    def __init__(self, work_area_folder):
        print("ShadesAndProjectionsLayerProcessor initialized", work_area_folder)
        self.work_area_folder = work_area_folder
        self.crs = QgsCoordinateReferenceSystem('EPSG:3395')
        self.unique_id = 1
        self.proj_layers = {}
        self.shade_layers = {}

    def create_layer(self, map_folder, filename, layer_name):
        file_path = os.path.join(map_folder, filename)

        if os.path.exists(file_path):
            print(f"Loading existing layer: {file_path}")
            layer = QgsVectorLayer(file_path, layer_name, 'ogr')
            if not layer.isValid():
                print(f"Failed to load layer: {file_path}")
                return None, None
            else:
                provider = layer.dataProvider()
                self.unique_id = provider.featureCount() + 1
                return layer, provider
        else:
            print(f"Creating new memory layer for: {map_folder}")
            layer = QgsVectorLayer(f'MultiPolygon?crs={self.crs.authid()}', layer_name, 'memory')
            provider = layer.dataProvider()
            provider.addAttributes([QgsField('id', QVariant.Int)])
            layer.updateFields()
            return layer, provider

    def add_features_from_wkt_file(self, wkt_file, provider):
        if os.path.exists(wkt_file):
            try:
                with open(wkt_file, 'r') as file:
                    wkt = file.read().strip()
                    geom = QgsGeometry.fromWkt(wkt)
                    if not geom.isNull():
                        feature = QgsFeature()
                        feature.setGeometry(geom)
                        feature.setAttributes([self.unique_id])
                        provider.addFeature(feature)
                        self.unique_id += 1
                    else:
                        print(f"Invalid geometry: {wkt}")
            except Exception as e:
                print(f"Error reading {wkt_file}: {e}")
        else:
            print(f"File does not exist: {wkt_file}")

    def process_proj_and_shade_files(self, selection_data):
        for entry in selection_data:
            map_folder = entry["map_folder"]
            image_path = entry.get("image_path")
            if image_path:
                base_file = os.path.splitext(image_path)[0]
                proj_file = base_file + '.proj'
                shade_file = base_file + '.shade'

                print(f"Processing proj file: {proj_file}")
                print(f"Processing shade file: {shade_file}")

                if map_folder not in self.proj_layers:
                    self.proj_layers[map_folder], _ = self.create_layer(map_folder, 'projes.shp', 'proj_layer')
                    self.shade_layers[map_folder], _ = self.create_layer(map_folder, 'shades.shp', 'shade_layer')

                proj_layer, proj_provider = self.proj_layers[map_folder], self.proj_layers[map_folder].dataProvider()
                shade_layer, shade_provider = self.shade_layers[map_folder], self.shade_layers[map_folder].dataProvider()

                self.add_features_from_wkt_file(proj_file, proj_provider)
                self.add_features_from_wkt_file(shade_file, shade_provider)

    def save_layer(self, layer, output_directory, filename):
        file_path = os.path.join(output_directory, filename)
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            file_path,
            QgsProject.instance().transformContext(),
            options
        )
        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error saving layer {filename}: {error}")
        else:
            print(f"Layer {filename} saved successfully at {file_path}")

    def load_selection_file(self):
        selection_file_path = os.path.join(self.work_area_folder, 'structure_selection_results.json')
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
        selection_file_path = os.path.join(self.work_area_folder, 'structure_selection_results.json')
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

        self.process_proj_and_shade_files(selection_data)

        for map_folder in self.proj_layers.keys():
            self.save_layer(self.proj_layers[map_folder], map_folder, 'projes.shp')
            self.save_layer(self.shade_layers[map_folder], map_folder, 'shades.shp')

        self.delete_selection_file()

        print("All layers processed and saved successfully!")
