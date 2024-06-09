import tkinter
from tkinter import ttk
import unittest

import miros

from main import Gui
from main import Statechart

class TestGUIStructure(unittest.TestCase):
    def setUp(self):
        self.gui = Gui()
        self.gui.create_gui()

    def test_gui_has_main_window(self):
        self.assertIsNotNone(self.gui.root)

    def test_gui_has_command_palette(self):
        self.assertIsNotNone(self.gui.command_palette, 'GUI has no command palette')

    def test_command_palette_has_children(self):
        children = self.gui.command_palette.winfo_children()
        assert len(children) > 0, 'Command palette has no children'

    def test_command_palette_has_new_load_save_rect_poly_buttons(self):
        buttons = ['New Project', 'Load Project', 'Save Project', 'Add File', 'Remove File', 'Draw Rectangle', 'Draw Polygon']
        children_names = [child['text'] for child in self.gui.command_palette.winfo_children()]
        for button_name in buttons:
            assert button_name in children_names, f'Command palette has no "{button_name}" button'

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
