import pytest
from config_lib.validator import ConfigValidator


def test_valid_simple_dict():
    schema = {
        "name": {
            "type": "str",
            "required": True
        },
        "age": {
            "type": "int",
            "required": True
        }
    }
    config = {"name": "Alice", "age": 30}

    validator = ConfigValidator(schema)
    assert validator.validate(config) is True


def test_missing_required_key():
    schema = {
        "name": {
            "type": "str",
            "required": True
        },
        "age": {
            "type": "int",
            "required": True
        }
    }
    config = {"name": "Bob"}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"Missing required field: age"):
        validator.validate(config)


def test_wrong_type():
    schema = {"enabled": {"type": "bool", "required": True}}
    config = {"enabled": "true"}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"enabled must be of type bool"):
        validator.validate(config)


def test_nested_dict_valid():
    schema = {
        "db": {
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
                }
            }
        }
    }
    config = {"db": {"host": "localhost"}}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"Missing required field: db.port"):
        validator.validate(config)


def test_list_of_strings_valid():
    schema = {"users": {"type": "list", "required": True, "item_type": "str"}}
    config = {"users": ["alice", "bob", "carol"]}

    validator = ConfigValidator(schema)
    assert validator.validate(config)


def test_list_wrong_item_type():
    schema = {"scores": {"type": "list", "required": True, "item_type": "int"}}
    config = {"scores": [10, "twenty", 30]}

    validator = ConfigValidator(schema)
    with pytest.raises(ValueError, match=r"scores\.1 must be of type int"):
        validator.validate(config)


def test_date_valid():
    schema = {"created_at": {"type": "date", "required": True}}
    config = {"created_at": "2024-12-31"}

    validator = ConfigValidator(schema)
    assert validator.validate(config)


def test_date_invalid():
    schema = {"created_at": {"type": "date", "required": True}}
    config = {"created_at": "31-12-2024"}

    validator = ConfigValidator(schema)
    with pytest.raises(
            ValueError,
            match=r"created_at must be a valid ISO 8601 date string"):
        validator.validate(config)
