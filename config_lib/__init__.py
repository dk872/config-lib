from .loader import load_config
from .schema import ConfigSchema
from .validator import ConfigValidator
from .utils import fill_defaults, mask_secrets


class ConfigManager:
    def __init__(self, file_path, schema_from_user=None):
        self.schema = schema_from_user or ConfigSchema().get_schema()
        self.file_path = file_path
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

    def print_config(self, masked=False, secret_fields=None):
        config = self.config
        if masked and secret_fields:
            config = mask_secrets(config, secret_fields)
        print(config)

    def apply_defaults(self):
        self.config = fill_defaults(self.config, self.schema)
