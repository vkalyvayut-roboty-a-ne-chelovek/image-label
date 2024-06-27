import datetime
import os.path
import pathlib
import tempfile
import unittest

from exporters.yolo import YoloExporter
from project import Project
from common_bus import CommonBus


class TestableStatechart:
    def __init__(self, bus):
        self.bus = bus
        self.project = Project(pathlib.Path('./assets/domik.boobalp'))
        self.bus.register_item('statechart', self)


class TestExportersYolo(unittest.TestCase):
    def setUp(self):
        self.bus = CommonBus()
        self.statechart = TestableStatechart(self.bus)
        self.y = YoloExporter(self.bus)
        self.y.path = tempfile.mkdtemp(prefix='yolo_')
        self.y.options = {
            'test_percent': 10,
            'validation_percent': 10,
            'export_rect_vals': 1
        }

    def test_mk_dest_dir(self):
        expected_dir = pathlib.Path(self.y.path, 'domik').absolute()
        self.y.mk_dest_dir()
        assert os.path.exists(expected_dir)

    def test_get_datasets_len(self):
        datasets = self.y.get_datasets()
        assert len(datasets) == 3

    def test_get_datasets_lengths(self):
        expected_lengths = {
            'train': 8,
            'test': 1,
            'val': 1
        }
        assert expected_lengths == self.y.get_datasets_lengths()


    def test_extract_project_filenames(self):
        expected_filenames = [
            'img1',
            'img2',
            'img3',
            'img4',
            'img5',
            'img6',
            'img7',
            'img8',
            'img9',
            'img10'
        ]

        assert expected_filenames == self.y.extract_project_filenames()

    def test_get_filenames_for_dataset(self):
        expected_lengths = {
            'train': 8,
            'test': 1,
            'val': 1
        }

        filenames_for_dataset = self.y.get_filenames_for_dataset(expected_lengths)

        for dataset_name, expected_len in expected_lengths.items():
            assert expected_len == len(filenames_for_dataset[dataset_name])

    def test_get_datasets_each_dataset_len(self):
        datasets = self.y.get_datasets()
        assert len(datasets['train']) == 8
        assert len(datasets['test']) == 1
        assert len(datasets['val']) == 1

    def test_extract_categories(self):
        expected_categories = {
            'poly1': 0,
            'rect1': 1,
        }

        assert expected_categories == self.y.extract_categories()

    def test_directory_created_mk_dataset_dir_and_save_dataset_data(self):
        dataset_data = {
            'img1': {
                'abs_path': pathlib.Path('./assets/domiki.png').absolute(),
                'data': [
                    ['0', '1', '2', '3', '4'],
                    ['0', '5', '6', '7', '8'],
                ]
            }
        }
        self.y.mk_dataset_dir_and_save_dataset_data('train', dataset_data)
        expected_path = pathlib.Path(self.y.path, 'domik', 'train').absolute()
        expected_categories_file_path = pathlib.Path(expected_path, 'categories.txt')
        expected_labels_dir_path = pathlib.Path(expected_path, 'labels')
        expected_labels_img1_path = pathlib.Path(expected_labels_dir_path, 'img1.txt')
        expected_images_dir_path = pathlib.Path(expected_path, 'images')
        expected_images_img1_path = pathlib.Path(expected_images_dir_path, 'img1.png')

        assert os.path.exists(expected_path)
        assert os.path.exists(expected_categories_file_path)
        assert os.path.exists(expected_labels_dir_path)
        assert os.path.exists(expected_labels_img1_path)
        assert os.path.exists(expected_images_dir_path)
        assert os.path.exists(expected_images_img1_path)


    # def test_extract_categories(self):
    #     expected_categories = {
    #         '65431': 0,
    #         '1234': 1,
    #         '<NOCATEGORY>': 2
    #     }
    #
    #     assert self.y.extract_categories() == expected_categories
    #
    # def test_extract_keys(self):
    #     expected_keys = [
    #         '58da0c08-2529-43bc-b784-389c1fe6997b',
    #         '3d93c653-cd1b-438d-91c3-ae370c678b17',
    #         '767b79a3-655d-406e-af69-39ee0b085bc2'
    #     ]
    #
    #     assert self.y.extract_keys() == expected_keys
    #
    # def test_generate_train_test_val_keys(self):
    #     print(self.y.generate_train_test_val_keys())



if __name__ == '__main__':
    unittest.main()
