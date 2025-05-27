DEFAULT_SCHEMA = {
    "database": {
        "type": "dict",
        "required": True,
        "schema": {
            "host": {
                "type": "str",
                "required": True
            },
            "port": {
                "type": "int",
                "required": True
            },
            "user": {
                "type": "str",
                "required": True
            },
            "password": {
                "type": "str",
                "required": True
            }
        }
    },
    "logging": {
        "type": "dict",
        "required": False,
        "schema": {
            "level": {
                "type": "str",
                "required": True
            },
            "output": {
                "type": "str",
                "required": True
            },
            "rotation_interval": {
                "type": "int",
                "required": False,
                "default": 7
            }
        }
    },
    "network": {
        "type": "dict",
        "required": False,
        "schema": {
            "timeout": {
                "type": "int",
                "required": False,
                "default": 30
            },
            "retries": {
                "type": "int",
                "required": False,
                "default": 3
            }
        }
    },
    "date_of_creation": {
        "type": "date",
        "required": True
    },
    "users": {
        "type": "list",
        "required": True,
        "item_type": "str"
    }
}


class ConfigSchema:

    def __init__(self, schema=None):
        self.schema = schema or DEFAULT_SCHEMA

    def get_schema(self):
        return self.schema
