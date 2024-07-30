import copy
import json
import os.path
import pathlib
import typing
import uuid

from image_label.history import History


class Project:
    def __init__(self, path: typing.Union[str, pathlib.Path] = None):
        self.version = 1
        self.path = path
        self.files = {}
        self.selected_file_id = None
        self.quick_categories = None

        if path is not None:
            self._load_from_path(path)

        self.history = History(self.files)

    def _load_from_path(self, path: str) -> typing.Dict:
        result = {}
        with open(path, 'r') as handle:
            data = json.loads(handle.read())
            if isinstance(data, dict):
                assert data['version'] == 1, 'incompatible version'
                if 'files' in data:
                    self.files = data['files']
                if 'quick_categories' in data:
                    self.quick_categories = data['quick_categories']

        return result

    def add_file(self, abs_path):
        file_id = str(uuid.uuid4())
        self.files[file_id] = {
            'abs_path': abs_path,
            'figures': [],
            "transformations": []}
        self.history.set_defaults(file_id, self.files[file_id])
        return file_id

    def remove_file(self, file_id):
        del self.files[file_id]

    def get_files(self, only_keys: typing.Tuple = None):
        if len(self.files) == 0:
            return []
        if only_keys is not None:
            return [(k, self.files.get(k)) for k in only_keys]
        return [(k, v) for k, v in self.files.items()]

    def select_file(self, file_id):
        self.selected_file_id = file_id

    def get_selected_file(self):
        if self.selected_file_id and self.selected_file_id in self.files:
            return self.selected_file_id, self.files[self.selected_file_id]
        return None, None

    def delete_figure(self, figure_id):
        self.history.add_snapshot(self.selected_file_id, self.files[self.selected_file_id])
        del self.files[self.selected_file_id]['figures'][figure_id]

    def save_project(self, abs_path: typing.Union[str, pathlib.Path], temp: bool = False):
        with open(abs_path, 'w+') as handle:
            data = {
                'version': self.version,
                'files': self.files,
                'quick_categories': self.quick_categories
            }
            handle.write(json.dumps(data))

        self.history.reset_history()
        if not temp:
            self.path = abs_path

    def undo_history(self):
        snapshot = self.history.pop_history(self.selected_file_id)
        self.files[self.selected_file_id] = snapshot

    def _add_figure(self, type_: str, points: typing.List[float], color: str = None, category: str = '<NOCATEGORY>'):
        self.history.add_snapshot(self.selected_file_id, self.files[self.selected_file_id])
        self.files[self.selected_file_id]['figures'].append({
            'type': type_,
            'points': copy.deepcopy(points),
            'category': category,
            'color': color,
        })
        return len(self.files[self.selected_file_id]['figures']) - 1

    def add_rectangle(self, points: typing.List[float], color: str = None, category: str = '<NOCATEGORY>'):
        return self._add_figure(type_='rect', points=points, color=color, category=category)

    def add_polygon(self, points: typing.List[float], color: str = None, category: str = '<NOCATEGORY>'):
        return self._add_figure(type_='poly', points=points, color=color, category=category)

    def update_figure_category(self, file_id, figure_id, category):
        self.files[file_id]['figures'][figure_id]['category'] = category

    def update_figure_point_position(self, file_id, figure_id, point_id, new_coords):
        self.history.add_snapshot(file_id, self.files[file_id])
        self.files[file_id]['figures'][figure_id]['points'][point_id] = new_coords

    def update_figure_remove_point(self, file_id, figure_id, point_id):
        self.history.add_snapshot(file_id, self.files[file_id])

        if self.files[file_id]['figures'][figure_id]['type'] == 'rect':
            del self.files[file_id]['figures'][figure_id]
        else:
            if len(self.files[file_id]['figures'][figure_id]['points']) <= 3:
                del self.files[file_id]['figures'][figure_id]
            else:
                del self.files[file_id]['figures'][figure_id]['points'][point_id]

    def update_figure_insert_point(self, file_id, figure_id, point_id, coords):
        self.history.add_snapshot(file_id, self.files[file_id])
        self.files[file_id]['figures'][figure_id]['points'].insert(point_id, coords)

    def get_all_categories(self):
        all_categories = []
        for _, file_data in self.get_files():
            for figure in file_data['figures']:
                all_categories.append(figure['category'])
        result = list(set(all_categories))

        return result

    def temp_save(self):
        if self.path:
            temp_save_path = pathlib.Path(f'{self.path}.tmp').absolute()
            self.save_project(temp_save_path, temp=True)

    def get_project_name(self):
        if self.path:
            return os.path.basename(self.path)

    def rotate_cw(self, file_id):
        self.history.add_snapshot(file_id, self.files[file_id])
        if 'transformations' not in self.files[file_id]:
            self.files[file_id]['transformations'] = []
        self.files[file_id]['transformations'].append('rotate_cw')

    def rotate_ccw(self, file_id):
        self.history.add_snapshot(file_id, self.files[file_id])
        if 'transformations' not in self.files[file_id]:
            self.files[file_id]['transformations'] = []
        self.files[file_id]['transformations'].append('rotate_ccw')

    def set_quick_categories(self, categories: typing.List[str]) -> None:
        self.quick_categories = categories

    def get_quick_categories(self):
        return self.quick_categories
