import json
import typing
import tkinter
from tkinter import filedialog
from tkinter import ttk
from miros import ActiveObject
from miros import Event
from miros import return_status
from miros import signals
from miros import spy_on

class AppGui(ActiveObject):
    def __init__(self, name: str, debug: bool = False):
        super().__init__(name=name)
        self.debug = debug
        self._app_data = None

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

        self.new_project_btn = tkinter.Button(self.command_palette, text='New Project',
                                              command=lambda: self.post_fifo(Event(signal=signals.NEW_PROJECT)))
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project',
                                              command=lambda: self.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=self.ask_for_load_project_path())))
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project')

        self.add_file_btn = tkinter.Button(self.command_palette, text='Add File')
        self.remove_file_btn = tkinter.Button(self.command_palette, text='Remove File')

        self.draw_rectangle_btn = tkinter.Button(self.command_palette, text='Draw Rectangle')
        self.draw_polygon_btn = tkinter.Button(self.command_palette, text='Draw Polygon')

        self.command_palette.grid(column=0, row=0, sticky='nsw', rowspan=2)
        self.new_project_btn.grid(column=0, row=0)
        self.load_project_btn.grid(column=0, row=1)
        self.save_project_btn.grid(column=0, row=2)

        self.add_file_btn.grid(column=0, row=3)
        self.remove_file_btn.grid(column=0, row=4)

        self.draw_rectangle_btn.grid(column=0, row=5)
        self.draw_polygon_btn.grid(column=0, row=6)

    def init_drawing_frame(self):
        self.drawing_frame = tkinter.Frame(self.root, background='green')
        self.canvas = tkinter.Canvas(self.drawing_frame)

        self.drawing_frame.grid(column=1, row=0, sticky='nesw', rowspan=2)

    def init_files_frame(self):
        self.files_frame = tkinter.Frame(self.root, background='blue')
        self.files_treeview = ttk.Treeview(self.files_frame)

        self.files_frame.grid(column=2, row=0, sticky='nesw')
        self.files_frame.columnconfigure(0, weight=1)
        self.files_frame.rowconfigure(0, weight=1)
        self.files_treeview.grid(column=0, row=0, sticky='nesw')

    def init_figures_frame(self):
        self.figures_frame = tkinter.Frame(self.root, background='cyan')
        self.figures_treeview = ttk.Treeview(self.figures_frame)

        self.figures_frame.grid(column=2, row=1, sticky='nesw')
        self.figures_frame.columnconfigure(0, weight=1)
        self.figures_frame.rowconfigure(0, weight=1)
        self.figures_treeview.grid(column=0, row=0, sticky='nesw')

    def run(self):
        self.create_gui()

        self.start_at(empty)

        if not self.debug:
            self.root.mainloop()

    def load_data(self, data: typing.List) -> None:
        self._app_data = data

    def ask_for_load_project_path(self) -> str:
        path_to_project = filedialog.askopenfilename(filetypes=[('Booba Label Project', '.blp')])
        print(f'path -> {path_to_project}')
        return path_to_project

    def load_project_data(self, path_to_project: str) -> typing.List:
        result = []
        with open(path_to_project, 'r') as f:
            result = json.loads(f.read())
        return result


@spy_on
def empty(chart: AppGui, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.NEW_PROJECT:
        chart.load_data([])
        status = chart.trans(not_empty)
    elif e.signal == signals.LOAD_PROJECT:
        chart.load_data(chart.load_project_data(e.payload))
        status = chart.trans(not_empty)
    else:
        status = return_status.SUPER
        chart.temp.fun = chart.top

    return status


@spy_on
def not_empty(chart: AppGui, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        chart.temp.fun = empty

    return status


if __name__ == '__main__':
    app = AppGui('app')

    # app.live_trace = True
    # app.live_spy = True

    app.run()