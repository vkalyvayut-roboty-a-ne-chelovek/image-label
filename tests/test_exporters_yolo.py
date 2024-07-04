import glob
import os.path
import pathlib
import tempfile
import unittest

from src.exporters.yolo import YoloExporter
from src.project import Project
from src.common_bus import CommonBus


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

    def test_convert_file_data_into_save_data(self):
        self.y.options['export_rect_vals'] = 1

        raw_data = [('img1', {"abs_path": str(pathlib.Path("./assets/domiki.png").absolute()), "figures": [{"type": "rect", "category": "rect1", "points": [[0, 0], [0.5, 0.5]]}, {"type": "poly", "category": "poly1", "points": [[0.5, 0.5], [0.5, 1], [1.0, 1.0], [1, 0.5]]}]})]
        expected_data = {'img1': {
            'abs_path': raw_data[0][1]['abs_path'],
            'data': [
                ['1', '0.25', '0.25', '0.5', '0.5']
            ]
        }}

        converted_data = self.y.convert_file_data_into_save_data(raw_data)
        assert expected_data == converted_data

        self.y.options['export_rect_vals'] = 2
        expected_data['img1']['data'].append(['0', '0.75', '0.75', '0.5', '0.5'])
        converted_data = self.y.convert_file_data_into_save_data(raw_data)
        assert expected_data == converted_data

    def test_directory_created_mk_dataset_dir_and_save_dataset_data(self):
        dataset_data = {
            'img1': {
                'abs_path': pathlib.Path('./assets/domiki.png').absolute(),
                'data': [
                    ['1', '0.25', '0.25', '0.5', '0.5'],
                    ['0', '0.75', '0.75', '0.5', '0.5']
                ]
            }
        }
        self.y.mk_dataset_dir_and_save_dataset_data('train', dataset_data)
        expected_path = pathlib.Path(self.y.path, 'domik', 'train').absolute()
        expected_categories_file_path = pathlib.Path(expected_path, 'classes.txt')
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

    def test_export(self):
        self.y.options['export_rect_vals'] = 2
        self.y.export()

        expected_path = pathlib.Path(self.y.path, 'domik', 'test').absolute()
        expected_categories_file_path = pathlib.Path(expected_path, 'classes.txt')
        expected_labels_dir_path = pathlib.Path(expected_path, 'labels')
        expected_images_dir_path = pathlib.Path(expected_path, 'images')

        assert os.path.exists(expected_path)
        assert os.path.exists(expected_categories_file_path)
        assert os.path.exists(expected_labels_dir_path)
        assert os.path.exists(expected_images_dir_path)

        expected_label_txt_content = '''1 0.25 0.25 0.5 0.5\n0 0.75 0.75 0.5 0.5'''
        for label_txt in glob.glob(f'{expected_labels_dir_path}/*.txt'):
            with open(label_txt, 'r') as label_txt_handle:
                assert label_txt_handle.read() == expected_label_txt_content



if __name__ == '__main__':
    unittest.main()
