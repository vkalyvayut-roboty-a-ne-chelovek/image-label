import pathlib
import tempfile
import unittest

from exporters.yolo import YoloExporter
from project import Project
from common_bus import CommonBus


class TestableStatechart:
    def __init__(self, bus):
        self.bus = bus
        self.project = Project(pathlib.Path('.', 'assets', 'domik.boobalp'))
        self.bus.register_item('statechart', self)


class TestExportersYolo(unittest.TestCase):
    def setUp(self):
        self.bus = CommonBus()
        self.statechart = TestableStatechart(self.bus)
        self.y = YoloExporter(self.bus)
        self.y.options = {
            'validation_percent': 10,
            'test_percent': 10,
            'export_rect_vals': 2
        }

    def test_dest_dir_name(self):
        self.y.path = tempfile.gettempdir()

        assert self.y.get_dest_dir_name() == pathlib.Path(self.y.path, 'domik.boobalp')

    def test_extract_categories(self):
        expected_categories = {
            '65431': 0,
            '1234': 1,
            '<NOCATEGORY>': 2
        }

        assert self.y.extract_categories() == expected_categories

    def test_extract_keys(self):
        expected_keys = [
            '58da0c08-2529-43bc-b784-389c1fe6997b',
            '3d93c653-cd1b-438d-91c3-ae370c678b17',
            '767b79a3-655d-406e-af69-39ee0b085bc2'
        ]

        assert self.y.extract_keys() == expected_keys

    def test_generate_train_test_val_keys(self):
        print(self.y.generate_train_test_val_keys())



if __name__ == '__main__':
    unittest.main()
