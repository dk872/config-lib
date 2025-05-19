class JSONSyntaxError(Exception):
    def __init__(self, message, line_number=None):
        prefix = f"JSON Syntax Error on line {line_number}" if line_number else "JSON Syntax Error"
        super().__init__(f"{prefix}: {message}")


def parse_json_string(json_str):
    json_str = json_str.strip()

    if not json_str:
        return {}

    try:
        if json_str.startswith('{'):
            return parse_json_object(json_str, json_str, 0)
        elif json_str.startswith('['):
            return parse_json_array(json_str, json_str, 0)
        elif json_str.startswith('"'):
            value, _ = parse_json_string_value(json_str, json_str, 0)
            return value
        elif json_str.startswith('true'):
            return True
        elif json_str.startswith('false'):
            return False
        elif json_str.startswith('null'):
            return None
        else:
            return parse_json_number(json_str, json_str, 0)
    except JSONSyntaxError:
        raise
    except Exception as e:
        raise JSONSyntaxError(str(e))
    