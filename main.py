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
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.root.columnconfigure(1, weight=75)
        self.root.columnconfigure(2, weight=20)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def init_command_palette(self):
        self.command_palette = tkinter.Frame(self.root, background='red')
        self.new_project_btn = tkinter.Button(self.command_palette, text='New Project')
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project')
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project')
        self.draw_rectangle_btn = tkinter.Button(self.command_palette, text='Draw Rectangle')
        self.draw_polygon_btn = tkinter.Button(self.command_palette, text='Draw Polygon')

        self.command_palette.grid(column=0, row=0, sticky='nsw', rowspan=2)
        self.new_project_btn.grid(column=0, row=0)
        self.load_project_btn.grid(column=0, row=1)
        self.save_project_btn.grid(column=0, row=2)
        self.draw_rectangle_btn.grid(column=0, row=3)
        self.draw_polygon_btn.grid(column=0, row=4)

    def init_drawing_frame(self):
        self.drawing_frame = tkinter.Frame(self.root, background='green')
        self.canvas = tkinter.Canvas(self.drawing_frame)

        self.drawing_frame.grid(column=1, row=0, sticky='nesw', rowspan=2)

    def init_files_frame(self):
        self.files_frame = tkinter.Frame(self.root, background='blue')
        self.files_frame.grid(column=2, row=0, sticky='nesw')

    def init_figures_frame(self):
        self.figures_frame = tkinter.Frame(self.root, background='cyan')
        self.figures_frame.grid(column=2, row=1, sticky='nesw')

    def run(self):
        self.create_gui()
        self.root.mainloop()


if __name__ == '__main__':
    app = AppGui('app')
    app.run()