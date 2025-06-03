import re


def is_iso_datetime(value: str) -> bool:
    iso_format = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    return isinstance(value, str) and re.match(iso_format, value)


def format_yaml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    elif isinstance(value, str):
        return value if is_iso_datetime(value) else f'"{value}"'
    else:
        return str(value)


def serialize_yaml(config, indent=0):
    if indent == 0 and not isinstance(config, dict):
        raise TypeError("YAML config must be a dictionary")

    lines = []
    pad = "  " * indent

    for key, value in config.items():
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.extend(serialize_yaml(value, indent + 1))
            lines.append("")
        elif isinstance(value, list):
            lines.append(f"{pad}{key}:")
            for item in value:
                item_pad = "  " * (indent + 1)
                if isinstance(item, dict):
                    lines.append(f"{item_pad}-")
                    lines.extend(serialize_yaml(item, indent + 2))
                    lines.append("")
                else:
                    lines.append(f"{item_pad}- {format_yaml_value(item)}")
        else:
            val = format_yaml_value(value)
            lines.append(f"{pad}{key}: {val}")

    return lines
