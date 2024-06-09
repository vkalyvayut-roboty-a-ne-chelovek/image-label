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
import helpers

class Gui:
    def __init__(self):
        self.statechart = None

    def set_statechart(self, statechart: ActiveObject):
        self.statechart = statechart

    def create_gui(self):
        self.init_window()
        self.init_command_palette()
        self.init_drawing_frame()
        self.init_files_frame()
        self.init_figures_frame()

        self.disable_save_button()

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
                                              command=lambda: self.statechart.post_fifo(Event(signal=signals.NEW_PROJECT)))
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project',
                                               command=lambda: self.statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=self.ask_for_load_project_path())))
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project',
                                               command=lambda: self.statechart.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=self.ask_for_save_project_path())))

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

        self.statechart.start_at(empty)

        self.root.mainloop()

    def enable_save_button(self):
        self.save_project_btn['state'] = 'normal'

    def disable_save_button(self):
        self.save_project_btn['state'] = 'disabled'

    def set_app_data(self, data: typing.List):
        self._app_data = data

    def ask_for_load_project_path(self) -> str:
        return filedialog.askopenfilename(filetypes=[('Booba Label Project', '.blp')])

    def ask_for_save_project_path(self) -> str:
        return filedialog.asksaveasfilename(filetypes=[('Booba Label Project', '.blp')])



class GuiForTest(Gui):
    def run(self):
        self.statechart.start_at(empty)

    def enable_save_button(self):
        pass

    def disable_save_button(self):
        pass


class Statechart(ActiveObject):
    def __init__(self, name: str, gui: Gui):
        super().__init__(name=name)
        self.gui = gui
        self.gui.set_statechart(self)
        self._app_data = None

    def set_app_data(self, data: typing.List):
        self._app_data = data
        self.gui.set_app_data(data)

    def get_app_data(self) -> typing.List:
        return self._app_data


@spy_on
def empty(chart: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.NEW_PROJECT:
        chart.set_app_data([])
        status = chart.trans(not_empty)
    elif e.signal == signals.LOAD_PROJECT:
        chart.set_app_data(helpers.read_project_file_from_path(e.payload))
        status = chart.trans(not_empty)
    elif e.signal == signals.SAVE_PROJECT:
        helpers.save_project_file_to_path(e.payload, chart.get_app_data())
        status = chart.trans(not_empty)
    else:
        status = return_status.SUPER
        chart.temp.fun = chart.top

    return status


@spy_on
def not_empty(chart: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        chart.gui.enable_save_button()
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        chart.temp.fun = empty

    return status


if __name__ == '__main__':
    gui = Gui()

    statechart = Statechart('statechart', gui=gui)

    statechart.live_trace = True
    statechart.live_spy = True

    gui.run()
