import copy
import json
import pathlib
import typing
import uuid

from history import History


class Project:
    def __init__(self, path: typing.Union[str, pathlib.Path] = None):
        self.files = dict() if not path else self._load_from_path(path)
        self.history = History(self.files)
        self.selected_file_id = None

    @staticmethod
    def _load_from_path(path: str) -> typing.Dict:
        result = dict()
        with open(path, 'r') as f:
            data = json.loads(f.read())
            if isinstance(data, dict) and 'files' in data:
                result = data['files']

        return result

    def add_file(self, abs_path):
        file_id = str(uuid.uuid4())
        self.files[file_id] = {'abs_path': abs_path, 'figures': []}
        self.history.set_defaults(file_id, self.files[file_id])

    def get_files(self):
        return self.files

    def select_file(self, file_id):
        self.selected_file_id = file_id

    def get_selected_file_id(self):
        return self.selected_file_id

    def add_rectangle(self, points: typing.List[float]):
        self.history.add_snapshot(self.selected_file_id, self.files[self.selected_file_id])
        self.files[self.selected_file_id]['figures'].append({
            'type': 'rect',
            'points': copy.deepcopy(points),
            'category': None
        })
        return len(self.files[self.selected_file_id]['figures']) - 1
