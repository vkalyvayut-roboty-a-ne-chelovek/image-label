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


if __name__ == '__main__':
    unittest.main()
