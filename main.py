import json
import typing
import tkinter
import uuid
from PIL import ImageTk
from tkinter import filedialog
from tkinter import messagebox
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
        self._app_data = dict()
        self.selected_image_data = None

    def set_statechart(self, statechart: ActiveObject):
        self.statechart = statechart

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
                                              command=lambda: self.statechart.post_fifo(
                                                  Event(signal=signals.NEW_PROJECT)))
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project',
                                               command=lambda: self.statechart.post_fifo(
                                                   Event(signal=signals.LOAD_PROJECT,
                                                         payload=self.ask_for_load_project_path())))
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project',
                                               command=lambda: self.statechart.post_fifo(
                                                   Event(signal=signals.SAVE_PROJECT,
                                                         payload=self.ask_for_save_project_path())))

        self.add_file_btn = tkinter.Button(self.command_palette, text='Add File',
                                           command=lambda: self.statechart.post_fifo(
                                               Event(signal=signals.ADD_FILE,
                                                     payload=self.ask_for_add_file_paths())))
        self.remove_file_btn = tkinter.Button(self.command_palette, text='Remove File',
                                              command=lambda: self.statechart.post_fifo(
                                                  Event(signal=signals.REMOVE_FILE,
                                                        payload=self.files_treeview.selection())))

        self.draw_rectangle_btn = tkinter.Button(self.command_palette, text='Draw Rectangle',
                                                 command=lambda: self.statechart.post_fifo(
                                                     Event(signal=signals.DRAW_RECT)
                                                 ))
        self.draw_polygon_btn = tkinter.Button(self.command_palette, text='Draw Polygon',
                                               command=lambda: self.statechart.post_fifo(
                                                   Event(signal=signals.DRAW_POLY)
                                               ))

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
        self.drawing_canvas = tkinter.Canvas(self.drawing_frame, background='white')

        self.drawing_frame.grid(column=1, row=0, sticky='nesw', rowspan=2)
        self.drawing_frame.columnconfigure(0, weight=1)
        self.drawing_frame.rowconfigure(0, weight=1)
        self.drawing_canvas.grid(column=0, row=0, sticky='nesw')

        self.drawing_canvas_image = None

    def init_files_frame(self):
        self.files_frame = tkinter.Frame(self.root, background='blue')
        self.files_treeview = ttk.Treeview(self.files_frame, columns=['filename'])
        self.files_treeview['show'] = 'headings'
        self.files_treeview.heading('filename', text='Filename')

        self.files_treeview.bind('<Double-Button-1>', lambda e: self.statechart.post_fifo(Event(signal=signals.SELECT_IMAGE, payload=self.files_treeview.selection()[0])))

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

    def set_app_data(self, data: typing.List):
        self._app_data = dict()

        for idx, filedata in data.items():
            self.add_file(idx, filedata)

    def add_file(self, idx, data):
        self._app_data[idx] = data
        self.files_treeview.insert('', 'end', iid=idx, text=data['filename'], values=(data['filename'],))

    def remove_file(self, idx):
        self.files_treeview.delete(idx)
        del self._app_data[idx]

    def ask_for_load_project_path(self) -> str:
        return filedialog.askopenfilename(filetypes=[('Booba Label Project', '.blp')])

    def ask_for_save_project_path(self) -> str:
        return filedialog.asksaveasfilename(filetypes=[('Booba Label Project', '.blp')])

    def ask_for_add_file_paths(self) -> typing.List[str]:
        return filedialog.askopenfilenames(filetypes=['PNG .png', 'JPEG .jpg', 'BMP .bmp'], multiple=True)

    def select_image(self, idx):
        self.drawing_canvas.update()
        self.selected_image_data = {
            'idx': idx,
            'data': self._app_data[idx],
            'img': None
        }

        self.update_canvas_image()

    def update_canvas_image(self):
        try:
            self.selected_image_data['img'] = tkinter.PhotoImage(file=self.selected_image_data['data']['abs_path_to_file'])
            self.drawing_canvas.create_image(self.drawing_canvas.winfo_width() // 2,
                                             self.drawing_canvas.winfo_height() // 2,
                                             image=self.selected_image_data['img'], anchor='c')
        except (tkinter.TclError, ) as e:
            messagebox.showerror(title='Error while loading image',
                                 message=f"Error while loading image {self.selected_image_data['data']['abs_path_to_file']},\n{e}")


class GuiForTest(Gui):
    def run(self):
        self.statechart.start_at(empty)

    def add_file(self, idx, filename):
        self._app_data[idx] = filename

    def remove_file(self, idx):
        del self._app_data[idx]

    def select_image(self, idx):
        self.selected_image_data = {
            'idx': idx,
            'data': self._app_data[idx],
            'img': None
        }


class Statechart(ActiveObject):
    def __init__(self, name: str, gui: Gui):
        super().__init__(name=name)
        self.gui = gui
        self.gui.set_statechart(self)
        self._app_data = None
        self.selected_image_data = None

    def set_app_data(self, data: typing.Dict):
        self._app_data = data
        self.gui.set_app_data(data)

    def get_app_data(self) -> typing.Dict:
        return self._app_data

    def add_file(self, path_to_image: str):
        idx = str(uuid.uuid4())
        self._app_data[idx] = {
            'abs_path_to_file': path_to_image,
            "filename": path_to_image,
            "figures": []
        }
        self.gui.add_file(idx, self._app_data[idx])

    def remove_file(self, idx):
        del self._app_data[idx]
        self.gui.remove_file(idx)

    def select_image(self, idx):
        self.selected_image_data = {
            'idx': idx,
            'data': self._app_data[idx],
        }
        self.gui.select_image(idx)



@spy_on
def empty(chart: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.NEW_PROJECT:
        chart.set_app_data(dict())
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

    if e.signal == signals.ADD_FILE:
        status = return_status.HANDLED
        for path_to_image in e.payload:
            chart.add_file(path_to_image)
    elif e.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED
        for image_idx in e.payload:
            chart.remove_file(image_idx)
    elif e.signal == signals.SELECT_IMAGE:
        chart.select_image(e.payload)
        status = chart.trans(image_selected)
    else:
        status = return_status.SUPER
        chart.temp.fun = empty

    return status


@spy_on
def image_selected(chart: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    # if e.signal == signals.DRAW_POLY:
    #     status = chart.trans()
    # else:
    #     status = return_status.SUPER
    #     chart.temp.fun = not_empty

    status = return_status.SUPER
    chart.temp.fun = not_empty

    return status





if __name__ == '__main__':
    gui = Gui()

    statechart = Statechart('statechart', gui=gui)

    statechart.live_trace = True
    statechart.live_spy = True

    gui.run()

    print(statechart.trace())
