import json
import random
import typing
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from miros import Event
from miros import signals
from miros import ActiveObject


def read_project_file_from_path(path_to_project_file: str) -> typing.Dict:
    result = None
    with open(path_to_project_file, 'r') as f:
        result = json.loads(f.read())
    return result


def ask_for_load_project_path() -> str:
    return filedialog.askopenfilename(filetypes=[('Booba Label Project', '.boobalp')])


def ask_for_save_project_path() -> str:
    return filedialog.asksaveasfilename(filetypes=[('Booba Label Project', '.boobalp')])


def ask_for_add_file_paths() -> typing.List[str]:
    return filedialog.askopenfilenames(filetypes=['PNG .png', 'JPEG .jpg', 'BMP .bmp'], multiple=True)


def pick_random_color():
    colors = ['#300', '#600', '#900', '#C00', '#F00', '#003', '#303', '#603', '#903', '#C03', '#F03', '#006', '#306', '#606', '#906', '#C06', '#F06', '#009', '#309', '#609', '#909', '#C09', '#F09', '#00C', '#30C', '#60C', '#90C', '#C0C', '#F0C', '#00F', '#30F', '#60F', '#90F', '#C0F', '#F0F', '#030', '#330', '#630', '#930', '#C30', '#F30', '#033', '#333', '#633', '#933', '#C33', '#F33', '#036', '#336', '#636', '#936', '#C36', '#F36', '#039', '#339', '#639', '#939', '#C39', '#F39', '#03C', '#33C', '#63C', '#93C', '#C3C', '#F3C', '#03F', '#33F', '#63F', '#93F', '#C3F', '#F3F', '#060', '#360', '#660', '#960', '#C60', '#F60', '#063', '#363', '#663', '#963', '#C63', '#F63', '#066', '#366', '#666', '#966', '#C66', '#F66', '#069', '#369', '#669', '#969', '#C69', '#F69', '#06C', '#36C', '#66C', '#96C', '#C6C', '#F6C', '#06F', '#36F', '#66F', '#96F', '#C6F', '#F6F', '#090', '#390', '#690', '#990', '#C90', '#F90', '#093', '#393', '#693', '#993', '#C93', '#F93', '#096', '#396', '#696', '#996', '#C96', '#F96', '#099', '#399', '#699', '#999', '#C99', '#F99', '#09C', '#39C', '#69C', '#99C', '#C9C', '#F9C', '#09F', '#39F', '#69F', '#99F', '#C9F', '#F9F', '#0C0', '#3C0', '#6C0', '#9C0', '#CC0', '#FC0', '#0C3', '#3C3', '#6C3', '#9C3', '#CC3', '#FC3', '#0C6', '#3C6', '#6C6', '#9C6', '#CC6', '#FC6', '#0C9', '#3C9', '#6C9', '#9C9', '#CC9', '#FC9', '#0CC', '#3CC', '#6CC', '#9CC', '#CCC', '#FCC', '#0CF', '#3CF', '#6CF', '#9CF', '#CCF', '#FCF', '#0F0', '#3F0', '#6F0', '#9F0', '#CF0', '#FF0', '#0F3', '#3F3', '#6F3', '#9F3', '#CF3', '#FF3', '#0F6', '#3F6', '#6F6', '#9F6', '#CF6', '#FF6', '#0F9', '#3F9', '#6F9', '#9F9', '#CF9', '#FF9', '#0FC', '#3FC', '#6FC', '#9FC', '#CFC', '#FFC', '#0FF', '#3FF', '#6FF', '#9FF', '#CFF']
    return random.sample(colors, 1)


def new_project_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.NEW_PROJECT))


def load_project_event(s: ActiveObject) -> None:
    file_path = ask_for_load_project_path()
    if file_path:
        s.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=file_path))


def save_project_event(s: ActiveObject) -> None:
    file_path = ask_for_save_project_path()
    if file_path:
        s.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=file_path))


def select_image_event(s: ActiveObject, file_id: typing.Any) -> None:
    if file_id:
        s.post_fifo(Event(signal=signals.SELECT_IMAGE, payload=file_id))


def add_file_event(s: ActiveObject) -> None:
    file_path = ask_for_add_file_paths()
    if len(file_path) > 0:
        s.post_fifo(Event(signal=signals.ADD_FILE, payload=file_path))



def remove_file_event(s: ActiveObject, file_ids: typing.Any) -> None:
    msg = f'Are you sure to remove selected file?'
    if messagebox.askyesno(title=msg, message=msg):
        s.post_fifo(Event(signal=signals.REMOVE_FILE, payload=file_ids))


def draw_rect_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.DRAW_RECT))


def draw_poly_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.DRAW_POLY))


def add_point_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.ADD_POINT))


def remove_point_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.REMOVE_POINT))


def move_point_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.MOVE_POINT))


def update_figures_point_position_event(s: ActiveObject, coords: typing.Tuple[int, int], figure_point_data: typing.Dict) -> None:
    if figure_point_data:
        s.post_fifo(Event(signal=signals.UPDATE_FIGURE_POINT_POSITION, payload={
            'coords': coords,
            'figure_idx': figure_point_data['figure_idx'],
            'point_idx': figure_point_data['point_idx']
        }))


def update_figure_remove_point_event(s: ActiveObject, figure_point_data: typing.Dict) -> None:
    if figure_point_data:
        s.post_fifo(Event(signal=signals.UPDATE_FIGURE_REMOVE_POINT, payload={
            'figure_idx': figure_point_data['figure_idx'],
            'point_idx': figure_point_data['point_idx']
        }))

def update_figure_add_point_event(s: ActiveObject, coords: typing.Tuple[int, int], figure_point_data: typing.Dict) -> None:
    if figure_point_data:
        s.post_fifo(Event(signal=signals.UPDATE_FIGURE_INSERT_POINT, payload={
            'coords': coords,
            'figure_idx': figure_point_data['figure_idx'],
            'point_idx': figure_point_data['point_idx']
        }))


def click_canvas_event(s: ActiveObject, coords: typing.Tuple[int, int]) -> None:
    s.post_fifo(Event(signal=signals.CLICK, payload=coords))


def reset_drawing_event(s: ActiveObject) -> None:
    s.post_fifo(Event(signal=signals.RESET_DRAWING))


def figure_selected_event(s: ActiveObject, id_: int) -> None:
    s.post_fifo(Event(signal=signals.FIGURE_SELECTED, payload=id_))


def delete_figure_event(s: ActiveObject, id_: int) -> None:
    s.post_fifo(Event(signal=signals.DELETE_FIGURE, payload=id_))


def clamp(_min, _max, cur):
    return min(_max, max(_min, cur))


# костыль, если в окне присутствует tkinter.Label
# то происходит потеря фокуса и невозможность скрытия окна
def ask_for_category_name(c: ActiveObject, file_id: str, figure_id: int, default_val: str = '', values: typing.List[str] = ()):
    val = tkinter.StringVar(value=default_val)

    w = tkinter.Toplevel()
    w.geometry(f'+{c.bus.gui.root.winfo_width()//2}+{c.bus.gui.root.winfo_height()//2}')
    w.title('Enter category name')
    w.columnconfigure(0, weight=1)
    w.rowconfigure(0, weight=1)
    w.rowconfigure(1, weight=1)
    w.rowconfigure(2, weight=1)

    def on_ok():
        if len(val.get()) > 0:
            set_figure_category_event(c, file_id, figure_id, val.get())
            w.destroy()

    label = tkinter.Label(w, text='Enter category name')
    label.grid(column=0, row=0, sticky='nesw')
    entry = ttk.Combobox(w, textvariable=val, values=values)
    entry.grid(column=0, row=1, sticky='nesw')
    btn_ok = tkinter.Button(w, text='OK', command=on_ok)
    btn_ok.grid(column=0, row=2, sticky='nesw')

    w.geometry(f'250x100+{c.bus.gui.root.winfo_width()//2 - 125 }+{c.bus.gui.root.winfo_height()//2 - 50}')
    w.bind('<KP_Enter>', lambda _: on_ok())
    w.bind('<Return>', lambda _: on_ok())



def undo_event(s: ActiveObject):
    s.post_fifo(Event(signal=signals.UNDO_HISTORY))


def set_figure_category_event(s: ActiveObject, file_id, figure_id, category_name):
    s.post_fifo(Event(signal=signals.SET_FIGURE_CATEGORY, payload={'file_id': file_id, 'figure_id': figure_id, 'category': category_name}))


def clamp_coords_in_image_area(i_w, i_h, c_w, c_h, x, y) -> (int, int):
    center_x, center_y = c_w / 2.0, c_h / 2.0
    min_x = center_x - i_w / 2
    max_x = center_x + i_w / 2
    min_y = center_y - i_h / 2
    max_y = center_y + i_h / 2

    clamped_x = clamp(min_x, max_x, x)
    clamped_y = clamp(min_y, max_y, y)

    return clamped_x, clamped_y


def from_canvas_to_image_coords(i_w, i_h, c_w, c_h, x, y):
    clamped_x, clamped_y = clamp_coords_in_image_area(i_w, i_h, c_w, c_h, x, y)

    center_x, center_y = c_w / 2.0, c_h / 2.0

    max_x = center_x + i_w / 2
    max_y = center_y + i_h / 2

    rel_x = 1.0 - (max_x - clamped_x) / i_w
    rel_y = 1.0 - (max_y - clamped_y) / i_h

    return rel_x, rel_y


def from_image_to_canvas_coords(i_w, i_h, c_w, c_h, x, y):
    center_x, center_y = c_w / 2.0, c_h / 2.0

    min_x = center_x - i_w / 2
    min_y = center_y - i_h / 2

    abs_x = min_x + (x * i_w)
    abs_y = min_y + (y * i_h)

    return abs_x, abs_y
