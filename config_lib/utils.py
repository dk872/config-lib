def handle_missing_key(rules, full_path):
    if "default" in rules:
        return rules["default"]
    elif rules.get("type") == dict:
        return fill_defaults({}, rules.get("schema", {}), path=full_path)
    return None


def handle_existing_key(value, rules, full_path):
    has_default = "default" in rules
    expected_type = rules.get("type")

    if (value is None or value == "") and has_default:
        return rules["default"]
    elif expected_type == dict and isinstance(value, dict):
        return fill_defaults(value, rules.get("schema", {}), path=full_path)
    return value


def fill_defaults(config, schema, path=""):
    if not isinstance(schema, dict):
        return config

    filled = config.copy()

    for key, rules in schema.items():
        full_path = f"{path}.{key}" if path else key

        if key not in filled:
            value = handle_missing_key(rules, full_path)
            if value is not None:
                filled[key] = value
        else:
            filled[key] = handle_existing_key(filled[key], rules, full_path)

    return filled


def mask_secrets(config: dict, secret_fields: list[str], mask: str = "***") -> dict:
    def _mask(value, path=""):
        if isinstance(value, dict):
            return {
                k: _mask(v, path=f"{path}.{k}" if path else k)
                for k, v in value.items()
            }
        return mask if path in secret_fields else value

    return _mask(config)
