import re
from typing import Dict, Any, List, Union

class TOMLSyntaxError(Exception):
    """Custom exception for TOML parsing errors."""
    
    def __init__(self, message: str, line_num: int):
        self.line_num = line_num
        self.message = f"TOML Syntax Error on line {line_num}: {message}"
        super().__init__(self.message)

class TOMLParser:
    """A simple TOML parser with improved structure and error handling."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.current_section: Dict[str, Any] = self.data
        self.line_number: int = 0
    
    def parse(self, toml_str: str) -> Dict[str, Any]:
        """Parse a TOML string and return the resulting dictionary."""
        self.data = {}
        self.current_section = self.data
        
        lines = toml_str.splitlines()
        for line_num, line in enumerate(lines, start=1):
            self.line_number = line_num
            self._parse_line(line.strip())
        
        return self.data
    
    def _parse_line(self, line: str) -> None:
        """Parse a single line of TOML."""
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return
        
        # Handle section headers
        if line.startswith('[') and line.endswith(']'):
            self._parse_section_header(line)
        # Handle key-value pairs
        elif '=' in line:
            self._parse_key_value(line)
        else:
            raise TOMLSyntaxError("Invalid line format - expected section header or key=value pair", self.line_number)
    
    def _parse_section_header(self, line: str) -> None:
        """Parse a section header like [section.subsection]."""
        section_name = line[1:-1].strip()
        
        if not section_name:
            raise TOMLSyntaxError("Empty section header", self.line_number)
        
        # Handle nested sections
        parts = [part.strip() for part in section_name.split('.')]
        
        # Validate section parts
        for part in parts:
            if not part:
                raise TOMLSyntaxError("Invalid section name - empty part after splitting by '.'", self.line_number)
            if not self._is_valid_key(part):
                raise TOMLSyntaxError(f"Invalid section name part: '{part}'", self.line_number)
        
        # Navigate/create nested structure
        self.current_section = self.data
        for part in parts:
            if part not in self.current_section:
                self.current_section[part] = {}
            elif not isinstance(self.current_section[part], dict):
                raise TOMLSyntaxError(f"Cannot create section '{part}' - key already exists with non-table value", self.line_number)
            self.current_section = self.current_section[part]
    
    def _parse_key_value(self, line: str) -> None:
        """Parse a key-value pair."""
        if line.count('=') == 0:
            raise TOMLSyntaxError("Missing '=' in key-value pair", self.line_number)
        
        # Split only on the first '=' to handle values containing '='
        key, raw_value = line.split('=', 1)
        key = key.strip()
        raw_value = raw_value.strip()
        
        # Handle end-of-line comments (basic implementation)
        # This is a simplified approach - full TOML would need to respect quotes
        raw_value = self._strip_end_of_line_comment(raw_value)
        
        if not key:
            raise TOMLSyntaxError("Missing key before '='", self.line_number)
        
        if not self._is_valid_key(key):
            raise TOMLSyntaxError(f"Invalid key format: '{key}'", self.line_number)
        
        if key in self.current_section:
            raise TOMLSyntaxError(f"Duplicate key: '{key}'", self.line_number)
        
        try:
            value = self._parse_value(raw_value)
            self.current_section[key] = value
        except Exception as e:
            if isinstance(e, TOMLSyntaxError):
                raise
            raise TOMLSyntaxError(f"Error parsing value for key '{key}': {str(e)}", self.line_number)
    
    def _is_valid_key(self, key: str) -> bool:
        """Check if a key is valid (basic validation)."""
        if not key:
            return False
        # Allow alphanumeric, underscore, hyphen
        return re.match(r'^[a-zA-Z0-9_-]+$', key) is not None
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a value string into appropriate Python type."""
        value_str = value_str.strip()
        
        if not value_str:
            raise TOMLSyntaxError("Empty value", self.line_number)
        
        # Boolean values
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
        
        # String values
        if self._is_string(value_str):
            return self._parse_string(value_str)
        
        # Array values
        if value_str.startswith('[') and value_str.endswith(']'):
            return self._parse_array(value_str)
        
        # Numeric values
        numeric_value = self._try_parse_numeric(value_str)
        if numeric_value is not None:
            return numeric_value
        
        # Date/datetime (basic detection, returned as string)
        if self._looks_like_datetime(value_str):
            return value_str
        
        # Default to string for unrecognized formats
        return value_str
    
    def _is_string(self, value_str: str) -> bool:
        """Check if value appears to be a quoted string."""
        return (value_str.startswith('"') and value_str.endswith('"')) or \
               (value_str.startswith("'") and value_str.endswith("'"))
    
    def _parse_string(self, value_str: str) -> str:
        """Parse a quoted string value."""
        if len(value_str) < 2:
            raise TOMLSyntaxError("Invalid string - too short", self.line_number)
        
        quote_char = value_str[0]
        if value_str[-1] != quote_char:
            raise TOMLSyntaxError(f"Mismatched quotes in string", self.line_number)
        
        # Basic string parsing with proper escape sequence handling
        inner = value_str[1:-1]
        result = ""
        i = 0
        while i < len(inner):
            if inner[i] == '\\' and i + 1 < len(inner):
                next_char = inner[i + 1]
                if next_char == 'n':
                    result += '\n'
                elif next_char == 't':
                    result += '\t'
                elif next_char == '"':
                    result += '"'
                elif next_char == "'":
                    result += "'"
                elif next_char == '\\':
                    result += '\\'
                else:
                    # Unknown escape sequence, keep as is
                    result += '\\' + next_char
                i += 2  # Skip both the backslash and the next character
            else:
                result += inner[i]
                i += 1
        return result
    
    def _parse_array(self, value_str: str) -> List[Any]:
        """Parse an array value."""
        inner = value_str[1:-1].strip()
        
        if not inner:
            return []
        
        items = self._split_array_items(inner)
        return [self._parse_value(item) for item in items]
    
    def _split_array_items(self, array_str: str) -> List[str]:
        """Split array items, respecting quoted strings."""
        result = []
        current_item = ''
        in_quotes = False
        quote_char = None
        bracket_depth = 0
        
        i = 0
        while i < len(array_str):
            char = array_str[i]
            
            # Handle escape sequences
            if char == '\\' and i + 1 < len(array_str) and in_quotes:
                current_item += char + array_str[i + 1]
                i += 2
                continue
            
            # Handle quotes
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            
            # Handle nested brackets
            if not in_quotes:
                if char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
            
            # Handle comma separation
            if char == ',' and not in_quotes and bracket_depth == 0:
                result.append(current_item.strip())
                current_item = ''
            else:
                current_item += char
            
            i += 1
        
        if current_item.strip():
            result.append(current_item.strip())
        
        if in_quotes:
            raise TOMLSyntaxError("Unterminated string in array", self.line_number)
        
        return result
    
    def _try_parse_numeric(self, value_str: str) -> Union[int, float, None]:
        """Try to parse a numeric value."""
        # Integer
        if re.match(r'^[+-]?\d+$', value_str):
            return int(value_str)
        
        # Float
        if re.match(r'^[+-]?\d*\.\d+([eE][+-]?\d+)?$', value_str):
            return float(value_str)
        
        return None
    
    def _strip_end_of_line_comment(self, value_str: str) -> str:
        """Strip end-of-line comments while respecting quoted strings."""
        result = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(value_str):
            char = value_str[i]
            
            # Handle escape sequences in quotes
            if char == '\\' and i + 1 < len(value_str) and in_quotes:
                result += char + value_str[i + 1]
                i += 2
                continue
            
            # Handle quotes
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            
            # Handle comments outside of quotes
            if char == '#' and not in_quotes:
                break  # Stop processing at comment
            
            result += char
            i += 1
        
        return result.strip()

    def _looks_like_datetime(self, value_str: str) -> bool:
        """Basic check if value looks like a datetime."""
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}([Tt\s]\d{2}:\d{2}:\d{2})?', value_str))

# Convenience function
def parse_toml_string(toml_str: str) -> Dict[str, Any]:
    """Parse a TOML string and return the resulting dictionary."""
    parser = TOMLParser()
    return parser.parse(toml_str)
