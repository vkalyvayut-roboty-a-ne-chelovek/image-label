import tkinter
import typing
from tkinter import ttk

from PIL import ImageTk

import helpers
from common_bus import CommonBus

class Gui:
    def __init__(self, bus: CommonBus):
        self.bus = bus
        self.bus.register_item('gui', self)

        self.image_on_canvas = None
        self.mouse_position_marker = None
        self.drawing_rect_point_1 = None
        self.drawing_rect_figure = None

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
        self.remove_file_btn.configure(command=lambda: helpers.remove_file_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))
        self.draw_rectangle_btn.configure(command=lambda: helpers.draw_rect_event(self.bus.statechart))
        self.draw_polygon_btn.configure(command=lambda: helpers.draw_poly_event(self.bus.statechart))

        self.root.mainloop()

    def add_file(self, id_, filedata):
        self.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

    def clear_files(self):
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children(''):
                self.files_frame_treeview.delete(item)

    def remove_file(self, id_):
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children():
                if item == id_:
                    self.files_frame_treeview.delete(item)

    def clear_figures(self):
        if self.figures_frame_treeview.tag_has('#files'):
            for item in self.figures_frame_treeview.get_children(''):
                self.figures_frame_treeview.delete(item)

    def clear_canvas(self):
        if self.drawing_frame_canvas.gettags('#draw_figures'):
            self.drawing_frame_canvas.delete('#draw_figures')

    def bind_select_image_listener(self):
        self.files_frame_treeview.bind('<Double-Button-1>', lambda _: helpers.select_image_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))

    def unbind_select_image_listener(self):
        self.files_frame_treeview.unbind('<Double-Button-1>')

    def load_image_into_canvas(self, abs_path):
        self.image_on_canvas = ImageTk.PhotoImage(file=abs_path)
        self.drawing_frame_canvas.create_image(
            self.drawing_frame_canvas.winfo_width() // 2,
            self.drawing_frame_canvas.winfo_height() // 2,
            image=self.image_on_canvas,
            tags=('#draw_figures')
        )

    def enable_save_project_btn(self):
        self.save_project_btn['state'] = 'normal'

    def disable_save_project_btn(self):
        self.save_project_btn['state'] = 'disabled'

    def enable_add_file_btn(self):
        self.add_file_btn['state'] = 'normal'

    def disable_add_file_btn(self):
        self.add_file_btn['state'] = 'disabled'

    def enable_remove_file_btn(self):
        self.remove_file_btn['state'] = 'normal'

    def disable_remove_file_btn(self):
        self.remove_file_btn['state'] = 'disabled'

    def enable_draw_buttons(self):
        self.draw_rectangle_btn['state'] = 'normal'
        self.draw_polygon_btn['state'] = 'normal'

    def disable_draw_buttons(self):
        self.draw_rectangle_btn['state'] = 'disabled'
        self.draw_polygon_btn['state'] = 'disabled'

    def bind_canvas_click_event(self):
        self.drawing_frame_canvas.bind('<Button-1>', lambda _e: helpers.click_canvas_event(self.bus.statechart, (_e.x, _e.y)))
        self.drawing_frame_canvas.bind('<Button-3>', lambda _e: helpers.reset_drawing_event(self.bus.statechart))
        self.root.bind('<KeyPress-Escape>', lambda _e: helpers.reset_drawing_event(self.bus.statechart))

    def unbind_canvas_click_event(self):
        self.drawing_frame_canvas.unbind('<Button-1>')
        self.drawing_frame_canvas.unbind('<Button-3>')
        self.root.unbind('<KeyPress-Escape>')

    def bind_canvas_motion_rect_drawing_stage_1(self):
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_position_marker(_e.x, _e.y))

    def unbind_canvas_motion_rect_drawing_stage_1(self):
        self.drawing_frame_canvas.unbind('<Motion>')

    def bind_canvas_motion_rect_drawing_stage_2(self):
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_rect_temp_figure(_e.x, _e.y))

    def unbind_canvas_motion_rect_drawing_stage_2(self):
        self.drawing_frame_canvas.unbind('<Motion>')

    def redraw_drawing_position_marker(self, x, y):
        self.clear_mouse_position_marker()
        self.mouse_position_marker = self.drawing_frame_canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline='red', tags=('#draw_figures',))

    def clear_mouse_position_marker(self):
        if self.mouse_position_marker:
            self.drawing_frame_canvas.delete(self.mouse_position_marker)

    def redraw_drawing_rect_temp_figure(self, x, y):
        self.clear_drawing_rect_temp_figure()

        self.redraw_drawing_position_marker(x, y)
        self.drawing_rect_figure = self.drawing_frame_canvas.create_rectangle(
            self.drawing_rect_point_1[0], self.drawing_rect_point_1[1],
            x, y,
            outline='red', width=2,
            tags=('#draw_figures',))

    def clear_drawing_rect_temp_figure(self):
        if self.drawing_rect_figure:
            self.drawing_frame_canvas.delete(self.drawing_rect_figure)

    def redraw_figures(self, figures: typing.List) -> None:
        for f in figures:
            if f['type'] == 'rect':
                self.drawing_frame_canvas.create_rectangle(f['points'][0][0], f['points'][0][1],
                                                           f['points'][1][0], f['points'][1][1],
                                                           fill='red', tags=('#draw_figures', ))


