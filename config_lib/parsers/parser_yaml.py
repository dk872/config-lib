class YAMLSyntaxError(Exception):
    def __init__(self, message, line_num):
        super().__init__(f"YAML Syntax Error on line {line_num}: {message}")
        self.line_number = line_num


def parse_yaml_string(yaml_str):
    # TODO: реалізувати парсер для YAML-файла з коректною обробкою помилок.

    return result

