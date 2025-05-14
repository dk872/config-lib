class INISyntaxError(Exception):
    def __init__(self, message, line_num=None):
        if line_num is not None:
            super().__init__(f"INI Syntax Error at line {line_num}: {message}")
        else:
            super().__init__(f"INI Syntax Error: {message}")


def parse_ini_string(ini_str):
    # TODO: реалізувати парсер для INI-файла з коректною обробкою помилок.

    return result
