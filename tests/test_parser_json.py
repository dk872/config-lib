import pytest
from config_lib.parsers.parser_json import (
    parse_json_string,
    JSONSyntaxError,
)


# ====== VALID CASES ======

# === EMPTY ===

def test_parse_empty_input():
    assert parse_json_string('') == {}


def test_parse_empty_object():
    assert parse_json_string('{}') == {}


def test_parse_empty_array():
    assert parse_json_string('[]') == []


# === SIMPLE STRUCTURES ===

def test_parse_booleans_and_null():
    assert parse_json_string('true') is True
    assert parse_json_string('false') is False
    assert parse_json_string('null') is None


def test_parse_simple_object():
    assert parse_json_string('{"key": "value"}') == {"key": "value"}


def test_parse_object_with_whitespace():
    assert parse_json_string('{ \n"key"\t:\r"value"\n }') == {"key": "value"}


def test_parse_array_of_numbers():
    assert parse_json_string('[1, 2, 3]') == [1, 2, 3]


def test_parse_mixed_numbers_and_strings_in_array():
    assert parse_json_string('[1, "2", 3]') == [1, "2", 3]


def test_parse_array_with_whitespace():
    assert parse_json_string('[ \n1,\t2,\r3 \n]') == [1, 2, 3]


def test_parse_mixed_array():
    assert parse_json_string('[1, "text", null, true, false]') == [1, "text", None, True, False]


# === STRINGS ===

def test_parse_escaped_string_characters():
    assert parse_json_string(r'"He said: \"Hi!\""') == 'He said: "Hi!"'
    assert parse_json_string(r'"string with \"quotes\" and \\backslash"') == 'string with "quotes" and \\backslash'
    assert parse_json_string(r'"C:\\\\path\\\\to\\\\file"') == r'C:\\path\\to\\file'
    assert parse_json_string(r'"https:\/\/example.com"') == 'https://example.com'
    assert parse_json_string(r'"a\b"') == 'a\b'
    assert parse_json_string(r'"a\f"') == 'a\f'
    assert parse_json_string(r'"line1\nline2"') == 'line1\nline2'
    assert parse_json_string(r'"a\rb"') == 'a\rb'
    assert parse_json_string(r'"a\tb"') == 'a\tb'


def test_parse_unicode_strings():
    assert parse_json_string('"\\u041f\\u0440\\u0438\\u0432\\u0456\\u0442"') == "Привіт"
    assert parse_json_string('"\\u00F6\\u00E4\\u00FC"') == "öäü"


def test_parse_special_control_chars():
    assert parse_json_string('"\\b\\f\\n\\r\\t"') == "\b\f\n\r\t"


# === NUMBERS ===

def test_parse_integers():
    assert parse_json_string('123') == 123
    assert parse_json_string('-468') == -468
    assert parse_json_string('999999999') == 999999999
    assert parse_json_string('0') == 0
    assert parse_json_string('-2147483648') == -2147483648


def test_parse_floats():
    assert parse_json_string('3.14') == 3.14
    assert parse_json_string('-15.96') == -15.96
    assert parse_json_string('0.0') == 0.0
    assert parse_json_string('123.456') == 123.456
    assert parse_json_string('-99759.9549') == -99759.9549


def test_parse_scientific_notation_numbers():
    assert parse_json_string('1e10') == 1e10
    assert parse_json_string('2.5E-5') == 2.5E-5
    assert parse_json_string('-3.14e+2') == -314.0
    assert parse_json_string('1e3') == 1e3
    assert parse_json_string('5E-1') == 5E-1


# === NESTED STRUCTURES ===

def test_parse_nested_object():
    assert parse_json_string('{"outer": {"inner": 123}}') == {"outer": {"inner": 123}}


def test_parse_deeply_nested_structures():
    json_str = '{"a": {"b": {"c": {"d": {"e": {"f": {"g": 42}}}}}}}'
    assert parse_json_string(json_str)["a"]["b"]["c"]["d"]["e"]["f"]["g"] == 42


def test_parse_nested_objects_and_arrays():
    json_str = '''
    {
        "config": {
            "version": 1,
            "settings": {
                "features": ["a", "b", "c"],
                "enabled": true
            }
        }
    }
    '''
    result = parse_json_string(json_str)
    assert result["config"]["settings"]["features"] == ["a", "b", "c"]
    assert result["config"]["settings"]["enabled"] is True


# === COMPLEX STRUCTURES ===

def test_parse_array_of_objects():
    json_str = '''
    [
        {"id": 1},
        {"id": 2},
        {"id": 3}
    ]
    '''
    result = parse_json_string(json_str)
    assert result == [{"id": 1}, {"id": 2}, {"id": 3}]


def test_parse_object_with_various_types():
    json_str = '''
    {
        "name": "Alice",
        "age": 30,
        "height": 1.65,
        "isStudent": false,
        "skills": ["Python", "C++"],
        "extra": null
    }
    '''
    result = parse_json_string(json_str)
    assert result["name"] == "Alice"
    assert result["age"] == 30
    assert result["height"] == 1.65
    assert result["isStudent"] is False
    assert result["skills"] == ["Python", "C++"]
    assert result["extra"] is None


def test_parse_complex_nested_structure():
    json_str = '''
    {
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "preferences": {
                    "theme": "dark",
                    "notifications": true
                }
            },
            {
                "id": 2,
                "name": "Bob",
                "preferences": {
                    "theme": "light",
                    "notifications": false
                }
            }
        ],
        "settings": {
            "version": "1.2.3",
            "features": [1, 2, 3],
            "active": true
        }
    }
    '''
    result = parse_json_string(json_str)
    assert len(result["users"]) == 2
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][1]["preferences"]["theme"] == "light"
    assert result["settings"]["features"] == [1, 2, 3]


def test_parse_line_number_reporting():
    json_str = '{\n"a": 1,\n"b": \n[2,3,4}}'
    try:
        parse_json_string(json_str)
    except JSONSyntaxError as e:
        assert "line 3" in str(e)
    else:
        pytest.fail("Expected JSONSyntaxError")


# ====== INVALID CASES ======


# === STRINGS ===

def test_invalid_unquoted_string_value():
    with pytest.raises(JSONSyntaxError, match="Expected value. Possibly missing quotes for string."):
        parse_json_string('{"key": value"}')


def test_parse_invalid_value_missing_quotes():
    with pytest.raises(JSONSyntaxError, match="Unterminated string"):
        parse_json_string('{"key": "value}')


def test_invalid_extra_character():
    with pytest.raises(JSONSyntaxError, match="Expected string key in double quotes"):
        parse_json_string('{"key": "value", d"another": 2}')


# === NUMBERS ===

def test_parse_invalid_number_with_multiple_signs():
    with pytest.raises(JSONSyntaxError, match="Invalid number"):
        parse_json_string('+-1')


def test_parse_invalid_exponent_format():
    with pytest.raises(JSONSyntaxError, match="Invalid number"):
        parse_json_string('1e')


def test_parse_invalid_leading_zeros():
    with pytest.raises(JSONSyntaxError, match="Invalid number"):
        parse_json_string('0123')


def test_parse_invalid_malformed_number():
    with pytest.raises(JSONSyntaxError, match="Invalid number"):
        parse_json_string('1.2.3')


def test_parse_invalid_positive_float_dot_behind():
    with pytest.raises(JSONSyntaxError, match="Invalid float number format"):
        parse_json_string('12.')


def test_parse_invalid_negative_float_dot_behind():
    with pytest.raises(JSONSyntaxError, match="Invalid float number format"):
        parse_json_string('-12.')


def test_parse_invalid_positive_float_dot_in_front():
    with pytest.raises(JSONSyntaxError, match="Invalid float number format"):
        parse_json_string('.16')


def test_parse_invalid_negative_float_dot_in_front():
    with pytest.raises(JSONSyntaxError, match="Invalid float number format"):
        parse_json_string('-.16')


# === ARRAYS ===

def test_parse_invalid_array_missing_closing():
    with pytest.raises(JSONSyntaxError, match="Invalid JSON array"):
        parse_json_string('[1, 2, 3')


def test_parse_invalid_array_separator():
    with pytest.raises(JSONSyntaxError, match="Expected ',' or ']' or quotes after value"):
        parse_json_string('[1; 2]')


def test_parse_invalid_array_in_object_missing_closing():
    with pytest.raises(JSONSyntaxError, match=r"No matching closing brace for '\['"):
        parse_json_string('{"numbers": [1, 2, 3}')


def test_invalid_unclosed_array_in_object():
    with pytest.raises(JSONSyntaxError, match="No matching closing brace"):
        parse_json_string('{"key": [1, 2, 3}')


# === OBJECTS ===

def test_parse_invalid_object_missing_closing_brace():
    with pytest.raises(JSONSyntaxError, match="Invalid JSON object"):
        parse_json_string('{"key": "value"')


def test_parse_invalid_object_separator():
    with pytest.raises(JSONSyntaxError, match="Expected ',' or '{' or quotes after value"):
        parse_json_string('{"a": 1; "b": 2}')


def test_parse_invalid_object_missing_key_quotes():
    with pytest.raises(JSONSyntaxError, match="Expected string key in double quotes"):
        parse_json_string('{key": "value"}')


def test_parse_invalid_key_missing_colon():
    with pytest.raises(JSONSyntaxError, match="Expected ':' or quotes after key"):
        parse_json_string('{"key: "value"}')


def test_parse_invalid_missing_colon_between_key_and_value():
    with pytest.raises(JSONSyntaxError, match="Expected ':' or quotes after key"):
        parse_json_string('{"key" "value"}')


def test_parse_invalid_missing_comma_between_pairs():
    with pytest.raises(JSONSyntaxError, match=r"Expected ',' or '\{' or quotes after value"):
        parse_json_string('{"key": "value" "another": 2}')


# === ESCAPE SEQUENCES ===

def test_parse_invalid_escape_sequence():
    with pytest.raises(JSONSyntaxError, match="Invalid escape character"):
        parse_json_string(r'"bad\escape"')


def test_parse_invalid_unicode_escape_short():
    with pytest.raises(JSONSyntaxError, match="Incomplete unicode escape sequence"):
        parse_json_string(r'"\u12"')


def test_parse_invalid_unicode_escape_non_hex():
    with pytest.raises(JSONSyntaxError, match="Invalid unicode escape"):
        parse_json_string(r'"\uZZZZ"')
