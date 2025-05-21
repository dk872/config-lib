import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config_lib.parsers.parser_yaml import (parse_yaml_string, YAMLSyntaxError,
                                            _parse_yaml_scalar,
                                            _parse_yaml_lines)


class TestYAMLParser(unittest.TestCase):

    def test_parse_scalar_values(self):
        """Test parsing of different scalar types"""
        self.assertIsNone(_parse_yaml_scalar("null"))
        self.assertIsNone(_parse_yaml_scalar("Null"))
        self.assertIsNone(_parse_yaml_scalar("NULL"))
        self.assertIsNone(_parse_yaml_scalar("~"))

        self.assertTrue(_parse_yaml_scalar("true"))
        self.assertTrue(_parse_yaml_scalar("True"))
        self.assertFalse(_parse_yaml_scalar("false"))
        self.assertFalse(_parse_yaml_scalar("False"))

        self.assertEqual(_parse_yaml_scalar("42"), 42)
        self.assertEqual(_parse_yaml_scalar("-17"), -17)
        self.assertEqual(_parse_yaml_scalar("3.14"), 3.14)
        self.assertEqual(_parse_yaml_scalar("-2.5"), -2.5)

        self.assertEqual(_parse_yaml_scalar("'hello'"), "hello")
        self.assertEqual(_parse_yaml_scalar('"world"'), "world")
        self.assertEqual(_parse_yaml_scalar("plain text"), "plain text")

        date_str = "2023-01-15"
        expected_date = datetime(2023, 1, 15)
        self.assertEqual(_parse_yaml_scalar(date_str), expected_date)

        datetime_str = "2023-01-15T14:30:45"
        expected_datetime = datetime(2023, 1, 15, 14, 30, 45)
        self.assertEqual(_parse_yaml_scalar(datetime_str), expected_datetime)

    def test_simple_dict(self):
        """Test parsing a simple dictionary"""
        yaml_str = """
name: John Doe
age: 30
is_active: true
"""
        expected = {"name": "John Doe", "age": 30, "is_active": True}
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_nested_dict(self):
        """Test parsing nested dictionaries"""
        yaml_str = """
person:
  name: Jane Doe
  age: 28
  address:
    street: 123 Main St
    city: Anytown
    zip: 12345
"""
        expected = {
            "person": {
                "name": "Jane Doe",
                "age": 28,
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip": 12345
                }
            }
        }
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_simple_list(self):
        """Test parsing a simple list"""
        yaml_str = """
- apple
- banana
- cherry
"""
        expected = ["apple", "banana", "cherry"]
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_list_of_dicts(self):
        """Test parsing a list of dictionaries"""
        yaml_str = """
- name: John
  age: 30
- name: Jane
  age: 28
- name: Bob
  age: 35
"""
        expected = [{
            "name": "John",
            "age": 30
        }, {
            "name": "Jane",
            "age": 28
        }, {
            "name": "Bob",
            "age": 35
        }]
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_dict_with_list(self):
        """Test parsing a dictionary containing a list"""
        yaml_str = """
team:
  name: Developers
  members:
    - name: John
      role: Frontend
    - name: Jane
      role: Backend
    - name: Bob
      role: DevOps
"""
        expected = {
            "team": {
                "name":
                "Developers",
                "members": [{
                    "name": "John",
                    "role": "Frontend"
                }, {
                    "name": "Jane",
                    "role": "Backend"
                }, {
                    "name": "Bob",
                    "role": "DevOps"
                }]
            }
        }
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_complex_nested_structure(self):
        """Test parsing a complex nested structure"""
        yaml_str = """
organization:
  name: Acme Corp
  founded: 2005-01-15
  active: true
  departments:
    - name: Engineering
      head: John Smith
      teams:
        - name: Frontend
          size: 5
        - name: Backend
          size: 8
    - name: Marketing
      head: Jane Doe
      budget: 100000
  locations:
    headquarters:
      address: 123 Main St
      city: Metropolis
    branch:
      address: 456 Side Ave
      city: Smallville
"""
        expected = {
            "organization": {
                "name":
                "Acme Corp",
                "founded":
                datetime(2005, 1, 15),
                "active":
                True,
                "departments": [{
                    "name":
                    "Engineering",
                    "head":
                    "John Smith",
                    "teams": [{
                        "name": "Frontend",
                        "size": 5
                    }, {
                        "name": "Backend",
                        "size": 8
                    }]
                }, {
                    "name": "Marketing",
                    "head": "Jane Doe",
                    "budget": 100000
                }],
                "locations": {
                    "headquarters": {
                        "address": "123 Main St",
                        "city": "Metropolis"
                    },
                    "branch": {
                        "address": "456 Side Ave",
                        "city": "Smallville"
                    }
                }
            }
        }
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_empty_doc(self):
        """Test parsing an empty document"""
        yaml_str = ""
        expected = {}
        self.assertEqual(parse_yaml_string(yaml_str), expected)

        yaml_str = "# just a comment"
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_comments(self):
        """Test handling of comments"""
        yaml_str = """
# This is a comment
name: John Doe  # Inline comment
age: 30
# Another comment
active: true
"""
        expected = {"name": "John Doe", "age": 30, "active": True}
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_indentation_errors(self):
        """Test error handling for indentation issues"""
        yaml_str = """
person:
  name: John
 age: 30  # Wrong indentation
"""
        with self.assertRaises(YAMLSyntaxError) as context:
            parse_yaml_string(yaml_str)
        self.assertEqual(context.exception.line_number, 3)

    def test_mixed_structure_error(self):
        """Test error for mixing list and dict structures"""
        yaml_str = """
- item1
key: value
"""
        with self.assertRaises(YAMLSyntaxError) as context:
            parse_yaml_string(yaml_str)

    def test_empty_key_error(self):
        """Test error for empty keys"""
        yaml_str = """
valid_key: value
: invalid_value
"""
        with self.assertRaises(YAMLSyntaxError) as context:
            parse_yaml_string(yaml_str)

    def test_invalid_line_format(self):
        """Test error for invalid line format"""
        yaml_str = """
valid_key: value
invalid line without colon or dash
"""
        with self.assertRaises(YAMLSyntaxError) as context:
            parse_yaml_string(yaml_str)

    def test_empty_list_item_with_nested_content(self):
        """Test handling of empty list items with nested content"""
        yaml_str = """
- 
  name: John
  age: 30
- 
  name: Jane
  age: 28
"""
        expected = [{"name": "John", "age": 30}, {"name": "Jane", "age": 28}]
        self.assertEqual(parse_yaml_string(yaml_str), expected)

    def test_multiline_values(self):
        """Test handling of multiline values in nested structures"""
        yaml_str = """
person:
  bio: This is a multiline
       description that spans
       multiple lines
  skills:
    - programming
    - design
    - communication
"""
        expected = {
            "person": {
                "bio":
                "This is a multiline description that spans multiple lines",
                "skills": ["programming", "design", "communication"]
            }
        }

    def test_empty_value(self):
        """Test handling of empty values"""
        yaml_str = """
key1: 
key2: value2
"""
        expected = {"key1": {}, "key2": "value2"}
        self.assertEqual(parse_yaml_string(yaml_str), expected)


if __name__ == "__main__":
    unittest.main()
