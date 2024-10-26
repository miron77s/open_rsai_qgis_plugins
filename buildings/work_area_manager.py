import json
import os

class WorkAreaManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.data_file = os.path.join(plugin_dir, 'work_areas.json')
        self.work_areas = []

        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            print(f"Created plugin directory: {plugin_dir}")

        self.load_work_areas()

    def load_work_areas(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.work_areas = data.get("work_areas", [])
                    print(f"Work areas loaded from file: {self.work_areas}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {self.data_file}: {e}")
                self.work_areas = []
        else:
            self.work_areas = []
            self.save_work_areas()
            print(f"No existing work areas file found. A new empty file was created at {self.data_file}")

    def save_work_areas(self):
        try:
            for work_area in self.work_areas:
                if 'image_path' in work_area and isinstance(work_area['image_path'], list):
                    work_area['image_path'] = [path for path in work_area['image_path'] if path]
                if 'vector_path' in work_area and isinstance(work_area['vector_path'], list):
                    work_area['vector_path'] = [path for path in work_area['vector_path'] if path]

            with open(self.data_file, 'w') as f:
                json.dump({"work_areas": self.work_areas}, f, indent=4)
            print(f"Work areas saved to file: {self.data_file}")
        except Exception as e:
            print(f"Failed to save work areas: {e}")

    def add_work_area(self, work_area):
        self.work_areas.append({
            "id": work_area.id,
            "name": work_area.name,
            "image_path": work_area.image_path,
            "vector_path": work_area.vector_path,
            "work_mode": work_area.work_mode,
            "work_area": work_area.work_area,
            "vectors": work_area.vectors,
            "use_segment_anything": work_area.use_segment_anything,
            "predict": work_area.predict
        })
        self.save_work_areas()

    def update_work_area(self, work_area):
        for i, wa in enumerate(self.work_areas):
            if wa["id"] == work_area.id:
                self.work_areas[i] = {
                    "id": work_area.id,
                    "name": work_area.name,
                    "image_path": work_area.image_path,
                    "vector_path": work_area.vector_path,
                    "work_mode": work_area.work_mode,
                    "work_area": work_area.work_area,
                    "vectors": work_area.vectors,
                    "use_segment_anything": work_area.use_segment_anything,
                    "predict": work_area.predict
                }
                self.save_work_areas()
                return
        self.add_work_area(work_area)

    def remove_work_area(self, work_area_id):
        self.work_areas = [wa for wa in self.work_areas if wa["id"] != work_area_id]
        self.save_work_areas()

    def get_work_area(self, work_area_id):
        for work_area in self.work_areas:
            if work_area["id"] == work_area_id:
                return work_area
        return None

    def get_all_work_areas(self):
        return self.work_areas

    def work_area_exists_by_name(self, name):
        return any(wa["name"] == name for wa in self.work_areas)
