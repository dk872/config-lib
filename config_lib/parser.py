from .parsers.parser_json import parse_json_string, JSONSyntaxError
from .parsers.parser_yaml import parse_yaml_string, YAMLSyntaxError
from .parsers.parser_toml import parse_toml_string, TOMLSyntaxError
from .parsers.parser_ini import parse_ini_string, INISyntaxError


def parse_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_json_string(content)
    except JSONSyntaxError as e:
        raise e
    except Exception as exc:
        raise RuntimeError(f"Error reading JSON: {exc}") from exc


def parse_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_yaml_string(content)
    except YAMLSyntaxError as e:
        raise e
    except Exception as exc:
        raise RuntimeError(f"Error reading YAML: {exc}") from exc


def parse_toml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_toml_string(content)
    except TOMLSyntaxError as e:
        raise e
    except Exception as exc:
        raise RuntimeError(f"Error reading TOML: {exc}") from exc


def parse_ini(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_ini_string(content)
    except INISyntaxError as e:
        raise e
    except Exception as exc:
        raise RuntimeError(f"Error reading INI: {exc}") from exc
