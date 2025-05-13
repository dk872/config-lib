class ConfigValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate(self, config):
        self._validate_dict(config, self.schema)
        return True

    def _validate_dict(self, config, schema, path=""):
        # TODO: Перевірити всі ключі за схемою.
        pass

    def _validate_list(self, value, item_schema, path):
        # TODO: Перевірити, що значення є списком, і перевірити кожен елемент.
        pass

    @staticmethod
    def _validate_date(value, path):
        # TODO: Перевірити, що значення дати — рядок у форматі ISO 8601.
        pass

    @staticmethod
    def _validate_type(expected_type, actual_value, path):
        # TODO: Перевірити, що значення має очікуваний тип (з урахуванням типу bool для int).
        pass

    @staticmethod
    def _format_path(path, key):
        # TODO: Сформувати повний шлях до ключа у вкладених структурах.
        pass
