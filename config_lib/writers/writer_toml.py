import re


def is_iso_datetime(value: str) -> bool:
    iso_format = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    return isinstance(value, str) and re.match(iso_format, value)


def format_toml_value(value):
    if isinstance(value, str):
        if is_iso_datetime(value):
            return value
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return '""'
    elif isinstance(value, list):
        items = ", ".join(format_toml_value(v) for v in value)
        return f"[{items}]"
    return str(value)


def serialize_toml(config):
    if not isinstance(config, dict):
        raise TypeError("TOML config must be a dictionary")

    lines = []
    root_keys = []
    nested_sections = []

    for key, value in config.items():
        if isinstance(value, dict):
            nested_sections.append((key, value))
        else:
            root_keys.append((key, value))

    for key, value in root_keys:
        val = format_toml_value(value)
        lines.append(f"{key} = {val}")

    for key, value in nested_sections:
        lines.append(f"\n[{key}]")
        for sub_key, sub_value in value.items():
            val = format_toml_value(sub_value)
            lines.append(f"{sub_key} = {val}")

    return lines
