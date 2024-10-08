import copy
import tkinter
import typing
from tkinter import ttk

from PIL import ImageTk, Image

from image_label import helpers
from image_label.common_bus import CommonBus
from image_label.figure import Figure

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
        self.root.title('Simple Image Label 👀')
        self.root.attributes('-zoomed', True)
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.main_menu = None
        self.project_menu = None
        self.figure_menu = None
        self.files_frame_treeview_menu = None
        self.figures_frame_treeview_menu = None
        self.exporters_menu = None
        self.help_menu = None

        self.root.columnconfigure(0, weight=90)
        self.root.columnconfigure(1, weight=10)
        self.root.rowconfigure(0, weight=80)
        self.root.rowconfigure(1, weight=20)

        self.drawing_frame = tkinter.Frame(self.root)
        self.files_frame = tkinter.Frame(self.root)
        self.figures_frame = tkinter.Frame(self.root)

        self.drawing_frame.grid(column=0, row=0, sticky='nesw', rowspan=2)
        self.files_frame.grid(column=1, row=0, sticky='nesw')
        self.figures_frame.grid(column=1, row=1, sticky='nesw')

        # DRAWING
        self.drawing_frame.columnconfigure(0, weight=1)
        self.drawing_frame.rowconfigure(1, weight=1)

        self.drawing_frame_commands = tkinter.Frame(self.drawing_frame)
        self.drawing_frame_commands_draw_figure_commands = tkinter.Frame(self.drawing_frame_commands)
        self.draw_rectangle_btn = tkinter.Button(self.drawing_frame_commands_draw_figure_commands, text='Draw Rectangle')
        self.draw_polygon_btn = tkinter.Button(self.drawing_frame_commands_draw_figure_commands, text='Draw Polygon')

        self.drawing_frame_commands_point_manipulation_commands = tkinter.Frame(self.drawing_frame_commands, padx=10)
        self.add_point_btn = tkinter.Button(self.drawing_frame_commands_point_manipulation_commands, text='Add Point')
        self.remove_point_btn = tkinter.Button(self.drawing_frame_commands_point_manipulation_commands, text='Remove Point')
        self.move_point_btn = tkinter.Button(self.drawing_frame_commands_point_manipulation_commands, text='Move Point')

        self.drawing_frame_commands_image_rotation_commands = tkinter.Frame(self.drawing_frame_commands)
        self.rotate_ccw_btn = tkinter.Button(self.drawing_frame_commands_image_rotation_commands, text='Image Rotate Left')
        self.rotate_cw_btn = tkinter.Button(self.drawing_frame_commands_image_rotation_commands, text='Image Rotate Right')

        self.drawing_frame_canvas = tkinter.Canvas(self.drawing_frame)

        self.drawing_frame_commands.grid(column=0, row=0, sticky='nesw')
        self.drawing_frame_commands_draw_figure_commands.grid(column=0, row=0, sticky='nesw')
        self.drawing_frame_commands_point_manipulation_commands.grid(column=1, row=0, sticky='nesw')
        self.drawing_frame_commands_image_rotation_commands.grid(column=2, row=0, sticky='nesw')

        self.draw_rectangle_btn.grid(column=0, row=0, sticky='w')
        self.draw_polygon_btn.grid(column=1, row=0, sticky='w')

        self.add_point_btn.grid(column=0, row=0, sticky='w')
        self.remove_point_btn.grid(column=1, row=0, sticky='w')
        self.move_point_btn.grid(column=2, row=0, sticky='w')
        self.rotate_ccw_btn.grid(column=0, row=0, sticky='w')
        self.rotate_cw_btn.grid(column=1, row=0, sticky='w')

        self.drawing_frame_canvas.grid(column=0, row=1, sticky='nesw')
        # END DRAWING

        # FILES
        self.files_frame.columnconfigure(0, weight=1)
        self.files_frame.columnconfigure(1, weight=1)
        self.files_frame.rowconfigure(1, weight=1)

        self.add_file_btn = tkinter.Button(self.files_frame, text='Add File')
        self.remove_file_btn = tkinter.Button(self.files_frame, text='Remove File')
        self.files_frame_treeview = ttk.Treeview(self.files_frame,
                                                 columns=['filename'],
                                                 selectmode='browse',
                                                 show='headings')
        self.files_frame_treeview.heading('filename', text='Filename')

        self.add_file_btn.grid(column=0, row=0)
        self.remove_file_btn.grid(column=1, row=0)
        self.files_frame_treeview.grid(column=0, row=1, sticky='nesw', columnspan=2)
        self.files_frame_treeview_scrollbar = ttk.Scrollbar(self.files_frame, orient='vertical')
        self.files_frame_treeview_scrollbar.grid(column=2, row=1, sticky='nesw')
        self.files_frame_treeview.config(yscrollcommand=self.files_frame_treeview_scrollbar.set)
        self.files_frame_treeview_scrollbar.config(command=self.files_frame_treeview.yview)
        # END FILES

        self.figures_frame_treeview = ttk.Treeview(self.figures_frame,
                                                   columns=['figure', 'id'],
                                                   selectmode='browse',
                                                   show='headings',
                                                   displaycolumns=('figure',))
        self.figures_frame_treeview.heading('figure', text='Figure')

        self.figures_frame.columnconfigure(0, weight=1)
        self.figures_frame.rowconfigure(0, weight=1)
        self.figures_frame_treeview.grid(column=0, row=0, sticky='nesw')
        self.figures_frame_treeview_scrollbar = ttk.Scrollbar(self.figures_frame, orient='vertical')
        self.figures_frame_treeview_scrollbar.grid(column=1, row=0, sticky='nesw')
        self.figures_frame_treeview.config(yscrollcommand=self.figures_frame_treeview_scrollbar.set)
        self.figures_frame_treeview_scrollbar.config(command=self.figures_frame_treeview.yview)

        self.init_bindings()

    def init_bindings(self):
        self.add_file_btn.configure(command=lambda: helpers.add_file_event(self.bus.statechart))
        self.remove_file_btn.configure(
            command=lambda: helpers.remove_file_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))

        self.draw_rectangle_btn.configure(command=lambda: helpers.draw_rect_event(self.bus.statechart))
        self.draw_polygon_btn.configure(command=lambda: helpers.draw_poly_event(self.bus.statechart))
        self.add_point_btn.configure(command=lambda: helpers.add_point_event(self.bus.statechart))
        self.remove_point_btn.configure(command=lambda: helpers.remove_point_event(self.bus.statechart))
        self.move_point_btn.configure(command=lambda: helpers.move_point_event(self.bus.statechart))
        self.rotate_ccw_btn.configure(command=lambda: helpers.rotate_ccw_event(self.bus.statechart))
        self.rotate_cw_btn.configure(command=lambda: helpers.rotate_cw_event(self.bus.statechart))

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

        self.root.bind('<F1>', lambda _: self.show_help())

        self.main_menu = tkinter.Menu(borderwidth=0)
        self.project_menu = tkinter.Menu(tearoff=False)
        self.figure_menu = tkinter.Menu(tearoff=False)
        self.exporters_menu = tkinter.Menu(tearoff=False)
        self.help_menu = tkinter.Menu(tearoff=False)

        if self.bus.exporters:
            for k, v in self.bus.exporters.items():
                self.exporters_menu.add_command(label=k, command=lambda: v.show_options(), state='disabled')

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

        self.project_menu.add_command(label='Quick Categories',
                                      command=lambda: self.show_quick_categories_settings(),
                                      state='normal')

        self.project_menu.add_separator()
        self.project_menu.add_command(label='Quit',
                                      command=lambda: helpers.quit_event(self.bus.statechart))

        self.figure_menu.add_command(label='Rotate CW (Right)',
                                     command=lambda: helpers.rotate_cw_event(self.bus.statechart),
                                     accelerator='<e>',
                                     state='disabled')
        self.figure_menu.add_command(label='Rotate CCW (Left)',
                                     command=lambda: helpers.rotate_ccw_event(self.bus.statechart),
                                     accelerator='<q>',
                                     state='disabled')
        self.figure_menu.add_separator()

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
        self.root.bind('<a>', lambda _: self.select_prev_image())
        self.root.bind('<d>', lambda _: self.select_next_image())
        self.root.bind('<Right>', lambda _: self.select_next_image())
        self.root.bind('<Down>', lambda _: self.select_next_image())

        self.root.bind('<q>', lambda _: helpers.rotate_ccw_event(self.bus.statechart))
        self.root.bind('<e>', lambda _: helpers.rotate_ccw_event(self.bus.statechart))

        self.root.config(menu=self.main_menu)

    def run(self) -> None:
        self.root.mainloop()

    def update_title(self, new_name: str) -> None:
        self.root.title(f'{new_name} | Simple Image Label 👀' if new_name else 'Simple Image Label 👀')

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
        if self.project_menu:
            self.project_menu.entryconfig('Save Project', state='normal')

    def disable_save_project_btn(self) -> None:
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

    def enable_rotate_buttons(self) -> None:
        self.rotate_cw_btn['state'] = 'normal'
        self.rotate_ccw_btn['state'] = 'normal'

        if self.figure_menu:
            self.figure_menu.entryconfig('Rotate CW (Right)', state='normal')
            self.figure_menu.entryconfig('Rotate CCW (Left)', state='normal')

    def disable_rotate_buttons(self) -> None:
        self.rotate_cw_btn['state'] = 'disabled'
        self.rotate_ccw_btn['state'] = 'disabled'

        if self.figure_menu:
            self.figure_menu.entryconfig('Rotate CW (Right)', state='disabled')
            self.figure_menu.entryconfig('Rotate CCW (Left)', state='disabled')

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
        if self.figure_menu:
            self.figure_menu.entryconfig('Undo', state='normal')

    def disable_undo_action_button(self) -> None:
        if self.figure_menu:
            self.figure_menu.entryconfig('Undo', state='disabled')

    def enable_quick_categories_settings_button(self) -> None:
        if self.project_menu:
            self.project_menu.entryconfig('Quick Categories', state='normal')

    def disable_quick_categories_settings_button(self) -> None:
        if self.project_menu:
            self.project_menu.entryconfig('Quick Categories', state='disabled')

    def enable_exporters(self) -> None:
        if self.exporters_menu:
            for entry_idx in range(self.exporters_menu.index('end') + 1):
                self.exporters_menu.entryconfig(entry_idx, state='normal')

    def disable_exporters(self) -> None:
        if self.project_menu:
            for entry_idx in range(self.exporters_menu.index('end') + 1):
                self.exporters_menu.entryconfig(entry_idx, state='disabled')

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
        popup.resizable(False, False)

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
'<KeyPress-q>' rotate CCW (Left)
'<KeyPress-e>' rotate CW (Right) 
        '''

        title_text = 'Simple Image Label (https://github.com/vkalyvayut-roboty-a-ne-chelovek/image-label)'
        title = tkinter.Label(popup, text=title_text, justify='center', pady=10)
        title.grid(column=0, row=0, sticky='nesw')

        lbl = tkinter.Label(popup, text=help_info, justify='left', padx=20)
        lbl.grid(column=0, row=1, sticky='nesw')

        ok_btn = tkinter.Button(popup, text='OK', command=lambda: popup.destroy())
        ok_btn.grid(column=0, row=2, sticky='ns')

        popup.grab_set()

        popup.bind('<Escape>', lambda _: popup.destroy())

    def show_quick_categories_settings(self):
        w = tkinter.Toplevel(self.root)
        w.title('Quick Categories')
        w.resizable(False, False)

        w.rowconfigure(0, weight=1)
        w.rowconfigure(1, weight=1)
        w.columnconfigure(0, weight=1)

        container = tkinter.Frame(w)
        container.grid(column=0, row=1, sticky='nesw')
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        categories = {}

        def add_new_category_action(category_name: typing.Optional[str] = None):
            cat_idxs = list(categories.keys())
            cat_idx = (cat_idxs[-1] + 1) if len(cat_idxs) > 0 else 0
            cat = tkinter.Frame(container)
            cat.grid(column=0, row=cat_idx, sticky='ew')
            cat.rowconfigure(0, weight=1)
            cat.columnconfigure(0, weight=1)

            input_var = tkinter.StringVar(value=category_name)
            input_ = tkinter.Entry(cat, textvariable=input_var)

            input_.grid(column=0, row=0, sticky='nesw')

            def delete_category():
                cat_data = categories.pop(cat_idx)
                cat_data['container'].destroy()

            del_btn = tkinter.Button(cat, text='-', command=delete_category)
            del_btn.grid(column=1, row=0)

            categories[cat_idx] = {
                'container': cat,
                'var': input_var
            }

        def update_quick_categories_action():
            new_categories = [copy.copy(cat['var'].get()) for cat in categories.values()]
            helpers.update_quick_categories(self.bus.statechart, new_categories)
            w.destroy()

        add_new_category_btn = tkinter.Button(w, text='+', command=add_new_category_action)
        add_new_category_btn.grid(column=0, row=0, sticky='nesw')

        save_btn = tkinter.Button(w, text='Update Quick Categories', command=update_quick_categories_action)
        save_btn.grid(column=0, row=2, sticky='ew')

        existing_categories = self.bus.statechart.project.get_quick_categories()
        if existing_categories:
            for cat in existing_categories:
                add_new_category_action(cat)

        w.grab_set()

    def reset_temp_drawing(self):
        self.drawing_poly_points = []

    def append_temp_poly_drawing_point(self, point):
        self.drawing_poly_points.append(point)

    def reset_temp_rect_drawing(self):
        self.drawing_rect_point_1 = None

    def set_temp_rect_drawing_point(self, point):
        self.drawing_rect_point_1 = point


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

    def enable_rotate_buttons(self) -> None:
        pass

    def disable_rotate_buttons(self) -> None:
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

    def enable_quick_categories_settings_button(self) -> None:
        pass

    def disable_quick_categories_settings_button(self) -> None:
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

    def show_quick_categories_settings(self):
        pass
