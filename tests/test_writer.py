import pytest
from config_lib.writer import save_config_to_file


def test_save_json_config(tmp_path):
    config = {
        "enabled": True,
        "timeout": 30,
        "username": "admin",
        "password": None,
        "created_at": "2024-05-31T12:00:00Z",
        "db": {
            "host": "localhost",
            "port": 5432,
        }
    }
    file_path = tmp_path / "config.json"
    save_config_to_file(config, str(file_path))

    expected = (
        '{\n'
        '  "enabled": true,\n'
        '  "timeout": 30,\n'
        '  "username": "admin",\n'
        '  "password": null,\n'
        '  "created_at": "2024-05-31T12:00:00Z",\n'
        '  "db": {\n'
        '    "host": "localhost",\n'
        '    "port": 5432\n'
        '  }\n'
        '}'
    )

    content = file_path.read_text(encoding="utf-8")
    assert content.strip() == expected.strip()


def test_save_yaml_config(tmp_path):
    config = {
        "enabled": True,
        "timeout": 30,
        "username": "admin",
        "password": None,
        "created_at": "2024-05-31T12:00:00Z",
        "db": {
            "host": "localhost",
            "port": 5432
        }
    }
    file_path = tmp_path / "config.yaml"
    save_config_to_file(config, str(file_path))

    expected_lines = [
        'enabled: true',
        'timeout: 30',
        'username: "admin"',
        'password: null',
        'created_at: 2024-05-31T12:00:00Z',
        'db:',
        '  host: "localhost"',
        '  port: 5432'
    ]

    content = file_path.read_text(encoding="utf-8").splitlines()
    assert content == expected_lines


def test_save_toml_config(tmp_path):
    config = {
        "enabled": True,
        "timeout": 30,
        "username": "admin",
        "password": None,
        "created_at": "2024-05-31T12:00:00Z",
        "db": {
            "host": "localhost",
            "port": 5432
        }
    }
    file_path = tmp_path / "config.toml"
    save_config_to_file(config, str(file_path))

    expected_lines = [
        'enabled = true',
        'timeout = 30',
        'username = "admin"',
        'password = ""',
        'created_at = 2024-05-31T12:00:00Z',
        '',
        '[db]',
        'host = "localhost"',
        'port = 5432'
    ]

    content = file_path.read_text(encoding="utf-8").splitlines()
    assert content == expected_lines


def test_save_ini_config(tmp_path):
    config = {
        "enabled": True,
        "timeout": 30,
        "username": "admin",
        "password": None,
        "port": 5432
    }
    file_path = tmp_path / "config.ini"
    save_config_to_file(config, str(file_path))

    expected_lines = [
        'enabled = true',
        'timeout = 30',
        'username = admin',
        'password = null',
        'port = 5432'
    ]

    content = file_path.read_text(encoding="utf-8").splitlines()
    assert content == expected_lines


def test_serialize_json_invalid_type(tmp_path):
    config = ["not", "a", "dict"]
    file_path = tmp_path / "config.json"

    with pytest.raises(ValueError, match="JSON config must be a dictionary"):
        save_config_to_file(config, str(file_path))


def test_serialize_yaml_invalid_type(tmp_path):
    config = 42
    file_path = tmp_path / "config.yaml"

    with pytest.raises(ValueError, match="YAML config must be a dictionary"):
        save_config_to_file(config, str(file_path))


def test_serialize_toml_invalid_type(tmp_path):
    config = "invalid"
    file_path = tmp_path / "config.toml"

    with pytest.raises(ValueError, match="TOML config must be a dictionary"):
        save_config_to_file(config, str(file_path))


def test_serialize_ini_invalid_type(tmp_path):
    config = True
    file_path = tmp_path / "config.ini"

    with pytest.raises(ValueError, match="INI config must be a dictionary"):
        save_config_to_file(config, str(file_path))


def test_unsupported_format(tmp_path):
    config = {"x": 1}
    file_path = tmp_path / "config.unsupported"

    with pytest.raises(ValueError, match="Unsupported file format"):
        save_config_to_file(config, str(file_path))
