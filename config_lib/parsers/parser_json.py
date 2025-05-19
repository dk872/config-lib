class JSONSyntaxError(Exception):
    def __init__(self, message, line_number=None):
        prefix = f"JSON Syntax Error on line {line_number}" if line_number else "JSON Syntax Error"
        super().__init__(f"{prefix}: {message}")


def get_line_number(text, pos):
    return text.count('\n', 0, pos) + 1


def parse_escape_sequence(text, index, source_text, offset):
    index += 1
    if index >= len(text):
        line_num = get_line_number(source_text, offset + index)
        raise JSONSyntaxError("Unexpected end after backslash", line_num)

    escape_char = text[index]
    escaped = handle_escape_sequence(escape_char, text, index, source_text, offset)

    if escape_char == 'u':
        index += 4  # Skip 4 hex digits

    return index, escaped


def handle_escape_sequence(escape_char, content, idx, original_text, start_pos):
    if escape_char == '"':
        return '"'
    elif escape_char == '\\':
        return '\\'
    elif escape_char == '/':
        return '/'
    elif escape_char == 'b':
        return '\b'
    elif escape_char == 'f':
        return '\f'
    elif escape_char == 'n':
        return '\n'
    elif escape_char == 'r':
        return '\r'
    elif escape_char == 't':
        return '\t'
    elif escape_char == 'u':
        return handle_unicode_escape(content, idx, original_text, start_pos)
    else:
        line_num = get_line_number(original_text, start_pos + idx)
        raise JSONSyntaxError(f"Invalid escape character: \\{escape_char}", line_num)


def handle_unicode_escape(content, idx, original_text, start_pos):
    line_num = get_line_number(original_text, start_pos + idx)

    # Expect 4 hex digits after \u
    if idx + 4 >= len(content):
        raise JSONSyntaxError("Incomplete unicode escape sequence", line_num)

    hex_digits = content[idx + 1:idx + 5]

    try:
        return chr(int(hex_digits, 16))
    except ValueError:
        raise JSONSyntaxError(f"Invalid unicode escape: \\u{hex_digits}", line_num)


def parse_json_string_value(text, source_text, offset):
    if not text.startswith('"'):
        line_num = get_line_number(source_text, offset)
        raise JSONSyntaxError("Expected string", line_num)

    index = 1
    result = []

    while index < len(text):
        char = text[index]
        if char == '"':
            return ''.join(result), text[index + 1:]
        if char == '\\':
            index, escaped = parse_escape_sequence(text, index, source_text, offset)
            result.append(escaped)
        else:
            result.append(char)
        index += 1

    line_num = get_line_number(source_text, offset + index)
    raise JSONSyntaxError("Unterminated string", line_num)


def parse_json_number(text, source_text, offset):
    raw_number, remainder_index = read_number_prefix(text)
    validate_number_format(raw_number, source_text, offset)

    try:
        if any(c in raw_number for c in ('.', 'e', 'E')):
            return float(raw_number)
        return int(raw_number)
    except ValueError:
        line_num = get_line_number(source_text, offset + remainder_index)
        raise JSONSyntaxError(f"Invalid number: {raw_number}", line_num)


def read_number_prefix(text):
    num_chars = []
    index = 0

    while index < len(text) and (text[index].isdigit() or text[index] in '-+.eE'):
        num_chars.append(text[index])
        index += 1

    return ''.join(num_chars), index


def validate_number_format(number_str, source_text, offset):
    line_num = get_line_number(source_text, offset)

    if number_str.startswith('0') and len(number_str) > 1 and number_str[1].isdigit():
        raise JSONSyntaxError(f"Invalid number with leading zero: {number_str}", line_num)

    if number_str.startswith('-0') and len(number_str) > 2 and number_str[2].isdigit():
        raise JSONSyntaxError(f"Invalid negative number with leading zero: {number_str}", line_num)

    if number_str.endswith('.') or number_str.startswith('.') or number_str.startswith('-.') or number_str.startswith(
            '+.'):
        raise JSONSyntaxError(f"Invalid float number format: {number_str}", line_num)


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
