import json
import typing


def read_project_file_from_path(path_to_project_file: str) -> typing.List:
    result = None
    with open(path_to_project_file, 'r') as f:
        result = json.loads(f.read())
    return result
