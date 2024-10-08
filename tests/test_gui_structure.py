import tkinter
from tkinter import ttk
import unittest

from image_label.gui import Gui
from image_label.common_bus import CommonBus


class TestGUIStructure(unittest.TestCase):
    def setUp(self):
        self.bus = CommonBus()
        self.gui = Gui(bus=self.bus)

    def test_gui_has_main_window(self):
        self.assertIsNotNone(self.gui.root)

    def test_gui_has_drawing_frame(self):
        self.assertIsNotNone(self.gui.drawing_frame)

    def test_drawing_frame_has_canvas(self):
        drawing_frame_has_canvas_child = False
        for child in self.gui.drawing_frame.winfo_children():
            if isinstance(child, tkinter.Canvas):
                drawing_frame_has_canvas_child = True
                break

        assert drawing_frame_has_canvas_child, 'Drawing frame has no canvas child'

    def test_gui_has_files_frame(self):
        self.assertIsNotNone(self.gui.files_frame, 'GUI has no Files frame')

    def test_files_frame_has_treeview(self):
        files_frame_has_treeview = False
        for child in self.gui.files_frame.winfo_children():
            if isinstance(child, ttk.Treeview):
                files_frame_has_treeview = True

        assert files_frame_has_treeview, 'Files frame has no Treeview'

    def test_files_treeview_contains_items_after_refresh(self):
        files = {
            '1': {'abs_path': '1', "filename": '1', "figures": []},
            '2': {'abs_path': '2', "filename": '2', "figures": []},
            '3': {'abs_path': '3', "filename": '3', "figures": []}
        }

        for file_id, file_data in files.items():
            self.gui.add_file(file_id, file_data)

        assert 3 == len(self.gui.files_frame_treeview.get_children())

        self.gui.clear_files()

        assert 0 == len(self.gui.files_frame_treeview.get_children())

        files = {
            '1': {'abs_path': '1', "filename": '1', "figures": []},
            '3': {'abs_path': '3', "filename": '3', "figures": []}
        }

        for file_id, file_data in files.items():
            self.gui.add_file(file_id, file_data)

        assert 2 == len(self.gui.files_frame_treeview.get_children())

    def test_gui_has_figures_frame(self):
        self.assertIsNotNone(self.gui.figures_frame, 'GUI has not Figures frame')

    def test_figures_frame_has_treeview(self):
        figures_frame_has_treeview = False
        for child in self.gui.figures_frame.winfo_children():
            if isinstance(child, ttk.Treeview):
                figures_frame_has_treeview = True

        assert figures_frame_has_treeview, 'Figures frame has no Treeview'


if __name__ == '__main__':
    unittest.main()
