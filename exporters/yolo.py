import tkinter

from tkinter import filedialog
from tkinter import ttk

class YoloExporter:
    def __init__(self, bus):
        self.bus = bus
        self.bus.register_item('exporters[yolo]', self)
        self.options = {}

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
        path = filedialog.askdirectory()
        self.root.destroy()

        if path:
            options = {'validation_percent': validation_percent,
                       'test_percent': test_percent,
                       'export_rect_vals': export_rect_vals}
            self.export(options, path=path)

    def export(self, options, path):
        raw = self.bus.statechart.project.get_files()
        categories = []
        for filename, filedata in raw:
            for figure in filedata['figures']:
                categories.append(figure['category'].strip())

        categories = list(set(categories))

        data = {}
        for filename, filedata in raw:
            data[filename] = []
            for figure in filedata['figures']:
                if options['export_rect_vals'] == 1:
                    if figure['type'] == 'rect':
                        data[filename].append([
                            categories.index(figure['category'].strip()),
                            *self._convert_rect_data_to_yolo_export_data(
                                figure['points'][0][0],
                                figure['points'][0][1],
                                figure['points'][1][0],
                                figure['points'][1][1]
                            )])
                elif options['export_rect_vals'] == 2:
                    if figure['type'] == 'rect':
                        data[filename].append([
                            categories.index(figure['category'].strip()),
                            *self._convert_rect_data_to_yolo_export_data(
                                figure['points'][0][0],
                                figure['points'][0][1],
                                figure['points'][1][0],
                                figure['points'][1][1]
                            )])
                    elif figure['type'] == 'poly':
                        data[filename].append([
                            categories.index(figure['category'].strip()),
                            *self._convert_poly_data_to_yolo_export_data(figure['points'])])


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




