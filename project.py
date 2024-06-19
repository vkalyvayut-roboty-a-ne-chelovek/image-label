import json
import pathlib
import typing
from history import History


class Project:
    def __init__(self, path: typing.Union[str, pathlib.Path] = None):
        self.files = dict() if not path else self._load_from_path(path)
        self.history = History(self.files)

    @staticmethod
    def _load_from_path(path: str) -> typing.Dict:
        result = dict()
        with open(path, 'r') as f:
            data = json.loads(f.read())
            if isinstance(data, dict) and 'files' in data:
                result = data['files']

        return result

