import datetime
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
        validation_percent = tkinter.StringVar(value='10')
        entry1 = tkinter.Entry(label1, textvariable=validation_percent)
        label1.grid(column=0, row=0, sticky='nesw')
        entry1.grid(column=0, row=0, sticky='nesw')

        label2 = tkinter.LabelFrame(frame, text='% validation')
        test_percent = tkinter.StringVar(value='10')
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

        ok_bnt = tkinter.Button(frame, text='Export to YOLO format', command=lambda: self.ask_for_path(
            validation_percent=validation_percent.get(), test_percent=test_percent.get(), export_rect_vals=export_rect_vals.get()))
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
        test_dataset_len = math.ceil(self.options['test_percent'] * percent)
        val_dataset_len = math.ceil(self.options['validation_percent'] * percent)

        return {
            'train': total_files - test_dataset_len - val_dataset_len,
            'test': test_dataset_len,
            'val': val_dataset_len
        }

    def extract_project_filenames(self):
        return [filename for filename, _ in self.bus.statechart.project.get_files()]

    def get_filenames_for_dataset(self, amount_of_files_per_dataset: typing.Dict):
        files = self.extract_project_filenames()
        return {
            'train': random.choices(files, k=amount_of_files_per_dataset['train']),
            'test': random.choices(files, k=amount_of_files_per_dataset['test']),
            'val': random.choices(files, k=amount_of_files_per_dataset['val']),
        }

    def get_datasets(self):

        datasets_lengths = self.get_datasets_lengths()
        datasets_filenames = self.get_filenames_for_dataset(datasets_lengths)

        datasets = {
            'train': self.bus.statechart.project.get_files(datasets_filenames['train']),
            'test': self.bus.statechart.project.get_files(datasets_filenames['test']),
            'val': self.bus.statechart.project.get_files(datasets_filenames['val']),
        }

        return datasets

    def mk_dataset_dir_and_save_dataset_data(self, dataset_name, dataset_data):
        dataset_dir = pathlib.Path(self.get_dest_dir_name(), dataset_name)
        dataset_dir.mkdir(parents=True)

    def export(self):
        self.mk_dest_dir()
        for dataset_name, dataset_data in self.get_datasets():
            self.mk_dataset_dir_and_save_dataset_data(dataset_name, dataset_data)

    # def extract_categories(self) -> typing.Dict:
    #     all_categories = []
    #     for filename, filedata in self.bus.statechart.project.get_files():
    #         for figure in filedata['figures']:
    #             all_categories.append(figure['category'].strip())
    #
    #     unique_categories = list(set(all_categories))
    #
    #     zipped = zip(unique_categories, range(len(unique_categories)))
    #
    #     return dict(zipped)
    #
    # def extract_keys(self) -> typing.List:
    #     return [k for (k, _) in self.bus.statechart.project.get_files()]
    #
    # def prepare_data(self):
    #     self.raw = self.bus.statechart.project.get_files()
    #     self.categories = self.extract_categories()
    #
    # def generate_datasets(self):
    #     train_keys, test_keys, val_keys = self.generate_train_test_val_keys()
    #     return {
    #         'train': self.bus.statechart.project.get_files(train_keys),
    #         'test': self.bus.statechart.project.get_files(test_keys),
    #         'val': self.bus.statechart.project.get_files(val_keys),
    #     }
    #
    # def generate_train_test_val_keys(self):
    #     all_keys = self.extract_keys()
    #     one_percent = len(all_keys) / 100
    #     val_amount = math.ceil(int(self.options['validation_percent']) * one_percent)
    #     test_amount = math.ceil(int(self.options['test_percent']) * one_percent)
    #     train_amount = len(all_keys) - test_amount - val_amount
    #
    #     return (random.choices(all_keys, k=train_amount),
    #             random.choices(all_keys, k=test_amount),
    #             random.choices(all_keys, k=val_amount))
    #
    # def fill_dataset_with_data(self, filenames):
    #     def _conv_rect(category, points):
    #         category_name = category.strip()
    #         converted_points = self._convert_rect_data_to_yolo_export_data(
    #                 points[0][0],
    #                 points[0][1],
    #                 points[1][0],
    #                 points[1][1]
    #         )
    #         return [
    #             str(self.categories[category_name]),
    #             *[str(p) for p in converted_points]
    #         ]
    #
    #     def _conv_poly(category, points):
    #         category_name = category.strip()
    #         converted_points = self._convert_rect_data_to_yolo_export_data(
    #             *self._convert_poly_data_to_yolo_export_data(points)
    #         )
    #         return [
    #             str(self.categories[category_name]),
    #             *[str(p) for p in converted_points]
    #         ]
    #
    #     data = {}
    #
    #     for filename, filedata in self.raw:
    #         if filename not in filenames:
    #             continue
    #
    #         data[filename] = {
    #             'abs_path': filedata['abs_path'],
    #             'data': []
    #         }
    #         for figure in filedata['figures']:
    #             if self.options['export_rect_vals'] == 1:
    #                 if figure['type'] == 'rect':
    #                     data[filename]['data'].append(
    #                         _conv_rect(
    #                             figure['category'],
    #                             figure['points'],
    #                         )
    #                     )
    #             elif self.options['export_rect_vals'] == 2:
    #                 if figure['type'] == 'rect':
    #                     data[filename]['data'].append(
    #                         _conv_rect(
    #                             figure['category'],
    #                             figure['points'],
    #                         )
    #                     )
    #                 elif figure['type'] == 'poly':
    #                     data[filename]['data'].append(
    #                         _conv_poly(figure['category'],
    #                                    figure['points'])
    #                     )
    #
    #     return data
    #
    # def export(self):
    #     self.prepare_data()
    #     datasets = self.generate_datasets()
    #
    #     path = pathlib.Path(self.path, str(datetime.datetime.utcnow()))
    #     path.mkdir()
    #
    #     for dataset_name, dataset_data in datasets.items():
    #         dataset_path = pathlib.Path(path, dataset_name)
    #         dataset_path.mkdir()
    #
    #         with open(pathlib.Path(dataset_path, 'classes.txt').absolute(), 'w+') as categories_file:
    #             categories_file.write('\n'.join(categories))
    #
    #         labels_dir = pathlib.Path(dataset_path, 'labels')
    #         labels_dir.mkdir()
    #         images_dir = pathlib.Path(dataset_path, 'images')
    #         images_dir.mkdir()
    #
    #         for filename, filedata in dataset_data.items():
    #             if filedata['data']:
    #                 _, ext = os.path.splitext(filedata['abs_path'])
    #                 with open(pathlib.Path(labels_dir, f'{filename}.txt').absolute(), 'w+') as label:
    #                     for line in filedata['data']:
    #                         _line = [str(i) for i in line]
    #                         label.write('\n'.join([' '.join(_line) for line in filedata['data']]))
    #                 shutil.copyfile(filedata['abs_path'], pathlib.Path(images_dir, f'{filename}{ext}'), follow_symlinks=True)
    #
    # @staticmethod
    # def _convert_rect_data_to_yolo_export_data(x1, y1, x2, y2):
    #     min_x, max_x, min_y, max_y = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
    #     w, h = max_x - min_x, max_y - min_y
    #
    #     center_x = min_x + w / 2.0
    #     center_y = min_y + h / 2.0
    #
    #     return center_x, center_y, w, h
    #
    # @staticmethod
    # def _convert_poly_data_to_yolo_export_data(points):
    #     xs = [point[0] for point in points]
    #     ys = [point[1] for point in points]
    #     min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    #
    #     w, h = max_x - min_x, max_y - min_y
    #
    #     center_x = min_x + w / 2.0
    #     center_y = min_y + h / 2.0
    #
    #     return center_x, center_y, w, h
    #
    #
    #

