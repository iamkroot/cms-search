import json
import toml
from pathlib import Path


def read_toml(path):
    try:
        with open(path) as f:
            return toml.load(f)
    except FileNotFoundError:
        print(f"Missing toml file at {path}.")
    except toml.TomlDecodeError as e:
        print(f"Invalid TOML in file: {path}")
        print(f"Error (probably) in line {e.lineno}.")
    exit(1)


def pprint_json(data):
    print(json.dumps(data, indent=4))


def get_real_path(file_path: Path) -> Path:
    return Path(config['PATHS']['dl_root']) / file_path


config = read_toml('config.toml')
