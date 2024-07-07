import json
import pathlib
import tempfile
import unittest

from src.project import Project


class TestProject(unittest.TestCase):
    def test_create_empty_project(self):
        p = Project()

        assert isinstance(p, Project)

    def test_after_create_empty_project_object_has_files_dictionary(self):
        p = Project()

        assert isinstance(p.files, dict)

    def test_load_project(self):
        path = pathlib.Path('.', 'assets', 'empty.boobalp')
        p = Project(path)

        assert isinstance(p, Project)

    def test_after_load_empty_project_object_has_files_dictionary_and_contains_some_data(self):
        path = pathlib.Path('.', 'assets', 'empty.boobalp')

        p = Project(path)

        assert p.files == dict()

    def test_after_load_not_empty_project_object_has_files_dictionary_and_contains_some_data(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)

        assert p.files != dict()

        with open(path, 'r') as f:
            assert p.files == json.loads(f.read())['files']

    def test_after_load_not_empty_project_object_has_not_empty_history(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)

        assert p.history.has_history('img1')

    def test_after_adding_file_in_also_add_to_history(self):
        abs_path = tempfile.mktemp()
        p = Project()
        p.add_file(abs_path)

        assert p.history.has_history(list(p.files.keys())[0])

    def test_get_files_after_creating_not_empty_project(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)

        assert len(p.get_files()) > 0

    def test_select_file(self):
        abs_path = tempfile.mktemp()
        p = Project()
        p.add_file(abs_path)

        p.select_file(list(p.files.keys())[0])
        selected_file_id, selected_file_data = p.get_selected_file()
        assert selected_file_id == list(p.files.keys())[0]

    def test_delete_figure(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)
        p.select_file('img1')

        _, selected_file_data = p.get_selected_file()
        prev_number_of_figures = len(selected_file_data['figures'])

        p.delete_figure(1)
        _, selected_file_data = p.get_selected_file()

        assert len(selected_file_data['figures']) != prev_number_of_figures

    def test_save_object(self):
        file_path = tempfile.mktemp()
        p = Project()
        file_id = p.add_file(file_path)
        assert p.history.has_history(file_id)

        project_path = tempfile.mktemp()
        p.save_project(project_path)

        assert pathlib.Path(project_path).exists()

    def test_history_sets_to_1_after_saveing(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)
        p.select_file('img1')

        selected_file_id, selected_file_data = p.get_selected_file()

        for figure_id, _ in enumerate(selected_file_data['figures']):
            p.delete_figure(figure_id)

        assert p.history.get_history_len(selected_file_id) != 0
        assert p.history.get_history_len(selected_file_id) == 2

        project_path = tempfile.mktemp()
        p.save_project(project_path)

        assert p.history.get_history_len(selected_file_id) == 1

    def test_remove_file_from_project(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)
        number_of_files_before = len(p.get_files())
        expected_number_of_files_after = number_of_files_before - 1
        p.remove_file('img1')

        assert len(p.get_files()) == expected_number_of_files_after

    def test_get_files(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)
        keys = ('img2',)

        assert len(p.get_files()) != len(p.get_files(keys))
        assert len(p.get_files(keys)) == 1

    def test_update_figure_category(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')

        p = Project(path)
        file_id = 'img2'
        figure_id = 0

        file_data = p.get_files((file_id,))
        p.update_figure_category(file_id, figure_id, 'test')

        assert file_data[0][1]['figures'][figure_id]['category'] == 'test'

    def test_rotate_cw(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')
        p = Project(path)
        file_id = 'img2'

        assert p.history.get_history_len(file_id) == 1

        p.rotate_cw(file_id)

        assert p.history.get_history_len(file_id) == 2

        assert p.files[file_id]['transformations']
        assert len(p.files[file_id]['transformations']) == 1
        assert p.files[file_id]['transformations'] == ['rotate_cw']

    def test_rotate_ccw(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')
        p = Project(path)
        file_id = 'img2'

        assert p.history.get_history_len(file_id) == 1

        p.rotate_ccw(file_id)

        assert p.history.get_history_len(file_id) == 2

        assert p.files[file_id]['transformations']
        assert len(p.files[file_id]['transformations']) == 1
        assert p.files[file_id]['transformations'] == ['rotate_ccw']

    def test_if_get_files_only_files_is_not_none_only_then_return_some_files(self):
        path = pathlib.Path('.', 'assets', 'domik.boobalp')
        p = Project(path)

        assert len(p.get_files()) == len(p.files)
        assert len(p.get_files(only_keys=None)) == len(p.files)
        assert len(p.get_files(only_keys=[])) == 0
        assert len(p.get_files(only_keys=['img2'])) == 1

    def test_project_set_project_quick_categories(self):
        p = Project()

        categories = ['a', 'b', 'c']
        p.set_quick_categories(categories)

        assert p.get_quick_categories() == categories


if __name__ == '__main__':
    unittest.main()
