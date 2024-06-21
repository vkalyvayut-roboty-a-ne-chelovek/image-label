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
        return file_id

    def remove_file(self, file_id):
        del self.files[file_id]

    def get_files(self, only_keys: typing.Tuple = None):
        if only_keys:
            return [(k, self.files.get(k)) for k in only_keys]
        return [(k, v) for k, v in self.files.items()]

    def select_file(self, file_id):
        self.selected_file_id = file_id

    def get_selected_file(self):
        if self.selected_file_id:
            return self.selected_file_id, self.files[self.selected_file_id]
        else:
            return None, None

    def delete_figure(self, figure_id):
        self.history.add_snapshot(self.selected_file_id, self.files[self.selected_file_id])
        del self.files[self.selected_file_id]['figures'][figure_id]

    def save_project(self, abs_path: typing.Union[str, pathlib.Path]):
        with open(abs_path, 'w+') as f:
            data = {
                'version': 0,
                'files': self.files
            }
            f.write(json.dumps(data))

        self.history.reset_history()

    def undo_history(self):
        snapshot = self.history.pop_history(self.selected_file_id)
        self.files[self.selected_file_id] = snapshot

    def add_rectangle(self, points: typing.List[float], color: str = None, category: str = '<NOCATEGORY>'):
        self.history.add_snapshot(self.selected_file_id, self.files[self.selected_file_id])
        self.files[self.selected_file_id]['figures'].append({
            'type': 'rect',
            'points': copy.deepcopy(points),
            'category': category,
            'color': color,
        })
        return len(self.files[self.selected_file_id]['figures']) - 1

    def update_figure_category(self, file_id, figure_id, category):
        self.files[file_id]['figures'][figure_id]['category'] = category
