DEFAULT_SCHEMA = {
    "database": {
        "type": dict,
        "required": True,
        "schema": {
            "host": {"type": str, "required": True, "default": "localhost"},
            "port": {"type": int, "required": True, "default": 5432},
            "user": {"type": str, "required": True, "default": "admin"},
            "password": {"type": str, "required": True},
            "is_active": {"type": bool, "required": True, "default": True},
            "last_login": {"type": (str, type(None)), "required": True, "default": None},
        },
    },
    "logging": {
        "type": dict,
        "required": True,
        "schema": {
            "level": {"type": str, "required": True, "default": "INFO"},
            "output": {"type": str, "required": True, "default": "stdout"},
            "log_rotation_interval": {"type": (float, int), "required": True, "default": 24.0},
        },
    },
    "network": {
        "type": dict,
        "required": True,
        "schema": {
            "timeout": {"type": int, "required": False, "default": 30},
            "retries": {"type": int, "required": True, "default": 3},
        },
    },
    "date_of_creation": {
        "type": str,
        "required": True,
        "format": "date",
    },
    "users": {
        "type": list,
        "required": True,
        "items": {"type": str},
    },
}


class ConfigSchema:
    def __init__(self, schema=None):
        self.schema = schema or DEFAULT_SCHEMA

    def get_schema(self):
        return self.schema