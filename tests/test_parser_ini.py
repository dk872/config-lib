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

    def test_case_insensitive_booleans(self):
        ini = (
            "[section]\n"
            "bool1=TRUE\n"
            "bool2=False\n"
            "bool3=true\n"
            "bool4=false"
        )
        result = parse_ini_string(ini)
        sec = result["section"]
        self.assertTrue(sec["bool1"])
        self.assertFalse(sec["bool2"])
        self.assertTrue(sec["bool3"])
        self.assertFalse(sec["bool4"])

    def test_whitespace_handling(self):
        ini = (
            "[section]\n"
            "  key1  =  value1  \n"
            "key2=  value with spaces  "
        )
        result = parse_ini_string(ini)
        sec = result["section"]
        self.assertEqual(sec["key1"], "value1")
        self.assertEqual(sec["key2"], "value with spaces")

    def test_empty_values(self):
        ini = (
            "[section]\n"
            "empty_key=\n"
            "space_key= "
        )
        result = parse_ini_string(ini)
        sec = result["section"]
        self.assertEqual(sec["empty_key"], "")
        self.assertEqual(sec["space_key"], "")

    def test_multiple_equals_in_value(self):
        ini = "key=value=with=equals"
        result = parse_ini_string(ini)
        self.assertEqual(result["key"], "value=with=equals")

    def test_section_overwrite_value_error(self):
        ini = (
            "key=value\n"
            "[key.subsection]\n"
            "subkey=subvalue"
        )
        with self.assertRaises(INISyntaxError) as cm:
            parse_ini_string(ini)
        self.assertIn("already exists as non-section value", str(cm.exception))

    def test_numeric_edge_cases(self):
        ini = (
            "[numbers]\n"
            "zero=0\n"
            "negative=-42\n"
            "negative_float=-3.14\n"
            "scientific=1.23e-4\n"
            "leading_zero=007\n"
            "just_dot=.\n"
            "multiple_dots=1.2.3"
        )
        result = parse_ini_string(ini)
        sec = result["numbers"]

        self.assertEqual(sec["zero"], 0)
        self.assertEqual(sec["negative"], -42)
        self.assertEqual(sec["negative_float"], -3.14)
        self.assertEqual(sec["scientific"], 1.23e-4)
        self.assertEqual(sec["leading_zero"], 7)
        self.assertEqual(sec["just_dot"], ".")
        self.assertEqual(sec["multiple_dots"], "1.2.3")

    def test_list_with_empty_elements(self):
        ini = (
            "[lists]\n"
            "empty_elem=one, , three\n"
            "trailing_comma=one, two,\n"
            "leading_comma=, one, two\n"
            "only_commas=, , ,"
        )
        result = parse_ini_string(ini)
        sec = result["lists"]

        self.assertEqual(sec["empty_elem"], ["one", "", "three"])
        self.assertEqual(sec["trailing_comma"], ["one", "two", ""])
        self.assertEqual(sec["leading_comma"], ["", "one", "two"])
        self.assertEqual(sec["only_commas"], ["", "", "", ""])


if __name__ == '__main__':
    unittest.main()
