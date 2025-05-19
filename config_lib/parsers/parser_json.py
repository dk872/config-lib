class JSONSyntaxError(Exception):
    def __init__(self, message, line_number=None):
        prefix = f"JSON Syntax Error on line {line_number}" if line_number else "JSON Syntax Error"
        super().__init__(f"{prefix}: {message}")


def get_line_number(text, pos):
    return text.count('\n', 0, pos) + 1


def parse_json_object(text, source_text, offset):
    if not text.startswith('{') or not text.endswith('}'):
        line_num = get_line_number(source_text, offset)
        raise JSONSyntaxError("Invalid JSON object", line_num)

    inner_content = text[1:-1].strip()
    current_offset = offset + 1
    obj = {}

    while inner_content:
        key, inner_content, current_offset = parse_object_key(inner_content, source_text, current_offset)
        value, inner_content, current_offset = parse_object_value(inner_content, source_text, current_offset)
        inner_content, current_offset = process_comma_or_end(inner_content, source_text, current_offset)

        obj[key] = value

    return obj


def parse_object_key(content, source_text, offset):
    if not content.startswith('"'):
        line_num = get_line_number(source_text, offset)
        raise JSONSyntaxError("Expected string key in double quotes", line_num)

    key, remainder = parse_json_string_value(content, source_text, offset)
    consumed = len(content) - len(remainder)
    offset += consumed
    content = remainder.strip()

    if not content.startswith(':'):
        line_num = get_line_number(source_text, offset)
        raise JSONSyntaxError("Expected ':' or quotes after key", line_num)

    return key, content[1:].strip(), offset + 1


def parse_object_value(content, source_text, offset):
    value, remainder = parse_json_value(content, source_text, offset)
    consumed = len(content) - len(remainder)

    return value, remainder.strip(), offset + consumed


def process_comma_or_end(content, source_text, offset):
    if content.startswith(','):
        return content[1:].strip(), offset + 1
    elif content.startswith('}'):
        return '', offset
    elif content:
        line_num = get_line_number(source_text, offset)
        raise JSONSyntaxError("Expected ',' or '{' or quotes after value", line_num)

    return '', offset


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
