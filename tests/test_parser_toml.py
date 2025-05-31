import unittest
import sys
import os

# Add the parent directory to the Python path so we can import from parsers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_lib.parsers.parser_toml import TOMLParser, TOMLSyntaxError, parse_toml_string


class TestTOMLParser(unittest.TestCase):
    """Test suite for the TOML parser."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = TOMLParser()
    
    def test_example_toml_file(self):
        """Test parsing the provided example TOML file."""
        example_toml = '''date_of_creation = 2025-05-12T14:00:00Z
users = ["user1", "user2"]
[database]
host = "localhost"
port = 5432
user = "admin"
password = "password123"
is_active = true
last_login = ""
[logging]
level = "debug"
output = "logfile.txt"
log_rotation_interval = 1.85
[network]
timeout = 30
retries = 3'''
        
        result = self.parser.parse(example_toml)
        
        # Test root level values
        self.assertEqual(result['date_of_creation'], '2025-05-12T14:00:00Z')
        self.assertEqual(result['users'], ['user1', 'user2'])
        
        # Test database section
        self.assertIn('database', result)
        db = result['database']
        self.assertEqual(db['host'], 'localhost')
        self.assertEqual(db['port'], 5432)
        self.assertEqual(db['user'], 'admin')
        self.assertEqual(db['password'], 'password123')
        self.assertTrue(db['is_active'])
        self.assertEqual(db['last_login'], '')
        
        # Test logging section
        self.assertIn('logging', result)
        log = result['logging']
        self.assertEqual(log['level'], 'debug')
        self.assertEqual(log['output'], 'logfile.txt')
        self.assertEqual(log['log_rotation_interval'], 1.85)
        
        # Test network section
        self.assertIn('network', result)
        net = result['network']
        self.assertEqual(net['timeout'], 30)
        self.assertEqual(net['retries'], 3)


class TestBasicValues(unittest.TestCase):
    """Test parsing of basic value types."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_string_values(self):
        """Test parsing string values."""
        toml = '''
        name = "John Doe"
        single_quote = 'Hello World'
        empty_string = ""
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['single_quote'], 'Hello World')
        self.assertEqual(result['empty_string'], '')
    
    def test_boolean_values(self):
        """Test parsing boolean values."""
        toml = '''
        enabled = true
        disabled = false
        mixed_case_true = True
        mixed_case_false = FALSE
        '''
        result = self.parser.parse(toml)
        self.assertTrue(result['enabled'])
        self.assertFalse(result['disabled'])
        self.assertTrue(result['mixed_case_true'])
        self.assertFalse(result['mixed_case_false'])
    
    def test_integer_values(self):
        """Test parsing integer values."""
        toml = '''
        positive = 42
        negative = -17
        zero = 0
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['positive'], 42)
        self.assertEqual(result['negative'], -17)
        self.assertEqual(result['zero'], 0)
    
    def test_float_values(self):
        """Test parsing float values."""
        toml = '''
        pi = 3.14159
        negative_float = -2.5
        scientific = 1.23e4
        '''
        result = self.parser.parse(toml)
        self.assertAlmostEqual(result['pi'], 3.14159)
        self.assertAlmostEqual(result['negative_float'], -2.5)
        self.assertAlmostEqual(result['scientific'], 12300.0)
    
    def test_datetime_values(self):
        """Test parsing datetime values (returned as strings)."""
        toml = '''
        date1 = 2025-05-12T14:00:00Z
        date2 = 2025-12-31 23:59:59
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['date1'], '2025-05-12T14:00:00Z')
        self.assertEqual(result['date2'], '2025-12-31 23:59:59')


class TestArrays(unittest.TestCase):
    """Test parsing of arrays."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_simple_arrays(self):
        """Test parsing simple arrays."""
        toml = '''
        numbers = [1, 2, 3, 4, 5]
        strings = ["apple", "banana", "cherry"]
        booleans = [true, false, true]
        empty = []
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['numbers'], [1, 2, 3, 4, 5])
        self.assertEqual(result['strings'], ['apple', 'banana', 'cherry'])
        self.assertEqual(result['booleans'], [True, False, True])
        self.assertEqual(result['empty'], [])
    
    def test_mixed_arrays(self):
        """Test parsing arrays with mixed types."""
        toml = '''
        mixed = [1, "two", true, 4.5]
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['mixed'], [1, 'two', True, 4.5])
    
    def test_nested_arrays(self):
        """Test parsing nested arrays."""
        toml = '''
        nested = [[1, 2], [3, 4], [5, 6]]
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['nested'], [[1, 2], [3, 4], [5, 6]])
    
    def test_arrays_with_quotes_and_commas(self):
        """Test arrays containing strings with quotes and commas."""
        toml = '''
        tricky = ["hello, world", 'it\\'s working', "quote: \\"test\\""]
        '''
        result = self.parser.parse(toml)
        expected = ['hello, world', "it's working", 'quote: "test"']
        self.assertEqual(result['tricky'], expected)


class TestSections(unittest.TestCase):
    """Test parsing of sections and nested sections."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_simple_sections(self):
        """Test parsing simple sections."""
        toml = '''
        global_key = "global"
        
        [section1]
        key1 = "value1"
        
        [section2]
        key2 = "value2"
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['global_key'], 'global')
        self.assertEqual(result['section1']['key1'], 'value1')
        self.assertEqual(result['section2']['key2'], 'value2')
    
    def test_nested_sections(self):
        """Test parsing nested sections."""
        toml = '''
        [parent]
        parent_key = "parent_value"
        
        [parent.child]
        child_key = "child_value"
        
        [parent.child.grandchild]
        grandchild_key = "grandchild_value"
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['parent']['parent_key'], 'parent_value')
        self.assertEqual(result['parent']['child']['child_key'], 'child_value')
        self.assertEqual(result['parent']['child']['grandchild']['grandchild_key'], 'grandchild_value')
    
    def test_section_with_special_characters(self):
        """Test sections with valid special characters."""
        toml = '''
        [my-section_1]
        key = "value"
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['my-section_1']['key'], 'value')


class TestComments(unittest.TestCase):
    """Test handling of comments."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_comments(self):
        """Test that comments are properly ignored."""
        toml = '''
        # This is a comment
        key1 = "value1"  # End of line comment would be handled in full TOML
        
        # Another comment
        [section]
        # Comment in section
        key2 = "value2"
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['section']['key2'], 'value2')
    
    def test_empty_lines(self):
        """Test that empty lines are properly ignored."""
        toml = '''
        
        key1 = "value1"
        
        
        [section]
        
        key2 = "value2"
        
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['section']['key2'], 'value2')


class TestErrorHandling(unittest.TestCase):
    """Test error handling and validation."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_empty_section_header(self):
        """Test error on empty section header."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('[]')
        self.assertIn('Empty section header', str(cm.exception))
    
    def test_missing_key(self):
        """Test error on missing key before equals."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('= "value"')
        self.assertIn("Missing key before '='", str(cm.exception))
    
    def test_missing_equals(self):
        """Test error on missing equals sign."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('key "value"')
        self.assertIn('Invalid line format', str(cm.exception))
    
    def test_duplicate_keys(self):
        """Test error on duplicate keys."""
        toml = '''
        key = "value1"
        key = "value2"
        '''
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse(toml)
        self.assertIn('Duplicate key', str(cm.exception))
    
    def test_invalid_key_format(self):
        """Test error on invalid key format."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('key with spaces = "value"')
        self.assertIn('Invalid key format', str(cm.exception))
    
    def test_unterminated_string_in_array(self):
        """Test error on unterminated string in array."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('arr = ["unterminated]')
        self.assertIn('Unterminated string', str(cm.exception))
    
    def test_invalid_section_name(self):
        """Test error on invalid section name."""
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse('[section..subsection]')
        self.assertIn('empty part', str(cm.exception))
    
    def test_line_number_in_errors(self):
        """Test that line numbers are correctly reported in errors."""
        toml = '''
        valid_key = "value"
        
        invalid line without equals
        '''
        with self.assertRaises(TOMLSyntaxError) as cm:
            self.parser.parse(toml)
        self.assertIn('line 4', str(cm.exception))


class TestConvenienceFunction(unittest.TestCase):
    """Test the convenience function."""
    
    def test_parse_toml_string_function(self):
        """Test the standalone parse_toml_string function."""
        toml = '''
        key = "value"
        [section]
        nested_key = 42
        '''
        result = parse_toml_string(toml)
        self.assertEqual(result['key'], 'value')
        self.assertEqual(result['section']['nested_key'], 42)


class TestStringEscaping(unittest.TestCase):
    """Test string escape sequence handling."""
    
    def setUp(self):
        self.parser = TOMLParser()
    
    def test_basic_escapes(self):
        """Test basic escape sequences."""
        toml = r'''
        newline = "line1\nline2"
        tab = "col1\tcol2"
        quote = "He said \"hello\""
        backslash = "path\\to\\file"
        '''
        result = self.parser.parse(toml)
        self.assertEqual(result['newline'], 'line1\nline2')
        self.assertEqual(result['tab'], 'col1\tcol2')
        self.assertEqual(result['quote'], 'He said "hello"')
        self.assertEqual(result['backslash'], 'path\\to\\file')


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)