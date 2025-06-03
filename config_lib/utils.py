def fill_defaults(config, schema, path=""):
    if not isinstance(schema, dict):
        return config

    filled = config.copy()

    for key, rules in schema.items():
        full_path = f"{path}.{key}" if path else key
        expected_type = rules.get("type")
        has_default = "default" in rules
        default_value = rules.get("default")

        if key not in filled:
            if has_default:
                filled[key] = default_value
            elif expected_type == dict:
                filled[key] = fill_defaults({}, rules.get("schema", {}), path=full_path)
        else:
            current_value = filled[key]

            if (current_value is None or current_value == "") and has_default:
                filled[key] = default_value
            elif expected_type == dict and isinstance(current_value, dict):
                filled[key] = fill_defaults(current_value, rules.get("schema", {}), path=full_path)

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
