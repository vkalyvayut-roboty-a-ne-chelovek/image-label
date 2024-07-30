import copy
import math
import os.path
import pathlib
import random
import shutil
import tempfile
import tkinter
import typing

from tkinter import filedialog
from tkinter import ttk
from PIL import Image


class YoloExporter:
    def __init__(self, bus):
        self.bus = bus
        self.bus.register_item('exporters[yolo]', self)
        self.options = {}
        self.path = None
        self.raw = None
        self.categories = {}
        self.root = None

    def show_options(self):
        self.root: tkinter.Toplevel = tkinter.Toplevel()
        self.root.title('YOLO Options')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        frame = tkinter.Frame(self.root)
        frame.grid(column=0, row=0, sticky='nesw')
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)

        label1 = tkinter.LabelFrame(frame, text='% validation')
        validation_percent = tkinter.StringVar(value='0')
        entry1 = tkinter.Entry(label1, textvariable=validation_percent)
        label1.grid(column=0, row=0, sticky='nesw')
        entry1.grid(column=0, row=0, sticky='nesw')

        label2 = tkinter.LabelFrame(frame, text='% test')
        test_percent = tkinter.StringVar(value='0')
        entry2 = tkinter.Entry(label2, textvariable=test_percent)
        label2.grid(column=0, row=1, sticky='nesw')
        entry2.grid(column=0, row=0, sticky='nesw')

        frame3 = tkinter.Frame(frame)
        frame3.rowconfigure(0, weight=1)
        frame3.rowconfigure(1, weight=1)
        frame3.columnconfigure(0, weight=1)
        frame3.columnconfigure(1, weight=1)

        frame3.grid(column=0, row=2, sticky='nesw')

        export_rect_vals = tkinter.IntVar(value=0)
        rb1 = ttk.Radiobutton(frame3, variable=export_rect_vals, value=1, text='Export only rectangulars')
        rb2 = ttk.Radiobutton(frame3, variable=export_rect_vals, value=2, text='Export with polygons (covert polygons to rectangles)')

        rb1.grid(column=0, row=0, sticky='nesw')
        rb2.grid(column=0, row=1, sticky='nesw')

        def confirm_options():
            self.ask_for_path(
                validation_percent=validation_percent.get(),
                test_percent=test_percent.get(),
                export_rect_vals=export_rect_vals.get())

        ok_bnt = tkinter.Button(frame, text='Export to YOLO format', command=confirm_options)

        self.root.bind('<Return>', lambda _: confirm_options())
        self.root.bind('<KP_Enter>', lambda _: confirm_options())

        self.root.grab_set()

        ok_bnt.grid(column=0, row=3)

    def ask_for_path(self, validation_percent, test_percent, export_rect_vals):
        if export_rect_vals == 0:
            return
        self.path = filedialog.askdirectory()
        self.root.destroy()

        if self.path:
            self.options = {'validation_percent': validation_percent,
                            'test_percent': test_percent,
                            'export_rect_vals': export_rect_vals}

            self.export()

    def get_dest_dir_name(self):
        project_name, _ = os.path.splitext(os.path.basename(self.bus.statechart.project.path))
        return pathlib.Path(self.path, project_name).absolute()

    def mk_dest_dir(self):
        dest_dir_path = self.get_dest_dir_name()
        dest_dir_path.mkdir()

    def get_datasets_lengths(self):
        total_files = len(self.bus.statechart.project.get_files())
        percent = total_files / 100
        test_dataset_len = math.ceil(float(self.options['test_percent']) * percent)
        val_dataset_len = math.ceil(float(self.options['validation_percent']) * percent)

        return {
            'train': total_files - test_dataset_len - val_dataset_len,
            'test': test_dataset_len,
            'val': val_dataset_len
        }

    def extract_project_filenames(self):
        return [filename for filename, _ in self.bus.statechart.project.get_files()]

    def get_filenames_for_dataset(self, amount_of_files_per_dataset: typing.Dict):
        files = self.extract_project_filenames()
        result = {}
        files_already_selected = []

        assert sum(amount_of_files_per_dataset.values()) <= len(files)

        for dataset_name, dataset_files_amount in amount_of_files_per_dataset.items():
            selected_files = []

            while len(selected_files) != dataset_files_amount:
                random_file = random.choice(files)
                if random_file not in files_already_selected:
                    selected_files.append(random_file)
                    files_already_selected.append(random_file)

            result[dataset_name] = copy.deepcopy(list(set(selected_files)))

        return result

    def get_datasets(self):
        datasets_lengths = self.get_datasets_lengths()
        datasets_filenames = self.get_filenames_for_dataset(datasets_lengths)

        datasets = {
            'train': self.convert_file_data_into_save_data(
                self.bus.statechart.project.get_files(datasets_filenames['train'])
            ),
            'test': self.convert_file_data_into_save_data(
                self.bus.statechart.project.get_files(datasets_filenames['test'])
            ),
            'val': self.convert_file_data_into_save_data(
                self.bus.statechart.project.get_files(datasets_filenames['val'])
            ),
        }

        return datasets

    def extract_categories(self):
        unique_categories = sorted(set(self.bus.statechart.project.get_all_categories()))
        zipped = zip(unique_categories, range(len(unique_categories)))
        return dict(zipped)

    def convert_file_data_into_save_data(self, data):
        result = {}
        categories = self.extract_categories()

        for filename, filedata in data:
            result[filename] = {
                'abs_path': copy.copy(filedata['abs_path']),
                'data': []
            }

            for figure in filedata['figures']:
                category_id = str(categories[figure['category']])
                if figure['type'] == 'rect':
                    _converted_figure_data = self._convert_rect_data_to_yolo_export_data(
                        *figure['points'][0],
                        *figure['points'][1]
                    )
                    result[filename]['data'].append([
                        category_id,
                        *map(str, _converted_figure_data)
                    ])
                elif figure['type'] == 'poly':
                    if self.options['export_rect_vals'] == 2:
                        _converted_figure_data = self._convert_poly_data_to_yolo_export_data(
                            figure['points']
                        )
                        result[filename]['data'].append([
                            category_id,
                            *map(str, _converted_figure_data)
                        ])

                if 'transformations' in filedata and len(filedata['transformations']) > 0:
                    image = Image.open(filedata['abs_path'])
                    for transform in filedata['transformations']:
                        image = self._apply_transformation_to_image(image, transform)
                    result[filename]['abs_path'] = self._save_to_temp_file(image, result[filename]['abs_path'])

        return result

    @staticmethod
    def _apply_transformation_to_image(image: Image, transform: str) -> Image:
        if transform == 'rotate_cw':
            image = image.rotate(angle=-90, expand=True)
        elif transform == 'rotate_ccw':
            image = image.rotate(angle=90, expand=True)
        return image

    @staticmethod
    def _save_to_temp_file(image: Image, src_abs_path: str) -> str:
        _, ext = os.path.splitext(src_abs_path)

        assert len(ext) > 1

        temp_path = tempfile.mktemp(suffix=ext)
        with open(temp_path, mode='wb') as temp_image_handle:
            ext = ext.strip('.')
            image.save(temp_image_handle, format=ext)

        return temp_path

    @staticmethod
    def _convert_rect_data_to_yolo_export_data(x1, y1, x2, y2):
        min_x, max_x, min_y, max_y = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
        w, h = max_x - min_x, max_y - min_y

        center_x = min_x + w / 2.0
        center_y = min_y + h / 2.0

        return center_x, center_y, w, h

    @staticmethod
    def _convert_poly_data_to_yolo_export_data(points):
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)

        w, h = max_x - min_x, max_y - min_y

        center_x = min_x + w / 2.0
        center_y = min_y + h / 2.0

        return center_x, center_y, w, h

    def mk_dataset_dir_and_save_dataset_data(self, dataset_name, dataset_data):
        dataset_dir = pathlib.Path(self.get_dest_dir_name(), dataset_name)
        dataset_dir.mkdir(parents=True)

        categories = self.extract_categories()
        categories_file_path = pathlib.Path(dataset_dir, 'classes.txt')
        with open(categories_file_path.absolute(), 'w') as categories_handle:
            categories_handle.write('\n'.join(categories.keys()))

        labels_dir = pathlib.Path(dataset_dir, 'labels')
        labels_dir.mkdir()

        images_dir = pathlib.Path(dataset_dir, 'images')
        images_dir.mkdir()

        for filename, filedata in dataset_data.items():
            label_txt_path = pathlib.Path(labels_dir, f'{filename}.txt').absolute()
            label_txt_str = '\n'.join([' '.join(line) for line in filedata['data']])

            with open(label_txt_path, 'w') as label_txt_handle:
                label_txt_handle.write(label_txt_str)

            _, ext = os.path.splitext(filedata['abs_path'])
            image_path = pathlib.Path(images_dir, f'{filename}{ext}').absolute()
            shutil.copyfile(filedata['abs_path'], image_path.absolute())

    def export(self):
        datasets = self.get_datasets()
        self.mk_dest_dir()

        for dataset_name, dataset_data in datasets.items():
            self.mk_dataset_dir_and_save_dataset_data(dataset_name, dataset_data)