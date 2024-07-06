import copy
import tkinter
import typing
from tkinter import ttk

from PIL import ImageTk, Image

from src import helpers
from src.common_bus import CommonBus
from src.figure import Figure

class Gui:
    def __init__(self, bus: CommonBus):
        self.bus = bus
        self.bus.register_item('gui', self)

        self.image_to_load_on_canvas: Image = None
        self.image_on_canvas: ImageTk = None
        self.mouse_position_marker = None
        self.drawing_rect_point_1 = None
        self.drawing_rect_figure = None

        self.drawing_poly_points = None
        self.drawing_poly_figures = None

        self.moving_figure_point = None

        self.root = tkinter.Tk()
        self.root.title('BOOBA')
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.main_menu = None
        self.project_menu = None
        self.figure_menu = None
        self.files_frame_treeview_menu = None
        self.figures_frame_treeview_menu = None
        self.exporters_menu = None
        self.help_menu = None

        self.root.columnconfigure(1, weight=90)
        self.root.columnconfigure(2, weight=10)
        self.root.rowconfigure(0, weight=80)
        self.root.rowconfigure(1, weight=20)

        self.command_palette = tkinter.Frame(self.root)

        self.new_project_btn = tkinter.Button(self.command_palette, text='New Project')
        self.load_project_btn = tkinter.Button(self.command_palette, text='Load Project')
        self.save_project_btn = tkinter.Button(self.command_palette, text='Save Project')
        self.add_file_btn = tkinter.Button(self.command_palette, text='Add File')
        self.remove_file_btn = tkinter.Button(self.command_palette, text='Remove File')
        self.draw_rectangle_btn = tkinter.Button(self.command_palette, text='Draw Rectangle')
        self.draw_polygon_btn = tkinter.Button(self.command_palette, text='Draw Polygon')
        self.add_point_btn = tkinter.Button(self.command_palette, text='Add Point')
        self.remove_point_btn = tkinter.Button(self.command_palette, text='Remove Point')
        self.move_point_btn = tkinter.Button(self.command_palette, text='Move Point')
        self.undo_btn = tkinter.Button(self.command_palette, text='UNDO')
        self.rotate_cw_btn = tkinter.Button(self.command_palette, text='Rotate Right')
        self.rotate_ccw_btn = tkinter.Button(self.command_palette, text='Rotate Left')

        self.command_palette.grid(column=0, row=0, sticky='nsw', rowspan=2)
        self.new_project_btn.grid(column=0, row=0)
        self.load_project_btn.grid(column=0, row=1)
        self.save_project_btn.grid(column=0, row=2)

        self.add_file_btn.grid(column=0, row=3)
        self.remove_file_btn.grid(column=0, row=4)

        self.draw_rectangle_btn.grid(column=0, row=5)
        self.draw_polygon_btn.grid(column=0, row=6)
        self.add_point_btn.grid(column=0, row=7)
        self.remove_point_btn.grid(column=0, row=8)
        self.move_point_btn.grid(column=0, row=9)
        self.undo_btn.grid(column=0, row=10)
        self.rotate_cw_btn.grid(column=0, row=11)
        self.rotate_ccw_btn.grid(column=0, row=12)

        self.drawing_frame = tkinter.Frame(self.root)
        self.drawing_frame_canvas = tkinter.Canvas(self.drawing_frame)

        self.drawing_frame.grid(column=1, row=0, sticky='nesw', rowspan=2)
        self.drawing_frame.columnconfigure(0, weight=1)
        self.drawing_frame.rowconfigure(0, weight=1)
        self.drawing_frame_canvas.grid(column=0, row=0, sticky='nesw')

        self.files_frame = tkinter.Frame(self.root)
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

        self.figures_frame = tkinter.Frame(self.root)
        self.figures_frame_treeview = ttk.Treeview(self.figures_frame, columns=['figure', 'id'], selectmode='browse', show='headings', displaycolumns=('figure',))
        self.figures_frame_treeview.heading('figure', text='Figure')

        self.figures_frame.grid(column=2, row=1, sticky='nesw')
        self.figures_frame.columnconfigure(0, weight=1)
        self.figures_frame.rowconfigure(0, weight=1)
        self.figures_frame_treeview.grid(column=0, row=0, sticky='nesw')
        self.figures_frame_treeview_scrollbar = ttk.Scrollbar(self.figures_frame, orient='vertical')
        self.figures_frame_treeview_scrollbar.grid(column=1, row=0, sticky='nesw')
        self.figures_frame_treeview.config(yscrollcommand=self.figures_frame_treeview_scrollbar.set)
        self.figures_frame_treeview_scrollbar.config(command=self.figures_frame_treeview.yview)

        self.init_bindings()

    def init_bindings(self):
        self.new_project_btn.configure(command=lambda: helpers.new_project_event(self.bus.statechart))
        self.load_project_btn.configure(command=lambda: helpers.load_project_event(self.bus.statechart))
        self.save_project_btn.configure(command=lambda: helpers.save_project_event(self.bus.statechart))
        self.add_file_btn.configure(command=lambda: helpers.add_file_event(self.bus.statechart))
        self.remove_file_btn.configure(
            command=lambda: helpers.remove_file_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))
        self.draw_rectangle_btn.configure(command=lambda: helpers.draw_rect_event(self.bus.statechart))
        self.draw_polygon_btn.configure(command=lambda: helpers.draw_poly_event(self.bus.statechart))
        self.add_point_btn.configure(command=lambda: helpers.add_point_event(self.bus.statechart))
        self.remove_point_btn.configure(command=lambda: helpers.remove_point_event(self.bus.statechart))
        self.move_point_btn.configure(command=lambda: helpers.move_point_event(self.bus.statechart))
        self.undo_btn.configure(command=lambda: helpers.undo_event(self.bus.statechart))
        self.rotate_cw_btn.configure(command=lambda: helpers.rotate_cw_event(self.bus.statechart))
        self.rotate_ccw_btn.configure(command=lambda: helpers.rotate_ccw_event(self.bus.statechart))

        self.root.bind('<Control-n>', lambda _: helpers.new_project_event(self.bus.statechart))
        self.root.bind('<Control-o>', lambda _: helpers.load_project_event(self.bus.statechart))
        self.root.bind('<Control-s>', lambda _: helpers.save_project_event(self.bus.statechart))

        self.root.bind('<Control-i>', lambda _: helpers.add_file_event(self.bus.statechart))

        self.root.bind('<Control-r>', lambda _: helpers.draw_rect_event(self.bus.statechart))
        self.root.bind('<KeyPress-1>', lambda _: helpers.draw_rect_event(self.bus.statechart))
        self.root.bind('<Control-p>', lambda _: helpers.draw_poly_event(self.bus.statechart))
        self.root.bind('<KeyPress-2>', lambda _: helpers.draw_poly_event(self.bus.statechart))

        self.root.bind('<KeyPress-a>', lambda _: helpers.add_point_event(self.bus.statechart))
        self.root.bind('<KeyPress-x>', lambda _: helpers.remove_point_event(self.bus.statechart))
        self.root.bind('<KeyPress-g>', lambda _: helpers.move_point_event(self.bus.statechart))

        self.root.bind('<Control-z>', lambda _: helpers.undo_event(self.bus.statechart))

        self.main_menu = tkinter.Menu(borderwidth=0)
        self.project_menu = tkinter.Menu(tearoff=False)
        self.figure_menu = tkinter.Menu(tearoff=False)
        self.exporters_menu = tkinter.Menu(tearoff=False)
        self.help_menu = tkinter.Menu(tearoff=False)

        if self.bus.exporters:
            for k, v in self.bus.exporters.items():
                self.exporters_menu.add_command(label=k, command=lambda: v.show_options())

        self.project_menu.add_command(label='New Project', accelerator='<Control-n>',
                                      command=lambda: helpers.new_project_event(self.bus.statechart))
        self.project_menu.add_command(label='Load Project', accelerator='<Control-o>',
                                      command=lambda: helpers.load_project_event(self.bus.statechart))
        self.project_menu.add_command(label='Save Project', accelerator='<Control-s>',
                                      command=lambda: helpers.save_project_event(self.bus.statechart),
                                      state='disabled')
        self.project_menu.add_separator()
        self.project_menu.add_command(label='Add File', accelerator='<Control-i>',
                                      command=lambda: helpers.add_file_event(self.bus.statechart),
                                      state='disabled')
        self.project_menu.add_command(label='Remove File', accelerator='<Delete>',
                                      command=lambda: helpers.remove_file_event(self.bus.statechart,
                                                                                self.files_frame_treeview.selection()[
                                                                                    0]),
                                      state='disabled')

        self.project_menu.add_separator()
        self.project_menu.add_command(label='Quit',
                                      command=lambda: helpers.quit_event(self.bus.statechart))

        self.figure_menu.add_command(label='Draw Rectangle', accelerator='<Control-r>',
                                     command=lambda: helpers.draw_rect_event(self.bus.statechart),
                                     state='disabled')
        self.figure_menu.add_command(label='Draw Polygon', accelerator='<Control-p>',
                                     command=lambda: helpers.draw_poly_event(self.bus.statechart),
                                     state='disabled')
        self.figure_menu.add_separator()

        self.figure_menu.add_command(label='Add Point',
                                     command=lambda: helpers.add_point_event(self.bus.statechart),
                                     state='disabled')
        self.figure_menu.add_command(label='Remove Point',
                                     command=lambda: helpers.remove_point_event(self.bus.statechart),
                                     state='disabled')
        self.figure_menu.add_command(label='Move Point',
                                     command=lambda: helpers.move_point_event(self.bus.statechart),
                                     state='disabled')
        self.figure_menu.add_separator()

        self.figure_menu.add_command(label='Undo', accelerator='<Control-z>',
                                     command=lambda: helpers.undo_event(self.bus.statechart),
                                     state='disabled')

        self.help_menu.add_command(label='Help', command=lambda: self.show_help())

        self.main_menu.add_cascade(label='Project', menu=self.project_menu)
        self.main_menu.add_cascade(label='Figure', menu=self.figure_menu)
        self.main_menu.add_cascade(label='Export', menu=self.exporters_menu)
        self.main_menu.add_cascade(label='Help', menu=self.help_menu)

        self.files_frame_treeview_menu = tkinter.Menu(tearoff=False)
        self.files_frame_treeview_menu.add_command(label='Add File',
                                                   command=lambda: helpers.add_file_event(self.bus.statechart))
        self.files_frame_treeview_menu.add_command(label='Remove File',
                                                   command=lambda: helpers.remove_file_event(self.bus.statechart,
                                                                                             self.files_frame_treeview.selection()[
                                                                                                 0]))

        self.figures_frame_treeview_menu = tkinter.Menu(tearoff=False)
        self.figures_frame_treeview_menu.add_command(label='Change Category',
                                                     command=lambda: self.show_popup_figure_category_rename())
        self.figures_frame_treeview_menu.add_command(label='Change Color', state='disabled')
        self.figures_frame_treeview_menu.add_separator()
        self.figures_frame_treeview_menu.add_command(label='Delete', command=lambda: self.send_figure_delete_event())

        self.files_frame_treeview.bind('<Button-1>', lambda _: self.files_frame_treeview_menu.unpost())
        self.files_frame_treeview.bind('<Button-3>', lambda _: self.show_files_frame_treeview_menu())

        self.figures_frame_treeview.bind('<Button-1>', lambda _: self.figures_frame_treeview_menu.unpost())
        self.figures_frame_treeview.bind('<Button-3>', lambda _: self.show_figures_frame_treeview_menu())

        self.root.bind('<Left>', lambda _: self.select_prev_image())
        self.root.bind('<Up>', lambda _: self.select_prev_image())
        self.root.bind('<Right>', lambda _: self.select_next_image())
        self.root.bind('<Down>', lambda _: self.select_next_image())

        self.root.config(menu=self.main_menu)

    def run(self) -> None:
        self.root.mainloop()

    def update_title(self, new_name: str) -> None:
        self.root.title(f'{new_name} | BOOBA' if new_name else 'BOOBA')

    def set_default_pointer(self) -> None:
        self.root.config(cursor='')

    def set_drawing_pointer(self) -> None:
        self.root.config(cursor='pencil')

    def set_grab_pointer(self) -> None:
        self.root.config(cursor='fleur')

    def set_remove_pointer(self) -> None:
        self.root.config(cursor='X_cursor')

    def set_add_pointer(self) -> None:
        self.root.config(cursor='plus')

    def add_file(self, id_, filedata) -> None:
        self.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

    def clear_files(self) -> None:
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children(''):
                self.files_frame_treeview.delete(item)

    def remove_file(self, file_id) -> None:
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children():
                if item == file_id:
                    self.files_frame_treeview.delete(item)

    def clear_image(self) -> None:
        if self.figures_frame_treeview.tag_has('#image'):
            for item in self.figures_frame_treeview.get_children(''):
                self.figures_frame_treeview.delete(item)

    def clear_figures(self) -> None:
        if self.figures_frame_treeview.tag_has('#figures'):
            for item in self.figures_frame_treeview.get_children(''):
                self.figures_frame_treeview.delete(item)

    def clear_canvas(self) -> None:
        if self.drawing_frame_canvas.gettags('#draw_figures'):
            self.drawing_frame_canvas.delete('#draw_figures')

    def bind_select_image_listener(self) -> None:
        self.files_frame_treeview.bind('<Double-Button-1>', lambda _: helpers.select_image_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))

    def unbind_select_image_listener(self) -> None:
        self.files_frame_treeview.unbind('<Double-Button-1>')

    def load_image_into_canvas(self, abs_path, transformations: typing.Optional[typing.List[str]] = None) -> None:
        self.clear_image()

        self.image_to_load_on_canvas = Image.open(abs_path)

        if transformations:
            for transform in transformations:
                if transform == 'rotate_cw':
                    self.image_to_load_on_canvas = self.image_to_load_on_canvas.rotate(angle=-90, expand=True)
                elif transform == 'rotate_ccw':
                    self.image_to_load_on_canvas = self.image_to_load_on_canvas.rotate(angle=90, expand=True)

        new_sizes = self._get_size_to_resize(
            i_w=self.image_to_load_on_canvas.width, i_h=self.image_to_load_on_canvas.height,
            c_w=self.drawing_frame_canvas.winfo_width(), c_h=self.drawing_frame_canvas.winfo_height()
        )
        self.image_to_load_on_canvas = self.image_to_load_on_canvas.resize(new_sizes, resample=Image.Resampling.NEAREST)
        self.image_on_canvas = ImageTk.PhotoImage(image=self.image_to_load_on_canvas)
        self.drawing_frame_canvas.create_image(
            self.drawing_frame_canvas.winfo_width() // 2,
            self.drawing_frame_canvas.winfo_height() // 2,
            image=self.image_on_canvas,
            tags=('#image',)
        )

    @staticmethod
    def _get_size_to_resize(i_w: int, i_h: int, c_w: int, c_h: int) -> typing.List[int]:
        result = [1, 1]

        if i_w / i_h >= 1:
            scale = c_w / i_w
            result = [i_w * scale, i_h * scale]
        else:
            scale = c_h / i_h
            result = [i_w * scale, i_h * scale]

        result = [helpers.clamp(0, c_w, result[0]), helpers.clamp(0, c_h, result[1])]

        return [int(pos) for pos in result]

    def enable_save_project_btn(self) -> None:
        self.save_project_btn['state'] = 'normal'

        if self.project_menu:
            self.project_menu.entryconfig('Save Project', state='normal')

    def disable_save_project_btn(self) -> None:
        self.save_project_btn['state'] = 'disabled'

        if self.project_menu:
            self.project_menu.entryconfig('Save Project', state='disabled')

    def enable_add_file_btn(self) -> None:
        self.add_file_btn['state'] = 'normal'

        if self.project_menu:
            self.project_menu.entryconfig('Add File', state='normal')

    def disable_add_file_btn(self) -> None:
        self.add_file_btn['state'] = 'disabled'

        if self.project_menu:
            self.project_menu.entryconfig('Add File', state='disabled')

    def enable_remove_file_btn(self) -> None:
        self.remove_file_btn['state'] = 'normal'

        if self.project_menu:
            self.project_menu.entryconfig('Remove File', state='normal')

    def disable_remove_file_btn(self) -> None:
        self.remove_file_btn['state'] = 'disabled'

        if self.project_menu:
            self.project_menu.entryconfig('Remove File', state='disabled')

    def enable_draw_buttons(self) -> None:
        self.draw_rectangle_btn['state'] = 'normal'
        self.draw_polygon_btn['state'] = 'normal'

        if self.figure_menu:
            self.figure_menu.entryconfig('Draw Rectangle', state='normal')
            self.figure_menu.entryconfig('Draw Polygon', state='normal')

    def disable_draw_buttons(self) -> None:
        self.draw_rectangle_btn['state'] = 'disabled'
        self.draw_polygon_btn['state'] = 'disabled'

        if self.figure_menu:
            self.figure_menu.entryconfig('Draw Rectangle', state='disabled')
            self.figure_menu.entryconfig('Draw Polygon', state='disabled')

    def enable_point_actions_buttons(self) -> None:
        self.add_point_btn['state'] = 'normal'
        self.remove_point_btn['state'] = 'normal'
        self.move_point_btn['state'] = 'normal'

        if self.figure_menu:
            self.figure_menu.entryconfig('Add Point', state='normal')
            self.figure_menu.entryconfig('Remove Point', state='normal')
            self.figure_menu.entryconfig('Move Point', state='normal')

    def disable_point_actions_buttons(self) -> None:
        self.add_point_btn['state'] = 'disabled'
        self.remove_point_btn['state'] = 'disabled'
        self.move_point_btn['state'] = 'disabled'

        if self.figure_menu:
            self.figure_menu.entryconfig('Add Point', state='disabled')
            self.figure_menu.entryconfig('Remove Point', state='disabled')
            self.figure_menu.entryconfig('Move Point', state='disabled')

    def enable_undo_action_button(self) -> None:
        self.undo_btn['state'] = 'normal'

        if self.figure_menu:
            self.figure_menu.entryconfig('Undo', state='normal')

    def disable_undo_action_button(self) -> None:
        self.undo_btn['state'] = 'disabled'

        if self.figure_menu:
            self.figure_menu.entryconfig('Undo', state='disabled')

    def bind_canvas_click_event(self) -> None:
        self.drawing_frame_canvas.bind('<Button-1>', lambda _e: helpers.click_canvas_event(self.bus.statechart, self.clamp_coords_in_image_area(_e.x, _e.y)))
        self.drawing_frame_canvas.bind('<Button-3>', lambda _e: helpers.right_click_canvas_event(self.bus.statechart))
        self.root.bind('<KeyPress-Escape>', lambda _e: helpers.reset_drawing_event(self.bus.statechart))

    def unbind_canvas_click_event(self) -> None:
        self.drawing_frame_canvas.unbind('<Button-1>')
        self.drawing_frame_canvas.unbind('<Button-3>')
        self.root.unbind('<KeyPress-Escape>')

    def bind_canvas_motion_rect_drawing_stage_1(self) -> None:
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_position_marker(*self.clamp_coords_in_image_area(_e.x, _e.y)))

    def unbind_canvas_motion_rect_drawing_stage_1(self) -> None:
        self.drawing_frame_canvas.unbind('<Motion>')

    def bind_canvas_motion_rect_drawing_stage_2(self) -> None:
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_rect_temp_figure(*self.clamp_coords_in_image_area(_e.x, _e.y)))

    def unbind_canvas_motion_rect_drawing_stage_2(self) -> None:
        self.drawing_frame_canvas.unbind('<Motion>')

    def redraw_drawing_position_marker(self, x, y) -> None:
        self.clear_mouse_position_marker()
        self.mouse_position_marker = self.drawing_frame_canvas.create_oval(
            x - 5, y - 5,
            x + 5, y + 5,
            outline='yellow', tags=('#draw_figures',))

    def clear_mouse_position_marker(self) -> None:
        if self.mouse_position_marker:
            self.drawing_frame_canvas.delete(self.mouse_position_marker)

    def redraw_drawing_rect_temp_figure(self, x, y) -> None:
        self.clear_drawing_rect_temp_figure()

        self.redraw_drawing_position_marker(x, y)
        self.drawing_rect_figure = self.drawing_frame_canvas.create_rectangle(
            self.drawing_rect_point_1[0], self.drawing_rect_point_1[1],
            x, y,
            outline='red', width=2,
            tags=('#draw_figures',))

    def clear_drawing_rect_temp_figure(self) -> None:
        if self.drawing_rect_figure:
            self.drawing_frame_canvas.delete(self.drawing_rect_figure)

    def draw_figure(self, file_id, figure_id, figure_data, highlight: bool = False, draggable: bool = False) -> None:
        figure = Figure(file_id, figure_id, figure_data, self.image_on_canvas, self.drawing_frame_canvas)
        figure.draw(highlight=highlight, draggable=draggable)

    def insert_figure_into_figures_list(self, file_id, figure_id, figure_data) -> None:
        values = (figure_data['category'], f'{file_id};{figure_id};{figure_data["category"]}')
        tags = ('#figures',)
        self.figures_frame_treeview.insert('', 'end', values=values, tags=tags)

    def bind_canvas_motion_poly_drawing(self) -> None:
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_poly_temp_figure(_e.x, _e.y))

    def unbind_canvas_motion_poly_drawing(self) -> None:
        self.drawing_frame_canvas.unbind('<Motion>')

    def clear_drawing_poly_temp_figure(self) -> None:
        if self.drawing_poly_figures:
            for figure in self.drawing_poly_figures:
                self.drawing_frame_canvas.delete(figure)
        self.drawing_poly_figures = []

    def redraw_drawing_poly_temp_figure(self, x, y) -> None:
        self.clear_drawing_poly_temp_figure()

        self.redraw_drawing_position_marker(x, y)

        temp_points = copy.copy(self.drawing_poly_points)
        if len(temp_points) >= 1:
            figure = self.drawing_frame_canvas.create_oval(temp_points[0][0] - 5, temp_points[0][1] - 5,
                                                           temp_points[0][0] + 5, temp_points[0][1] + 5,
                                                           outline='pink', width=5, tags=('#draw_figures',))
            self.drawing_poly_figures.append(figure)
        if len(temp_points) > 1:
            temp_points.append((x, y))
            figure = self.drawing_frame_canvas.create_polygon(temp_points, fill='green', outline='yellow', tags=('#draw_figures',))
            self.drawing_poly_figures.append(figure)

    def get_image_and_canvas_sizes(self) -> typing.Tuple[int, int, int, int]:
        return (self.image_on_canvas.width(), self.image_on_canvas.height(),
                self.drawing_frame_canvas.winfo_width(), self.drawing_frame_canvas.winfo_height())

    def clamp_coords_in_image_area(self, x, y) -> typing.Tuple[float, float]:
        i_w, i_h, c_w, c_h = self.get_image_and_canvas_sizes()
        clamped_x, clamped_y = helpers.clamp_coords_in_image_area(i_w=i_w, i_h=i_h, c_w=c_w, c_h=c_h, x=x, y=y)

        return clamped_x, clamped_y

    def from_canvas_to_image_coords(self, x, y) -> typing.Tuple[float, float]:
        i_w, i_h, c_w, c_h = self.get_image_and_canvas_sizes()
        clamped_x, clamped_y = helpers.clamp_coords_in_image_area(i_w=i_w, i_h=i_h, c_w=c_w, c_h=c_h, x=x, y=y)
        rel_x, rel_y = helpers.from_canvas_to_image_coords(i_w=i_w, i_h=i_h, c_w=c_w, c_h=c_h, x=clamped_x, y=clamped_y)

        return rel_x, rel_y

    def bind_figure_selection_event(self) -> None:
        self.figures_frame_treeview.bind('<<TreeviewSelect>>', lambda _: self.send_figure_selected_event())
        self.figures_frame_treeview.bind('<Double-Button-1>', lambda _: self.show_popup_figure_category_rename())

    def bind_figure_delete_event(self) -> None:
        self.figures_frame_treeview.bind('<KeyPress-Delete>', lambda _: self.send_figure_delete_event())

    def show_figures_frame_treeview_menu(self) -> None:
        if len(self.figures_frame_treeview.selection()) > 0:
            self.figures_frame_treeview_menu.post(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )

    def show_files_frame_treeview_menu(self) -> None:
        self.files_frame_treeview_menu.entryconfig('Remove File', state='normal')
        if len(self.files_frame_treeview.selection()) > 0:
            self.files_frame_treeview_menu.post(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
        else:
            self.files_frame_treeview_menu.post(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
            self.files_frame_treeview_menu.entryconfig('Remove File', state='disabled')

    def show_popup_figure_category_rename(self) -> None:
        if len(self.figures_frame_treeview.selection()) > 0:
            data = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values'][1].split(';')
            file_id, figure_id, category_name = data[0], int(data[1]), data[2]
            helpers.ask_for_category_name(self.bus.statechart, file_id, figure_id, default_val=category_name)

    def send_figure_delete_event(self) -> None:
        if len(self.figures_frame_treeview.selection()) > 0:
            values = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values']
            _, figure_id, _ = values[1].split(';')
            helpers.delete_figure_event(self.bus.statechart, int(figure_id))

    def send_figure_selected_event(self) -> None:
        if len(self.figures_frame_treeview.selection()) > 0:
            values = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values']
            _, figure_id, _ = values[1].split(';')
            helpers.figure_selected_event(self.bus.statechart, int(figure_id))

    def bind_point_move_click(self) -> None:
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self._find_closest_draggable_point(e.x, e.y))

    def unbind_point_move_click(self) -> None:
        self.drawing_frame_canvas.unbind('<Button-1>')

    def _find_closest_draggable_point(self, x, y) -> None:
        self.moving_figure_point = None
        figures = self.drawing_frame_canvas.find_closest(x, y, halo=10)
        for figure in figures:
            tags = self.drawing_frame_canvas.gettags(figure)
            for tag in tags:
                if tag.startswith('#grabbable-data='):
                    data = tag.lstrip('#grabbable-data=').split(';')
                    self.moving_figure_point = {
                        'figure_idx': int(data[1]),
                        'point_idx': int(data[2])
                    }
                    break

    def bind_point_move_motion_event(self) -> None:
        self.drawing_frame_canvas.bind('<B1-Motion>', lambda e: helpers.update_figures_point_position_event(self.bus.statechart, (e.x, e.y), self.moving_figure_point))

    def unbind_point_move_motion_event(self) -> None:
        self.drawing_frame_canvas.unbind('<B1-Motion>')

    def bind_point_remove_click(self) -> None:
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self.send_update_figure_remove_point_event(e.x, e.y))

    def unbind_point_remove_click(self) -> None:
        self.drawing_frame_canvas.unbind('<Button-1>')

    def send_update_figure_remove_point_event(self, x, y) -> None:
        self._find_closest_draggable_point(x, y)
        if self.moving_figure_point:
            helpers.update_figure_remove_point_event(self.bus.statechart, self.moving_figure_point)

    def bind_point_add_click(self) -> None:
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self._find_closest_insertable_line(e.x, e.y))

    def unbind_point_add_click(self) -> None:
        self.drawing_frame_canvas.unbind('<Button-1>')

    def _find_closest_insertable_line(self, x, y):
        self.moving_figure_point = None
        figures = self.drawing_frame_canvas.find_closest(x, y, halo=10)
        for figure in figures:
            tags = self.drawing_frame_canvas.gettags(figure)
            for tag in tags:
                if tag.startswith('#insertable-data='):
                    data = tag.lstrip('#insertable-data=').split(';')
                    insertable_line_data = {
                        'figure_idx': int(data[1]),
                        'point_idx': int(data[2])
                    }
                    helpers.update_figure_add_point_event(self.bus.statechart, (x, y), insertable_line_data)
                    break

    def select_prev_image(self) -> None:
        file_id = self._get_file_in_direction(direction=-1)
        if file_id:
            helpers.select_image_event(self.bus.statechart, file_id)

    def select_next_image(self) -> None:
        file_id = self._get_file_in_direction(direction=1)
        if file_id:
            helpers.select_image_event(self.bus.statechart, file_id)

    def _get_file_in_direction(self, direction: int) -> str:
        next_file_index = None
        next_file = None

        all_files = self.files_frame_treeview.get_children('')
        if all_files:
            if len(self.files_frame_treeview.selection()) > 0:
                current_file = self.files_frame_treeview.selection()[0]
                current_file_index = all_files.index(current_file)
                next_file_index = current_file_index + direction

                if direction < 0:
                    if current_file_index <= 0:
                        next_file_index = len(all_files) - 1
                elif direction > 0:
                    if current_file_index == len(all_files) - 1:
                        next_file_index = 0

                next_file = all_files[next_file_index]

        return next_file

    def set_files_selection(self, file_id: str) -> None:
        self.files_frame_treeview.selection_set([file_id])

    def show_help(self):
        popup = tkinter.Toplevel(self.root)
        popup.title('Help')

        help_info = '''
            '<Control-n>' create new project
            '<Control-o>' open project
            '<Control-s>' save project
            '<Control-i>' add file
            '<Control-r>' or '<KeyPress-1>' draw rectangle
            '<Control-p>' or '<KeyPress-2>' draw polygon
            '<KeyPress-a>' add new point to existing figure (works only for polygons)
            '<KeyPress-x>' remove point from existing figure (if point on rectangle then removes entire figure)
            '<KeyPress-g>' move point to another location
            '<Control-z>' undo last action only for current file
            '<Double-Left-Click>' on file item on files list select file as active
            '<Left-Click>' on figure item on figures list select figure on canvas
            '<Right-Click>' on figure item on figures list show context menu
            '<Left-Arrow>' or '<Up-Arrow>' select previous file
            '<Right-Arrow>' or '<Down-Arrow>' select next file 
        '''

        lbl = tkinter.Label(popup, text=help_info)
        lbl.grid(column=0, row=0, sticky='nesw')

        ok_btn = tkinter.Button(popup, text='OK', command=lambda: popup.destroy())
        ok_btn.grid(column=0, row=1, sticky='ns')

        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(0, weight=1)



class PlaceholderGui(Gui):
    def __init__(self, bus: CommonBus):
        self.bus = bus
        self.bus.register_item('gui', self)

    def run(self) -> None:
        pass

    def update_title(self, new_name: str) -> None:
        pass

    def set_default_pointer(self) -> None:
        pass

    def set_drawing_pointer(self) -> None:
        pass

    def set_grab_pointer(self) -> None:
        pass

    def set_remove_pointer(self) -> None:
        pass

    def set_add_pointer(self) -> None:
        pass

    def add_file(self, id_, filedata) -> None:
        pass

    def clear_files(self) -> None:
        pass

    def remove_file(self, file_id) -> None:
        pass

    def clear_image(self) -> None:
        pass

    def clear_figures(self) -> None:
        pass

    def clear_canvas(self) -> None:
        pass

    def bind_select_image_listener(self) -> None:
        pass

    def unbind_select_image_listener(self) -> None:
        pass

    def load_image_into_canvas(self, abs_path, transformations: typing.Optional[typing.List[str]] = None) -> None:
        pass

    def enable_save_project_btn(self) -> None:
        pass

    def disable_save_project_btn(self) -> None:
        pass

    def enable_add_file_btn(self) -> None:
        pass

    def disable_add_file_btn(self) -> None:
        pass

    def enable_remove_file_btn(self) -> None:
        pass

    def disable_remove_file_btn(self) -> None:
        pass

    def enable_draw_buttons(self) -> None:
        pass

    def disable_draw_buttons(self) -> None:
        pass

    def enable_point_actions_buttons(self) -> None:
        pass

    def disable_point_actions_buttons(self) -> None:
        pass

    def enable_undo_action_button(self) -> None:
        pass

    def disable_undo_action_button(self) -> None:
        pass

    def bind_canvas_click_event(self) -> None:
        pass

    def unbind_canvas_click_event(self) -> None:
        pass

    def bind_canvas_motion_rect_drawing_stage_1(self) -> None:
        pass

    def unbind_canvas_motion_rect_drawing_stage_1(self) -> None:
        pass

    def bind_canvas_motion_rect_drawing_stage_2(self) -> None:
        pass

    def unbind_canvas_motion_rect_drawing_stage_2(self) -> None:
        pass

    def redraw_drawing_position_marker(self, x, y) -> None:
        pass

    def clear_mouse_position_marker(self) -> None:
        pass

    def redraw_drawing_rect_temp_figure(self, x, y) -> None:
        pass

    def clear_drawing_rect_temp_figure(self) -> None:
        pass

    def draw_figure(self, file_id, figure_id, figure_data, highlight: bool = False, draggable: bool = False) -> None:
        pass

    def insert_figure_into_figures_list(self, file_id, figure_id, figure_data) -> None:
        pass

    def bind_canvas_motion_poly_drawing(self) -> None:
        pass

    def unbind_canvas_motion_poly_drawing(self) -> None:
        pass

    def clear_drawing_poly_temp_figure(self) -> None:
        pass

    def redraw_drawing_poly_temp_figure(self, x, y) -> None:
        pass

    def get_image_and_canvas_sizes(self) -> typing.Tuple[int, int, int, int]:
        return 0, 0, 1, 1

    def clamp_coords_in_image_area(self, x, y) -> typing.Tuple[float, float]:
        return 0.0, 0.0

    def from_canvas_to_image_coords(self, x, y) -> typing.Tuple[float, float]:
        return 0.0, 0.0

    def bind_figure_selection_event(self) -> None:
        pass

    def bind_figure_delete_event(self) -> None:
        pass

    def show_figures_frame_treeview_menu(self) -> None:
        pass

    def show_files_frame_treeview_menu(self) -> None:
        pass

    def show_popup_figure_category_rename(self) -> None:
        pass

    def send_figure_delete_event(self) -> None:
        pass

    def send_figure_selected_event(self) -> None:
        pass

    def bind_point_move_click(self) -> None:
        pass

    def unbind_point_move_click(self) -> None:
        pass

    def bind_point_move_motion_event(self) -> None:
        pass

    def unbind_point_move_motion_event(self) -> None:
        pass

    def bind_point_remove_click(self) -> None:
        pass

    def unbind_point_remove_click(self) -> None:
        pass

    def send_update_figure_remove_point_event(self, x, y) -> None:
        pass

    def bind_point_add_click(self) -> None:
        pass

    def unbind_point_add_click(self) -> None:
        pass

    def select_prev_image(self) -> None:
        pass

    def select_next_image(self) -> None:
        pass

    def set_files_selection(self, file_id: str) -> None:
        pass

    def show_help(self):
        pass