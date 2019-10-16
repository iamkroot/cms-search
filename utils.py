import json
import toml
from pathlib import Path


def read_toml(path):
    """
    Parse a TOML file for its contents.

    Args:
        path(str or Path): Location of the TOML file

    Returns:
        dict: Parsed contents of the file
    """
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
    """
    Pretty format and print a json object

    Args:
        data(dict): The data to be printed
    """
    print(json.dumps(data, indent=4))


def get_real_path(file_path: Path) -> Path:
    """
    Prepend the root folder of the download directory to the given path

    Args:
        file_path(Path): The relative path of the file

    Returns:
        Path: The absolute path where the file should be saved
    """
    return Path(config["PATHS"]["dl_root"]) / file_path


def clean_line(line: str):
    """
    Sanitize the input line by removing extra whitespace characters.

    Args:
        line(str): The sentence to be cleaned

    Return:
        str: Sanitized sentence
    """
    return line.replace("\n", "").replace("\t", "").strip()


config = read_toml("config.toml")
