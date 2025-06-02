import pytest
from config_lib.utils import fill_defaults, mask_secrets


def test_fill_defaults_simple():
    config = {"host": "localhost"}
    schema = {
        "host": {"type": str},
        "port": {"type": int, "default": 8080},
    }

    result = fill_defaults(config, schema)
    assert result == {"host": "localhost", "port": 8080}


def test_fill_defaults_nested():
    config = {"db": {"user": "admin"}}
    schema = {
        "db": {
            "type": dict,
            "schema": {
                "user": {"type": str},
                "password": {"type": str, "default": "secret"},
            },
        },
    }

    result = fill_defaults(config, schema)
    assert result == {"db": {"user": "admin", "password": "secret"}}


def test_fill_defaults_empty_config():
    config = {}
    schema = {
        "debug": {"type": bool, "default": False},
        "logging": {
            "type": dict,
            "schema": {
                "level": {"type": str, "default": "INFO"},
            },
        },
    }

    result = fill_defaults(config, schema)
    assert result == {
        "debug": False,
        "logging": {"level": "INFO"},
    }


def test_fill_defaults_preserves_existing_values():
    config = {"debug": True, "logging": {"level": "DEBUG"}}
    schema = {
        "debug": {"type": bool, "default": False},
        "logging": {
            "type": dict,
            "schema": {
                "level": {"type": str, "default": "INFO"},
                "format": {"type": str, "default": "%(message)s"},
            },
        },
    }

    result = fill_defaults(config, schema)
    assert result == {
        "debug": True,
        "logging": {"level": "DEBUG", "format": "%(message)s"},
    }


def test_fill_defaults_applies_default_to_empty_string():
    config = {"port": ""}
    schema = {"port": {"type": int, "default": 1234}}

    result = fill_defaults(config, schema)
    assert result == {"port": 1234}


def test_mask_secrets_flat_config():
    config = {"username": "admin", "password": "1234"}
    secret_fields = ["password"]

    result = mask_secrets(config, secret_fields)
    assert result == {"username": "admin", "password": "***"}


def test_mask_secrets_nested():
    config = {
        "db": {
            "user": "admin",
            "password": "1234",
        },
        "api_key": "ABC123",
    }
    secret_fields = ["db.password", "api_key"]

    result = mask_secrets(config, secret_fields)
    assert result == {
        "db": {
            "user": "admin",
            "password": "***",
        },
        "api_key": "***",
    }


def test_mask_secrets_missing_fields():
    config = {"username": "admin"}
    secret_fields = ["password", "token"]

    result = mask_secrets(config, secret_fields)
    assert result == {"username": "admin"}


def test_mask_secrets_custom_mask():
    config = {"secret": "topsecret"}
    secret_fields = ["secret"]

    result = mask_secrets(config, secret_fields, mask="XXX")
    assert result == {"secret": "XXX"}
