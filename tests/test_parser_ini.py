import unittest

from config_lib.parsers.parser_ini import (
    parse_ini_string,
    INISyntaxError,
)

class TestINIParser(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(parse_ini_string(""), {})

    def test_comments_and_blank_lines(self):
        ini = (
            "; comment line 1\n"
            "# comment line 2\n"
            "   \n"
        )
        self.assertEqual(parse_ini_string(ini), {})

    def test_simple_key_value_no_section(self):
        ini = "key=value"
        self.assertEqual(parse_ini_string(ini), {"key": "value"})

    def test_multiple_key_values_and_types(self):
        ini = (
            "[section]\n"
            "int_key=42\n"
            "float_key=3.14\n"
            "bool_true=true\n"
            "bool_false=False\n"
            "null_val=null\n"
            "list_key=one, two, three\n"
            "string_key=hello world"
        )
        result = parse_ini_string(ini)
        sec = result.get("section")
        self.assertIsInstance(sec.get("int_key"), int)
        self.assertEqual(sec.get("int_key"), 42)
        self.assertIsInstance(sec.get("float_key"), float)
        self.assertAlmostEqual(sec.get("float_key"), 3.14)
        self.assertIs(sec.get("bool_true"), True)
        self.assertIs(sec.get("bool_false"), False)
        self.assertIsNone(sec.get("null_val"))
        self.assertEqual(sec.get("list_key"), ["one", "two", "three"])
        self.assertEqual(sec.get("string_key"), "hello world")

    def test_nested_sections(self):
        ini = "[parent.child]\nkey=value"
        result = parse_ini_string(ini)
        self.assertIn("parent", result)
        self.assertIn("child", result["parent"])
        self.assertEqual(result["parent"]["child"]["key"], "value")

    def test_empty_section_name_raises_error(self):
        with self.assertRaises(INISyntaxError) as cm:
            parse_ini_string("[]")
        self.assertIn("Empty section name", str(cm.exception))

    def test_invalid_line_raises_error(self):
        with self.assertRaises(INISyntaxError) as cm:
            parse_ini_string("[section]\ninvalid_line")
        self.assertIn("Invalid line", str(cm.exception))

    def test_missing_key_before_equal_raises_error(self):
        with self.assertRaises(INISyntaxError) as cm:
            parse_ini_string("[sec]\n= value")
        self.assertIn("Missing key", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
