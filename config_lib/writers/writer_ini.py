def serialize_ini(config):
    if not isinstance(config, dict):
        raise TypeError("INI config must be a dictionary")

    lines = []
    for section, values in config.items():
        if isinstance(values, dict):
            lines.append(f"[{section}]")
            for key, value in values.items():
                if isinstance(value, bool):
                    val = "true" if value else "false"
                elif value is None:
                    val = "null"
                else:
                    val = value
                lines.append(f"{key} = {val}")
            lines.append("")
        else:
            if isinstance(values, bool):
                val = "true" if values else "false"
            elif values is None:
                val = "null"
            else:
                val = values
            lines.append(f"{section} = {val}")
    return lines
