import os
from os import popen

from .image_picker_dialog import ImagePicker
from .json_settings import JsonSettings
from .merge_vectors import VectorLayerProcessor
from .multi_image_picker import MultiImagePicker
from .shades_and_projections_layer_processor import ShadesAndProjectionsLayerProcessor
from .qgis_loader import QGISLayerLoader
import shutil

map_for_mode = {
    'Manual': '-n external',
    'Automatic': '-m auto',
    'Semiautomatic': '-m on_demand -n external',
}

class ConsoleCommandTool:
    def __init__(self, work_area):
        self.work_area = work_area
        self.settings = JsonSettings()
        pass

    def remove_empty_strings(self, arr):
        return [element for element in arr if element != ""]

    def split_path_and_filename(self, file_path):
        folder_path, file_name_with_ext = os.path.split(file_path)
        file_name, _ = os.path.splitext(file_name_with_ext)
        return file_name

    def remove_related_files_and_variants(self, result_folder):
        file_types = ['.shp', '.shx', '.dbf', '.prj', '.cpg']
        target_files = ['roofs', 'shades', 'projes']

        for foldername, subfolders, filenames in os.walk(result_folder):
            for target in target_files:
                for file_type in file_types:
                    file_path = os.path.join(foldername, target + file_type)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"Removed: {file_path}")
                        except Exception as e:
                            print(f"Error removing {file_path}: {e}")

            # Remove 'variants' folder if it exists
            if 'variants' in subfolders:
                variants_folder_path = os.path.join(foldername, 'variants')
                try:
                    shutil.rmtree(variants_folder_path)
                    print(f"Removed folder and its contents: {variants_folder_path}")
                except Exception as e:
                    print(f"Error removing folder {variants_folder_path}: {e}")
                subfolders.remove('variants')  # Prevent further recursion into 'variants'

    def execute(self, iface):
        print("Executing Console Command Tool")
        raster_inliers_extractor = self.settings.value("raster_inliers_extractor")
        objects_bounds_finder = self.settings.value("objects_bounds_finder")
        roof_locator = self.settings.value("roof_locator")
        multiview_building_reconstructor = self.settings.value("multiview_building_reconstructor")
        result_folder = os.path.join(self.settings.value("result_folder"), self.work_area.name) + "/"
        self.remove_related_files_and_variants(result_folder)

        map_path = self.work_area.image_path[0]
        vector_path = self.work_area.vectors
        work_region_file_path = self.work_area.work_area

        first_command = f"{raster_inliers_extractor} -r {map_path} -v {vector_path} -i {work_region_file_path} -o {result_folder} -f"
        first_command_result = popen(first_command)
        first_command_result_str = first_command_result.read()
        first_command_result.close()
        print(first_command_result_str)

        print(first_command)
        print("-------------------")
        all_images = self.remove_empty_strings(self.work_area.image_path)
        print("all_images", all_images)
        for index, map_path in enumerate(all_images):
            work_vectors_file_path = self.work_area.vector_path[index]

            image_name_without_ext = self.split_path_and_filename(map_path)
            image_result_folder = os.path.join(self.settings.value("result_folder"), self.work_area.name,
                                               image_name_without_ext) + "/"
            second_command = f"{objects_bounds_finder} -v {os.path.join(self.settings.value('result_folder'), self.work_area.name) + '/inliers.shp'} -r {map_path} -i {work_vectors_file_path} -l 80 -m 100 -o {image_result_folder} -f"
            second_command_result = popen(second_command)
            second_command_result_str = second_command_result.read()
            print(second_command_result_str)
            second_command_result.close()
            print(second_command)

        print("-------------------")
        use_asm = "--use_sam" if self.work_area.use_segment_anything else ''
        mode = map_for_mode[self.work_area.work_mode]
        for index, map_path in enumerate(all_images):
            image_name_without_ext = self.split_path_and_filename(map_path)
            image_result_folder = os.path.join(self.settings.value("result_folder"), self.work_area.name,
                                               image_name_without_ext) + "/"

            third_command = f"{roof_locator} -r {map_path} -v {image_result_folder + 'bounds.shp'} -o {image_result_folder} {use_asm} {mode} -f"
            third_command_result = popen(third_command)
            third_command_result_str = third_command_result.read()
            print(third_command_result_str)
            third_command_result.close()
            print(third_command)

        ImagePicker(iface, result_folder, self.work_area.id)
        VectorLayerProcessor(
            work_area_folder=os.path.join(self.settings.value("result_folder"), self.work_area.name)).run()

        print("-------------------")
        roofs = []
        bounds = []
        output = []
        for index, map_path in enumerate(all_images):
            image_name_without_ext = self.split_path_and_filename(map_path)
            image_result_folder = os.path.join(self.settings.value("result_folder"), self.work_area.name,
                                               image_name_without_ext) + "/"
            output.append(image_result_folder)
            roofs.append(image_result_folder + "roofs.shp")
            bounds.append(image_result_folder + "bounds.shp")

        use_predict = "--predict" if self.work_area.predict else ''
        last_command = f"{multiview_building_reconstructor} -v {','.join(roofs)} -b {','.join(bounds)} -r {','.join(all_images)} -o {','.join(output)} {use_predict} {mode} -f"
        last_command_result = popen(last_command)
        last_command_result_str = last_command_result.read()
        print(last_command_result_str)
        last_command_result.close()
        print(last_command)

        root_folder = os.path.join(self.settings.value("result_folder"), self.work_area.name)
        MultiImagePicker(iface=iface,
                         root_folder=root_folder,
                         work_area_id=self.work_area.id)
        ShadesAndProjectionsLayerProcessor(
            work_area_folder=root_folder).run()
        QGISLayerLoader(root_folder=root_folder).run()
