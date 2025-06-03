def serialize_ini(config):
    if not isinstance(config, dict):
        raise TypeError("INI config must be a dictionary")

    lines = []
    for section, values in config.items():
        lines.extend(_serialize_section(section, values))
    return lines


def _serialize_section(section, values):
    lines = []

    if isinstance(values, dict):
        lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} = {serialize_value(value)}")
        lines.append("")
    else:
        lines.append(f"{section} = {serialize_value(values)}")

    return lines


def serialize_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)
