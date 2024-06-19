import json
import pathlib
import tempfile
import unittest

from project import Project


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

        assert p.history.has_history('58da0c08-2529-43bc-b784-389c1fe6997b')

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


if __name__ == '__main__':
    unittest.main()
