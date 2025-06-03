from datetime import datetime
import re


class ConfigValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate(self, config):
        self._validate_dict(config, self.schema)
        return True

    def _validate_dict(self, config, schema, path=""):
        for key, rules in schema.items():
            full_path = self._format_path(path, key)
            if rules.get("required", False) and key not in config:
                raise ValueError(f"Missing required key: {full_path}")
            if key in config:
                value = config[key]
                expected_type = rules["type"]

                if expected_type is dict and "schema" in rules:
                    if not isinstance(value, dict):
                        raise TypeError(f"Incorrect type for key {full_path}: expected dict, got {type(value).__name__}")
                    self._validate_dict(value, rules["schema"], full_path)
                elif expected_type is list:
                    self._validate_list(value, rules["items"], full_path)
                elif expected_type is str and rules.get("format") == "date":
                    self._validate_date(value, full_path)
                else:
                    self._validate_type(expected_type, value, full_path)

        for key in config:
            if key not in schema:
                raise ValueError(f"Extra key found: {self._format_path(path, key)}")

    def _validate_list(self, value, item_schema, path):
        if not isinstance(value, list):
            raise TypeError(f"Incorrect type for key {path}: expected list, got {type(value).__name__}")
        for i, item in enumerate(value):
            item_path = f"{path}[{i}]"
            self._validate_type(item_schema["type"], item, item_path)

    @staticmethod
    def _validate_date(value, path):
        if isinstance(value, datetime):
            return

        if not isinstance(value, str):
            raise TypeError(f"Incorrect type for key {path}: expected ISO 8601 str or datetime")

        iso_z_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        if not re.match(iso_z_pattern, value):
            raise ValueError(
                f"Incorrect date format for key {path}: expected YYYY-MM-DDTHH:MM:SSZ"
            )

        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError(f"Invalid datetime value for key {path}")

    @staticmethod
    def _validate_type(expected_type, actual_value, path):
        if expected_type is int and isinstance(actual_value, bool):
            raise TypeError(f"Incorrect type for key {path}: expected int, got bool")

        if not isinstance(actual_value, expected_type):
            if isinstance(expected_type, tuple):
                type_names = ", ".join(t.__name__ for t in expected_type)
            else:
                type_names = expected_type.__name__
            raise TypeError(f"Incorrect type for key {path}: expected {type_names}, got {type(actual_value).__name__}")

    @staticmethod
    def _format_path(path, key):
        return f"{path}.{key}" if path else key