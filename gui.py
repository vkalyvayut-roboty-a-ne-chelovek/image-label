import tkinter
from tkinter import ttk

import helpers
from common_bus import CommonBus

class Gui:
    def __init__(self, bus: CommonBus):
        self.bus = bus
        self.bus.register_item('gui', self)

        self.root = tkinter.Tk()
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.root.columnconfigure(1, weight=75)
        self.root.columnconfigure(2, weight=20)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.command_palette = tkinter.Frame(self.root, background='red')

        self.new_project_btn = tkinter.Button(self.command_palette, text='New Project')
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project')
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project')
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

        self.drawing_frame = tkinter.Frame(self.root, background='green')
        self.drawing_frame_canvas = tkinter.Canvas(self.drawing_frame)

        self.drawing_frame.grid(column=1, row=0, sticky='nesw', rowspan=2)
        self.drawing_frame.columnconfigure(0, weight=1)
        self.drawing_frame.rowconfigure(0, weight=1)
        self.drawing_frame_canvas.grid(column=0, row=0, sticky='nesw')

        self.files_frame = tkinter.Frame(self.root, background='blue')
        self.files_frame_treeview = ttk.Treeview(self.files_frame, columns=['filename'], selectmode='browse', show='headings')
        self.files_frame_treeview.heading('filename', text='Filename')

        self.files_frame.grid(column=2, row=0, sticky='nesw')
        self.files_frame.columnconfigure(0, weight=1)
        self.files_frame.rowconfigure(0, weight=1)
        self.files_frame_treeview.grid(column=0, row=0, sticky='nesw')
        self.files_frame_treeview_scrollbar = ttk.Scrollbar(self.files_frame, orient='vertical')
        self.files_frame_treeview_scrollbar.grid(column=1, row=0, sticky='nesw')
        self.files_frame_treeview.config(yscrollcommand=self.files_frame_treeview_scrollbar.set)
        self.files_frame_treeview_scrollbar.config(command=self.files_frame_treeview.yview)

        self.figures_frame = tkinter.Frame(self.root, background='cyan')
        self.figures_frame_treeview = ttk.Treeview(self.figures_frame, columns=['figure'], selectmode='browse', show='headings')
        self.figures_frame_treeview.heading('figure', text='Figure')

        self.figures_frame.grid(column=2, row=1, sticky='nesw')
        self.figures_frame.columnconfigure(0, weight=1)
        self.figures_frame.rowconfigure(0, weight=1)
        self.figures_frame_treeview.grid(column=0, row=0, sticky='nesw')
        self.figures_frame_treeview_scrollbar = ttk.Scrollbar(self.figures_frame, orient='vertical')
        self.figures_frame_treeview_scrollbar.grid(column=1, row=0, sticky='nesw')
        self.figures_frame_treeview.config(yscrollcommand=self.figures_frame_treeview_scrollbar.set)
        self.figures_frame_treeview_scrollbar.config(command=self.figures_frame_treeview.yview)

    def run(self):
        self.new_project_btn.configure(command=lambda: helpers.new_project_event(self.bus.statechart))
        self.load_project_btn.configure(command=lambda: helpers.load_project_event(self.bus.statechart))
        self.save_project_btn.configure(command=lambda: helpers.save_project_event(self.bus.statechart))
        self.add_file_btn.configure(command=lambda: helpers.add_file_event(self.bus.statechart))
        self.remove_file_btn.configure(command=lambda: helpers.remove_file_event(self.bus.statechart, self.files_frame_treeview.selection()))

        self.root.mainloop()
