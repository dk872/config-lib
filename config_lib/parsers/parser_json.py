class JSONSyntaxError(Exception):
    def __init__(self, message, line_number=None):
        prefix = f"JSON Syntax Error on line {line_number}" if line_number else "JSON Syntax Error"
        super().__init__(f"{prefix}: {message}")


def get_line_number(text, pos):
    return text.count('\n', 0, pos) + 1


def parse_json_value(content, original_text, start_pos):
    content = content.strip()

    if not content:
        line_num = get_line_number(original_text, start_pos)
        raise JSONSyntaxError("Unexpected end of input", line_num)

    if content.startswith('{'):
        return parse_json_object_value(content, original_text, start_pos)
    elif content.startswith('['):
        return parse_json_array_value(content, original_text, start_pos)
    elif content.startswith('"'):
        return parse_json_string_value(content, original_text, start_pos)
    elif content.startswith('true'):
        return parse_boolean_value(content, True)
    elif content.startswith('false'):
        return parse_boolean_value(content, False)
    elif content.startswith('null'):
        return parse_null_value(content)
    else:
        return parse_json_number_value(content, original_text, start_pos)


def parse_json_object_value(content, original_text, start_pos):
    end = find_matching_brace(content, '{', '}', original_text, start_pos)
    return parse_json_object(content[:end + 1], original_text, start_pos), content[end + 1:]


def parse_json_array_value(content, original_text, start_pos):
    end = find_matching_brace(content, '[', ']', original_text, start_pos)
    return parse_json_array(content[:end + 1], original_text, start_pos), content[end + 1:]


def parse_boolean_value(content, value):
    return value, content[len(str(value)):]


def parse_null_value(content):
    return None, content[4:]


def parse_json_number_value(content, original_text, start_pos):
    num_str = ''
    i = 0

    while i < len(content) and (content[i].isdigit() or content[i] in '.-+eE'):
        num_str += content[i]
        i += 1

    if not num_str:
        line_num = get_line_number(original_text, start_pos)
        raise JSONSyntaxError("Expected value. Possibly missing quotes for string.", line_num)

    return parse_json_number(num_str, original_text, start_pos), content[i:]


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
