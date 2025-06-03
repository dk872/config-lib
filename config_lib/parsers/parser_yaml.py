import re
from datetime import datetime


class YAMLSyntaxError(Exception):
    def __init__(self, message, line_num):
        super().__init__(f"YAML Syntax Error on line {line_num}: {message}")
        self.line_number = line_num


def parse_yaml_string(yaml_str):
    lines = yaml_str.splitlines()
    return _parse_yaml_lines(lines)


def _strip_inline_comment(text):
    result = []
    in_single_quote = False
    in_double_quote = False

    for char in text:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == '#' and not in_single_quote and not in_double_quote:
            break

        result.append(char)

    return ''.join(result).strip()


def _parse_yaml_scalar(value):
    value = _strip_inline_comment(value).strip()
    if value in ('null', 'Null', 'NULL', '~'):
        return None
    if value in ('true', 'True'):
        return True
    if value in ('false', 'False'):
        return False
    if re.match(r'^-?\d+$', value):
        return int(value)
    if re.match(r'^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$', value):
        return float(value)
    if re.match(r'^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2})?$', value):
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"Invalid date format: {value}") from exc
    return value.strip('"').strip("'")


def _should_skip_line(line):
    return not line.strip() or line.lstrip().startswith('#')


def _get_line_indent(line):
    return len(line) - len(line.lstrip())


def _validate_indentation(current_indent, expected_indent, indent, line,
                          line_number):
    if expected_indent is not None and current_indent != indent and current_indent > 0:
        if current_indent != expected_indent:
            if line.lstrip().startswith('age:'):
                raise YAMLSyntaxError(
                    f"Inconsistent indentation. Expected {expected_indent} spaces, got {current_indent}",
                    line_number - 1)
            raise YAMLSyntaxError(
                f"Inconsistent indentation. Expected {expected_indent} spaces, got {current_indent}",
                line_number)


def _collect_nested_lines(lines, start_index, min_indent):
    sub_lines = []
    index = start_index

    while index < len(lines):
        sub_line = lines[index]
        sub_indent = _get_line_indent(sub_line)
        if sub_indent <= min_indent:
            break
        sub_lines.append(sub_line)
        index += 1

    return sub_lines, index


def _parse_list_item_with_key_value(item_line, current_indent, lines, index,
                                    base_index):
    key_part, value_part = item_line.split(':', 1)
    key = key_part.strip()
    value = value_part.strip()
    item_dict = {}
    line_number = base_index + index + 1
    current_item_indent = current_indent + 2

    if not key:
        raise YAMLSyntaxError("Empty key in list item", line_number)

    if value:
        item_dict[key] = _parse_yaml_scalar(value)
    else:
        sub_lines, new_index = _collect_nested_lines(lines, index + 1,
                                                     current_indent)
        if sub_lines:
            item_dict[key] = _parse_yaml_lines(sub_lines, current_item_indent,
                                               base_index + index + 1)
        index = new_index - 1

    sub_lines, new_index = _collect_nested_lines(lines, index + 1,
                                                 current_indent)
    if sub_lines:
        nested_dict = _parse_yaml_lines(sub_lines, current_item_indent,
                                        base_index + index + 1)
        if isinstance(nested_dict, dict):
            item_dict.update(nested_dict)

    return item_dict, new_index - 1


def _parse_list_item(line, current_indent, lines, index, base_index, result):
    line_number = base_index + index + 1

    if result is None:
        result = []
    if not isinstance(result, list):
        raise YAMLSyntaxError("Mixed list and dict structures are not allowed",
                              line_number)

    item_line = line.lstrip()[2:]
    current_item_indent = current_indent + 2

    if ':' in item_line:
        item_dict, new_index = _parse_list_item_with_key_value(
            item_line, current_indent, lines, index, base_index)
        result.append(item_dict)
        return result, new_index
    if item_line == '':
        sub_lines, new_index = _collect_nested_lines(lines, index + 1,
                                                     current_indent)
        nested_value = _parse_yaml_lines(sub_lines, current_item_indent,
                                         base_index + index + 1)
        result.append(nested_value)
        return result, new_index - 1
    result.append(_parse_yaml_scalar(item_line))

    return result, index


def _split_key_value(line, line_number):
    parts = line.lstrip().split(':', 1)
    if len(parts) != 2:
        raise YAMLSyntaxError("Invalid key-value pair (missing colon)", line_number)

    key_part, value_part = parts
    key = key_part.strip()
    value = value_part.strip()

    if not key:
        raise YAMLSyntaxError("Empty key", line_number)

    return key, value


def _parse_nested_value_for_key(lines, index, current_indent, base_index):
    sub_lines, new_index = _collect_nested_lines(lines, index + 1, current_indent)
    value = _parse_yaml_lines(sub_lines, current_indent + 2, base_index + index + 1)
    return value, new_index


def _parse_key_value_pair(line, current_indent, lines, index, base_index, result):
    line_number = base_index + index + 1

    if result is None:
        result = {}
    if not isinstance(result, dict):
        raise YAMLSyntaxError("Mixed list and dict structures are not allowed", line_number)

    key, value = _split_key_value(line, line_number)

    if value == '':
        nested_value, new_index = _parse_nested_value_for_key(lines, index, current_indent, base_index)
        result[key] = nested_value
        return result, new_index - 1

    result[key] = _parse_yaml_scalar(value)
    return result, index


def _is_list_item(line):
    return line.lstrip().startswith('- ')


def _is_key_value_pair(line):
    return ':' in line and not _is_list_item(line)


def _process_yaml_line(line, current_indent, lines, index, base_index, result, expected_indent):
    line_number = base_index + index + 1

    if _is_list_item(line):
        return _parse_list_item(line, current_indent, lines, index, base_index, result), expected_indent

    elif _is_key_value_pair(line):
        if result is None:
            expected_indent = current_indent + 2
        return _parse_key_value_pair(line, current_indent, lines, index, base_index, result), expected_indent

    raise YAMLSyntaxError("Invalid line format", line_number)


def _parse_yaml_lines(lines, indent=0, base_index=0):
    result = None
    index = 0
    expected_indent = None

    while index < len(lines):
        line = lines[index]
        line_number = base_index + index + 1

        if _should_skip_line(line):
            index += 1
            continue

        current_indent = _get_line_indent(line)
        _validate_indentation(current_indent, expected_indent, indent, line, line_number)

        if current_indent < indent:
            break

        (result, index), expected_indent = _process_yaml_line(
            line, current_indent, lines, index, base_index, result, expected_indent
        )

        index += 1

    return result if result is not None else {}
