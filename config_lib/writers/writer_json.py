def serialize_json(config, indent=2):
    if not isinstance(config, dict):
        raise TypeError("JSON config must be a dictionary")

    def to_json(obj, level=0):
        spaces = " " * (indent * level)
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                items.append(f'{spaces}  "{k}": {to_json(v, level + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{spaces}}}"
        if isinstance(obj, list):
            items = [f"{spaces}  {to_json(v, level + 1)}" for v in obj]
            return "[\n" + ",\n".join(items) + f"\n{spaces}]"
        if isinstance(obj, str):
            return f'"{obj}"'
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if obj is None:
            return "null"
        return str(obj)

    return to_json(config)
