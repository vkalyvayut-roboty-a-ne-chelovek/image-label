import json
import typing
from tkinter import filedialog
from tkinter import messagebox


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
