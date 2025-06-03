import pytest
from config_lib.validator import ConfigValidator



def test_valid_simple_dict():
    schema = {
        "name": {
            "type": str,
            "required": True
        },
        "age": {
            "type": int,
            "required": True
        }
    }
    config = {"name": "Alice", "age": 30}

    validator = ConfigValidator(schema)
    assert validator.validate(config) is True


def test_missing_required_key():
    schema = {
        "name": {
            "type": str,
            "required": True
        },
        "age": {
            "type": int,
            "required": True
        }
    }
    config = {"name": "Bob"}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"Missing required key: age"):
        validator.validate(config)


def test_wrong_type():
    schema = {"enabled": {"type": bool, "required": True}}
    config = {"enabled": "true"}

    validator = ConfigValidator(schema)
    with pytest.raises(TypeError, match=r"Incorrect type for key enabled: expected bool, got str"):
        validator.validate(config)


def test_nested_dict_valid():
    schema = {
        "db": {
            "type": dict,
            "required": True,
            "schema": {
                "host": {
                    "type": str,
                    "required": True
                },
                "port": {
                    "type": int,
                    "required": True
                }
            }
        }
    }
    config = {"db": {"host": "localhost", "port": 5432}}

    validator = ConfigValidator(schema)
    assert validator.validate(config)


def test_nested_dict_missing_field():
    schema = {
        "db": {
            "type": dict,
            "required": True,
            "schema": {
                "host": {
                    "type": str,
                    "required": True
                },
                "port": {
                    "type": int,
                    "required": True
                }
            }
        }
    }
    config = {"db": {"host": "localhost"}}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"Missing required key: db.port"):
        validator.validate(config)


def test_list_of_strings_valid():
    schema = {
        "users": {
            "type": list,
            "required": True,
            "items": {"type": str}
        }
    }
    config = {"users": ["alice", "bob", "carol"]}

    validator = ConfigValidator(schema)
    assert validator.validate(config)


def test_list_wrong_item_type():
    schema = {
        "scores": {
            "type": list,
            "required": True,
            "items": {"type": int}
        }
    }
    config = {"scores": [10, "twenty", 30]}

    validator = ConfigValidator(schema)
    with pytest.raises(TypeError, match=r"Incorrect type for key scores\[1\]: expected int, got str"):
        validator.validate(config)


def test_date_valid():
    schema = {
        "created_at": {
            "type": str,
            "required": True,
            "format": "date"
        }
    }
    config = {"created_at": "2024-12-31T12:00:00Z"}

    validator = ConfigValidator(schema)
    assert validator.validate(config)


def test_date_invalid():
    schema = {
        "created_at": {
            "type": str,
            "required": True,
            "format": "date"
        }
    }
    config = {"created_at": "31-12-2024"}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"Incorrect date format for key created_at: expected YYYY-MM-DDTHH:MM:SSZ"):
        validator.validate(config)