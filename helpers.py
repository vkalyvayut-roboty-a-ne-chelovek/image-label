import json
import random
import typing
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import commondialog

from miros import Event
from miros import signals
from miros import ActiveObject


def read_project_file_from_path(path_to_project_file: str) -> typing.Dict:
    result = None
    with open(path_to_project_file, 'r') as f:
        result = json.loads(f.read())
    return result


def save_project_file_to_path(path_to_project_file: str, data: typing.Dict) -> None:
    with open(path_to_project_file, 'w+') as f:
        f.write(json.dumps(data))


def ask_for_load_project_path() -> str:
    return filedialog.askopenfilename(filetypes=[('Booba Label Project', '.blp')])


def ask_for_save_project_path() -> str:
    return filedialog.asksaveasfilename(filetypes=[('Booba Label Project', '.blp')])


def ask_for_add_file_paths() -> typing.List[str]:
    return filedialog.askopenfilenames(filetypes=['PNG .png', 'JPEG .jpg', 'BMP .bmp'], multiple=True)


def ask_for_category_name(prnt) -> str:
    return pick_random_color()


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
    if file_path:
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
