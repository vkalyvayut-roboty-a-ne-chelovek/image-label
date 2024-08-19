import pathlib
import shutil
import os
import copy
from PIL import Image
import tkinter
from tkinter import filedialog

from image_label.exporters.yolo import YoloExporter, ExportOptions


class ImageFolder(YoloExporter):
    exported_id = 'exporters[image_folder]'

    def show_options(self):
        self.root: tkinter.Toplevel = tkinter.Toplevel()
        self.root.title('ImageFolder Options')
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

        def confirm_options():
            options = ExportOptions(validation_percent=validation_percent.get(),
                                    test_percent=test_percent.get())

            self.ask_for_path(options)

        ok_bnt = tkinter.Button(frame, text='Export to YOLO format', command=confirm_options)

        self.root.bind('<Return>', lambda _: confirm_options())
        self.root.bind('<KP_Enter>', lambda _: confirm_options())

        self.root.grab_set()

        ok_bnt.grid(column=0, row=3)

    def ask_for_path(self, options: ExportOptions):
        self.path = filedialog.askdirectory()
        self.root.destroy()

        if self.path:
            self.options = {'validation_percent': options.validation_percent,
                            'test_percent': options.test_percent}

            self.export()

    def convert_file_data_into_save_data(self, data):
        result = {}

        for filename, filedata in data:
            result[filename] = {
                'abs_path': copy.copy(filedata['abs_path']),
                'data': []
            }

            for figure in filedata['figures']:
                result[filename]['data'].append(figure['category'])
                if 'transformations' in filedata and len(filedata['transformations']) > 0:
                    image = Image.open(filedata['abs_path'])
                    for transform in filedata['transformations']:
                        image = self._apply_transformation_to_image(image, transform)
                    result[filename]['abs_path'] = self._save_to_temp_file(image, result[filename]['abs_path'])

        return result

    def mk_dataset_dir_and_save_dataset_data(self, dataset_name, dataset_data):
        dataset_dir = pathlib.Path(self.get_dest_dir_name(), dataset_name)
        dataset_dir.mkdir(parents=True)

        for filename, filedata in dataset_data.items():
            for category_name in filedata['data']:
                category_dir = pathlib.Path(dataset_dir, category_name)
                category_dir.mkdir(parents=True, exist_ok=True)

                _, ext = os.path.splitext(filedata['abs_path'])
                image_path = pathlib.Path(category_dir, f'{filename}{ext}').absolute()
                shutil.copyfile(filedata['abs_path'], image_path.absolute())
