import tkinter

from tkinter import filedialog

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

        label1 = tkinter.LabelFrame(frame, text='% validation')
        validation_percent = tkinter.StringVar(value='25')
        entry1 = tkinter.Entry(label1, textvariable=validation_percent)
        label1.grid(column=0, row=0, sticky='nesw')
        entry1.grid(column=0, row=0, sticky='nesw')

        label2 = tkinter.LabelFrame(frame, text='% validation')
        test_percent = tkinter.StringVar(value='25')
        entry2 = tkinter.Entry(label2, textvariable=test_percent)
        label2.grid(column=0, row=1, sticky='nesw')
        entry2.grid(column=0, row=0, sticky='nesw')

        ok_bnt = tkinter.Button(frame, text='Export to YOLO format', command=lambda: self.ask_for_path(
            validation_percent=validation_percent.get(), test_percent=test_percent.get()))
        ok_bnt.grid(column=0, row=2)

    def ask_for_path(self, validation_percent, test_percent):
        path = filedialog.askdirectory()
        if path:
            self.export({'validation_percent': validation_percent, 'test_percent': test_percent}, path=path)
            self.root.destroy()

    def export(self, options, path):
        pass