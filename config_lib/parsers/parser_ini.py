class INISyntaxError(Exception):
    def __init__(self, message, line_num=None):
        if line_num is not None:
            super().__init__(f"INI Syntax Error at line {line_num}: {message}")
        else:
            super().__init__(f"INI Syntax Error: {message}")


def parse_ini_string(ini_str):
    result = {}
    current_section = None

    lines = ini_str.splitlines()
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('#'):
            continue

        if line.startswith('[') and line.endswith(']'):
            section_name = line[1:-1].strip()
            if not section_name:
                raise INISyntaxError(f"Empty section name at line {line_num}", line_num)
            current_section = section_name
            _set_ini_nested_section(result, current_section)
        else:
            if '=' not in line:
                raise INISyntaxError(f"Invalid line at line {line_num}: {line}", line_num)
            key, value = map(str.strip, line.split('=', 1))
            value = _infer_ini_type(value)
            if not key:
                raise INISyntaxError(f"Missing key before '=' at line {line_num}", line_num)
            if current_section is None:
                section_ref = result
            else:
                section_ref = _get_ini_nested_section(result, current_section)
            section_ref[key] = value

    return result


def _set_ini_nested_section(result, dotted_path):
    keys = dotted_path.split(".")
    ref = result
    for key in keys:
        ref = ref.setdefault(key, {})


def _get_ini_nested_section(result, dotted_path):
    keys = dotted_path.split(".")
    ref = result
    for key in keys:
        if key not in ref:
            raise INISyntaxError(f"Section '{key}' not found in path '{dotted_path}'", 0)
        ref = ref[key]
    return ref


def _infer_ini_type(value):
    if value.lower() == "null":
        return None
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if "," in value:
        return [v.strip() for v in value.split(",")]
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
