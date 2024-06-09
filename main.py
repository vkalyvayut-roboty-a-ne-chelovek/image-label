import tkinter
from miros import ActiveObject

class AppGui(ActiveObject):
    def __init__(self, name: str):
        super().__init__(name=name)

    def create_gui(self):
        self.init_window()
        self.init_command_palette()
        self.init_drawing_frame()
        self.init_files_frame()
        self.init_figures_frame()

    def init_window(self):
        self.root = tkinter.Tk()

    def init_command_palette(self):
        self.command_palette = tkinter.Frame(self.root)
        self.new_project_btn = tkinter.Button(self.command_palette, text='New Project')
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project')
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project')
        self.draw_rectangle_btn = tkinter.Button(self.command_palette, text='Draw Rectangle')
        self.draw_polygon_btn = tkinter.Button(self.command_palette, text='Draw Polygon')

    def init_drawing_frame(self):
        self.drawing_frame = tkinter.Frame(self.root)
        self.canvas = tkinter.Canvas(self.drawing_frame)

    def init_files_frame(self):
        self.files_frame = tkinter.Frame(self.root)

    def init_figures_frame(self):
        self.figures_frame = tkinter.Frame(self.root)

    def run(self):
        self.create_gui()
        self.root.mainloop()


if __name__ == '__main__':
    app = AppGui('app')
    # app.run()