import tkinter
import unittest
from main import AppGui

class TestGUIStructure(unittest.TestCase):
    def setUp(self):
        self.gui = AppGui('app')
        self.gui.create_gui()

    def test_gui_has_main_window(self):
        self.assertIsNotNone(self.gui.root)

    def test_gui_has_command_palette(self):
        self.assertIsNotNone(self.gui.command_palette, 'GUI has no command palette')

    def test_command_palette_has_children(self):
        children = self.gui.command_palette.winfo_children()
        assert len(children) > 0, 'Command palette has no children'

    def test_command_palette_has_new_load_save_rect_poly_buttons(self):
        buttons = ['New Project', 'Load Project', 'Save Project', 'Draw Rectangle', 'Draw Polygon']
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

        assert drawing_frame_has_canvas_child == True, 'Drawing frame has no canvas child'

    def test_gui_has_files_frame(self):
        self.assertIsNotNone(self.gui.files_frame, 'GUI has no Files frame')

    def test_gui_has_figures_frame(self):
        self.assertIsNotNone(self.gui.figures_frame, 'GUI has not Figures frame')



if __name__ == '__main__':
    unittest.main()
