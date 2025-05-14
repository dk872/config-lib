class TOMLSyntaxError(Exception):
    def __init__(self, message, line_num):
        self.message = f"TOML Syntax Error on line {line_num}: {message}"
        super().__init__(self.message)


def parse_toml_string(toml_str):
    # TODO: реалізувати парсер для TOML-файла з коректною обробкою помилок.

    return result
