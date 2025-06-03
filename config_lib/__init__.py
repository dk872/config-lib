from .loader import load_config
from .schema import ConfigSchema
from .validator import ConfigValidator
from .utils import fill_defaults, mask_secrets
from .db import MongoDBHandler
import os


class ConfigManager:
    def __init__(self, file_path=None, custom_schema=None):
        self.schema = custom_schema or ConfigSchema().get_schema()
        self.file_path = file_path
        self.config = None

        if file_path:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            try:
                self.config = load_config(file_path)
            except Exception as e:
                raise RuntimeError(f"Parse error from {file_path}: {e}")

    def validate(self):
        if self.config is None:
            raise ValueError("Loaded configuration is None. Check the config file.")

        try:
            config_validator = ConfigValidator(self.schema)
            config_validator.validate(self.config)
            print("Configuration is valid!")
        except Exception as e:
            raise ValueError(f"Validation error from {self.file_path}: {e}")

    def get_config(self):
        return self.config

    def print_config(self, secret_fields=None):
        config = self.config
        if secret_fields:
            config = mask_secrets(config, secret_fields)
        print(config)

    def apply_defaults(self):
        self.config = fill_defaults(self.config, self.schema)

    def save_to_db(self, name, mongo_uri, db_name, collection_name="configs"):
        if self.config is None:
            print("Error: No configuration loaded to save")
            return

        try:
            db_handler = MongoDBHandler(mongo_uri, db_name, collection_name)
            db_handler.save_config(name, self.config)
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def load_from_db(self, name, mongo_uri, db_name, collection_name="configs"):
        try:
            db_handler = MongoDBHandler(mongo_uri, db_name, collection_name)
            self.config = db_handler.load_config(name)
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def delete_from_db(self, name, mongo_uri, db_name, collection_name="configs"):
        try:
            db_handler = MongoDBHandler(mongo_uri, db_name, collection_name)
            db_handler.delete_config(name)
        except Exception as e:
            print(f"Error deleting configuration: {e}")
