class JSONSyntaxError(Exception):
    def __init__(self, message, line_num=None):
        if line_num is not None:
            super().__init__(f"JSON Syntax Error on line {line_num}: {message}")
        else:
            super().__init__(f"JSON Syntax Error: {message}")


def parse_json_string(json_str):
    # TODO: реалізувати парсер для JSON-файла з коректною обробкою помилок.

    return result
