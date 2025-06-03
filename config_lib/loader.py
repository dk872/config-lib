from .parser import parse_json, parse_yaml, parse_toml, parse_ini


def load_config(file_path):
    if file_path.endswith(".json"):
        config = parse_json(file_path)
    elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
        config = parse_yaml(file_path)
    elif file_path.endswith(".toml"):
        config = parse_toml(file_path)
    elif file_path.endswith(".ini"):
        config = parse_ini(file_path)
    else:
        raise ValueError(f"Unsupported file format")

    return config
