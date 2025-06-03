import os
from .writers.writer_json import serialize_json
from .writers.writer_yaml import serialize_yaml
from .writers.writer_toml import serialize_toml
from .writers.writer_ini import serialize_ini


def save_config_to_file(config: dict, file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".json":
            content = serialize_json(config)
        elif ext in [".yaml", ".yml"]:
            content = "\n".join(serialize_yaml(config))
        elif ext == ".toml":
            content = "\n".join(serialize_toml(config))
        elif ext == ".ini":
            content = "\n".join(serialize_ini(config))
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Failed to serialize config to {ext}: {exc}") from exc

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as exc:
        raise OSError(f"Failed to write to file {file_path}: {exc}") from exc
