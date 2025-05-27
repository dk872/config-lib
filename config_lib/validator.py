from datetime import datetime


class ConfigValidator:

    def __init__(self, schema):
        self.schema = schema

    def validate(self, config):
        self._validate_dict(config, self.schema)
        return True

    def _validate_dict(self, config, schema, path=""):
        if not isinstance(config, dict):
            raise ValueError(f"{path or 'root'} must be a dictionary")

        for key, rules in schema.items():
            full_path = self._format_path(path, key)
            required = rules.get("required", False)
            has_value = key in config

            if not has_value:
                if required:
                    raise ValueError(f"Missing required field: {full_path}")
                elif "default" in rules:
                    config[key] = rules["default"]
                continue

            value = config[key]
            expected_type = rules.get("type")

            if expected_type == "dict":
                self._validate_type("dict", value, full_path)
                self._validate_dict(value, rules.get("schema", {}), full_path)

            elif expected_type == "list":
                self._validate_list(value, rules, full_path)

            elif expected_type == "date":
                self._validate_date(value, full_path)

            else:
                self._validate_type(expected_type, value, full_path)

    def _validate_list(self, value, item_schema, path):
        if not isinstance(value, list):
            raise ValueError(f"{path} must be a list")

        expected_type = item_schema.get("item_type", "str")
        for i, item in enumerate(value):
            self._validate_type(expected_type, item,
                                self._format_path(path, str(i)))

    @staticmethod
    def _validate_date(value, path):
        if not isinstance(value, str):
            raise ValueError(f"{path} must be a string in ISO 8601 format")

        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"{path} must be a valid ISO 8601 date string")

    @staticmethod
    def _validate_type(expected_type, actual_value, path):
        python_type = {
            "str": str,
            "int": int,
            "bool": bool,
            "dict": dict,
            "list": list
        }.get(expected_type)

        if python_type is None:
            raise ValueError(f"Unknown expected type: {expected_type}")

        if not isinstance(actual_value, python_type):
            raise ValueError(f"{path} must be of type {expected_type}")

    @staticmethod
    def _format_path(path, key):
        return f"{path}.{key}" if path else key
