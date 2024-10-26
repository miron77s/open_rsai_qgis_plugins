import json
import os


class JsonSettings:
    def __init__(self):
        self.plugin_directory = os.path.dirname(__file__)
        self.file_path = os.path.join(self.plugin_directory, "settings.json")

        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def setValue(self, key, value):
        with open(self.file_path, 'r') as f:
            settings = json.load(f)

        settings[key] = value

        with open(self.file_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def value(self, key, default_value=None):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                settings = json.load(f)

            return settings.get(key, default_value)

        return default_value

    def check_keys_have_values(self, keys):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                settings = json.load(f)

            for key in keys:
                if key not in settings or settings[key] is None:
                    return False
            return True
        return False

