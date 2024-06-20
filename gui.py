import copy
import tkinter
import typing
from tkinter import ttk

from PIL import ImageTk, Image

import helpers
from common_bus import CommonBus
from figure import Figure

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
        self.add_point_btn = tkinter.Button(self.command_palette, text='Add Point')
        self.remove_point_btn = tkinter.Button(self.command_palette, text='Remove Point')
        self.move_point_btn = tkinter.Button(self.command_palette, text='Move Point')
        self.undo_btn = tkinter.Button(self.command_palette, text='UNDO')

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

    def run(self):
        self.new_project_btn.configure(command=lambda: helpers.new_project_event(self.bus.statechart))
        self.load_project_btn.configure(command=lambda: helpers.load_project_event(self.bus.statechart))
        self.save_project_btn.configure(command=lambda: helpers.save_project_event(self.bus.statechart))
        self.add_file_btn.configure(command=lambda: helpers.add_file_event(self.bus.statechart))
        self.remove_file_btn.configure(command=lambda: helpers.remove_file_event(self.bus.statechart, self.files_frame_treeview.selection()[0]))
        self.draw_rectangle_btn.configure(command=lambda: helpers.draw_rect_event(self.bus.statechart))
        self.draw_polygon_btn.configure(command=lambda: helpers.draw_poly_event(self.bus.statechart))
        self.add_point_btn.configure(command=lambda: helpers.add_point_event(self.bus.statechart))
        self.remove_point_btn.configure(command=lambda: helpers.remove_point_event(self.bus.statechart))
        self.move_point_btn.configure(command=lambda: helpers.move_point_event(self.bus.statechart))
        self.undo_btn.configure(command=lambda: helpers.undo_event(self.bus.statechart))

        self.root.mainloop()

    def add_file(self, id_, filedata):
        self.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

    def clear_files(self):
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children(''):
                self.files_frame_treeview.delete(item)

    def remove_file(self, file_id):
        if self.files_frame_treeview.tag_has('#files'):
            for item in self.files_frame_treeview.get_children():
                if item == file_id:
                    self.files_frame_treeview.delete(item)

    def clear_figures(self):
        if self.figures_frame_treeview.tag_has('#figures'):
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
        self.image_to_load_on_canvas = Image.open(abs_path)
        new_sizes = self._get_size_to_resize(
            self.image_to_load_on_canvas.width, self.image_to_load_on_canvas.height,
            self.drawing_frame_canvas.winfo_width(), self.drawing_frame_canvas.winfo_height()
        )
        self.image_to_load_on_canvas = self.image_to_load_on_canvas.resize(new_sizes, resample=Image.Resampling.NEAREST)
        self.image_on_canvas = ImageTk.PhotoImage(image=self.image_to_load_on_canvas)
        self.drawing_frame_canvas.create_image(
            self.drawing_frame_canvas.winfo_width() // 2,
            self.drawing_frame_canvas.winfo_height() // 2,
            image=self.image_on_canvas,
            tags=('#draw_figures',)
        )

    def _get_size_to_resize(self, i_w: int, i_h: int, c_w: int, c_h: int) -> typing.List[int]:
        result = [1, 1]

        if i_w / i_h >= 1:
            scale = c_w // i_w
            result = [i_w * scale, i_h * scale]
        else:
            scale = c_h // i_h
            result = [i_w * scale, i_h * scale]

        result = [helpers.clamp(0, c_w, result[0]), helpers.clamp(0, c_h, result[1])]

        return result

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
        self.drawing_frame_canvas.bind('<Button-1>', lambda _e: helpers.click_canvas_event(self.bus.statechart, self.clamp_coords_in_image_area(_e.x, _e.y)))
        self.drawing_frame_canvas.bind('<Button-3>', lambda _e: helpers.reset_drawing_event(self.bus.statechart))
        self.root.bind('<KeyPress-Escape>', lambda _e: helpers.reset_drawing_event(self.bus.statechart))

    def unbind_canvas_click_event(self):
        self.drawing_frame_canvas.unbind('<Button-1>')
        self.drawing_frame_canvas.unbind('<Button-3>')
        self.root.unbind('<KeyPress-Escape>')

    def bind_canvas_motion_rect_drawing_stage_1(self):
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_position_marker(*self.clamp_coords_in_image_area(_e.x, _e.y)))

    def unbind_canvas_motion_rect_drawing_stage_1(self):
        self.drawing_frame_canvas.unbind('<Motion>')

    def bind_canvas_motion_rect_drawing_stage_2(self):
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_rect_temp_figure(*self.clamp_coords_in_image_area(_e.x, _e.y)))

    def unbind_canvas_motion_rect_drawing_stage_2(self):
        self.drawing_frame_canvas.unbind('<Motion>')

    def redraw_drawing_position_marker(self, x, y):
        self.clear_mouse_position_marker()
        self.mouse_position_marker = self.drawing_frame_canvas.create_oval(
            x - 5, y - 5,
            x + 5, y + 5,
            outline='yellow', tags=('#draw_figures',))

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

    def draw_figure(self, file_id, figure_id, figure_data, highlight_figure: bool = False, draggable: bool = False) -> None:
        f = Figure(file_id, figure_id, figure_data, self.image_on_canvas, self.drawing_frame_canvas)
        f.draw(highlight=highlight_figure, draggable=draggable)

    def insert_figure_into_figures_list(self, file_id, figure_id, figure_data):
        values = (figure_data['category'], f'{file_id};{figure_id};{figure_data["category"]}')
        tags = ('#figures',)
        self.figures_frame_treeview.insert('', 'end', values=values, tags=tags)

    def bind_canvas_motion_poly_drawing(self):
        self.drawing_frame_canvas.bind('<Motion>', lambda _e: self.redraw_drawing_poly_temp_figure(_e.x, _e.y))

    def unbind_canvas_motion_poly_drawing(self):
        self.drawing_frame_canvas.unbind('<Motion>')

    def clear_drawing_poly_temp_figure(self):
        if self.drawing_poly_figures:
            for f in self.drawing_poly_figures:
                self.drawing_frame_canvas.delete(f)
        self.drawing_poly_figures = []

    def redraw_drawing_poly_temp_figure(self, x, y):
        self.clear_drawing_poly_temp_figure()

        self.redraw_drawing_position_marker(x, y)

        temp_points = copy.copy(self.drawing_poly_points)
        if len(temp_points) >= 1:
            f = self.drawing_frame_canvas.create_oval(temp_points[0][0] - 5, temp_points[0][1] - 5,
                                                      temp_points[0][0] + 5, temp_points[0][1] + 5,
                                                      outline='pink', width=5, tags=('#draw_figures',))
            self.drawing_poly_figures.append(f)
        if len(temp_points) > 1:
            temp_points.append((x, y))
            f = self.drawing_frame_canvas.create_polygon(temp_points, fill='green', outline='yellow', tags=('#draw_figures',))
            self.drawing_poly_figures.append(f)

    def clamp_coords_in_image_area(self, x, y) -> (int, int):
        i_w, i_h = self.image_on_canvas.width(), self.image_on_canvas.height()
        c_w, c_h = self.drawing_frame_canvas.winfo_width(), self.drawing_frame_canvas.winfo_height()
        center_x, center_y = self.drawing_frame_canvas.winfo_width() / 2.0, self.drawing_frame_canvas.winfo_height() / 2.0
        min_x = center_x - self.image_on_canvas.width() / 2
        max_x = center_x + self.image_on_canvas.width() / 2
        min_y = center_y - self.image_on_canvas.height() / 2
        max_y = center_y + self.image_on_canvas.height() / 2

        clamped_x = helpers.clamp(min_x, max_x, x)
        clamped_y = helpers.clamp(min_y, max_y, y)

        return clamped_x, clamped_y

    def from_canvas_to_image_coords(self, x, y):
        clamped_x, clamped_y = self.clamp_coords_in_image_area(x, y)
        i_w, i_h = self.image_on_canvas.width(), self.image_on_canvas.height()
        center_x, center_y = self.drawing_frame_canvas.winfo_width() / 2.0, self.drawing_frame_canvas.winfo_height() / 2.0

        max_x = center_x + i_w / 2
        max_y = center_y + i_h / 2

        rel_x = 1.0 - (max_x - clamped_x) / i_w
        rel_y = 1.0 - (max_y - clamped_y) / i_h

        return rel_x, rel_y

    def from_image_to_canvas_coords(self, x, y):
        i_w, i_h = self.image_on_canvas.width(), self.image_on_canvas.height()
        center_x, center_y = self.drawing_frame_canvas.winfo_width() / 2.0, self.drawing_frame_canvas.winfo_height() / 2.0

        min_x = center_x - i_w / 2
        min_y = center_y - i_h / 2

        abs_x = min_x + (x * i_w)
        abs_y = min_y + (y * i_h)

        return abs_x, abs_y

    def bind_figure_selection_event(self):
        self.figures_frame_treeview.bind('<<TreeviewSelect>>', lambda _: self.send_figure_selected_event())
        self.figures_frame_treeview.bind('<Double-Button-1>', lambda _: self.show_popup_figure_category_rename())

    def bind_figure_delete_event(self):
        self.figures_frame_treeview.bind('<KeyPress-Delete>', lambda _: self.send_figure_delete_event())

    def show_popup_figure_category_rename(self):
        if len(self.figures_frame_treeview.selection()) > 0:
            data = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values'][2].split(';')
            print('DATA>>>>>', data, self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0]))
            file_id, figure_id, category_name = data[0], int(data[1]), data[2]
            helpers.ask_for_category_name(self.bus.statechart, file_id, figure_id, default_val=category_name)

    def send_figure_delete_event(self):
        if len(self.figures_frame_treeview.selection()) > 0:
            values = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values']
            _, figure_id, _ = values[1].split(';')
            helpers.delete_figure_event(self.bus.statechart, int(figure_id))

    def send_figure_selected_event(self):
        if len(self.figures_frame_treeview.selection()) > 0:
            values = self.figures_frame_treeview.item(self.figures_frame_treeview.selection()[0])['values']
            _, figure_id, _ = values[1].split(';')
            helpers.figure_selected_event(self.bus.statechart, int(figure_id))

    def bind_point_move_click(self):
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self._find_closest_draggable_point(e.x, e.y))

    def unbind_point_move_click(self):
        self.drawing_frame_canvas.unbind('<Button-1>')

    def _find_closest_draggable_point(self, x, y):
        self.moving_figure_point = None
        # figures = self.drawing_frame_canvas.find_enclosed(x - 15, y - 15, x + 15, y + 15)
        figures = self.drawing_frame_canvas.find_closest(x, y, halo=10)
        for f in figures:
            tags = self.drawing_frame_canvas.gettags(f)
            for t in tags:
                if t.startswith('#grabbable-data='):
                    data = t.lstrip('#grabbable-data=').split(',')
                    self.moving_figure_point = {
                        'figure_idx': int(data[0]),
                        'point_idx': int(data[1])
                    }
                    break

    def bind_point_move_motion_event(self):
        self.drawing_frame_canvas.bind('<B1-Motion>', lambda e: helpers.update_figures_point_position_event(self.bus.statechart, (e.x, e.y), self.moving_figure_point))

    def unbind_point_move_motion_event(self):
        self.drawing_frame_canvas.unbind('<B1-Motion>')

    def bind_point_remove_click(self):
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self.send_point_remove_remove_point_event(e.x, e.y))

    def unbind_point_remove_click(self):
        self.drawing_frame_canvas.unbind('<Button-1>')

    # TODO переименовать метод лол
    def send_point_remove_remove_point_event(self, x, y):
        self._find_closest_draggable_point(x, y)
        if self.moving_figure_point:
            helpers.update_figure_remove_point_event(self.bus.statechart, self.moving_figure_point)

    def bind_point_add_click(self):
        self.drawing_frame_canvas.bind('<Button-1>', lambda e: self._find_closest_insertable_line(e.x, e.y))

    def unbind_point_add_click(self):
        self.drawing_frame_canvas.unbind('<Button-1>')

    def _find_closest_insertable_line(self, x, y):
        self.moving_figure_point = None
        figures = self.drawing_frame_canvas.find_closest(x, y, halo=10)
        for f in figures:
            tags = self.drawing_frame_canvas.gettags(f)
            print('>>>>TAGS', tags)
            for t in tags:
                if t.startswith('#insertable-data='):
                    data = t.lstrip('#insertable-data=').split(',')
                    insertable_line_data = {
                        'figure_idx': int(data[0]),
                        'point_idx': int(data[1])
                    }
                    helpers.update_figure_add_point_event(self.bus.statechart, (x, y), insertable_line_data)
                    break

    def redraw_figures_as_polylines(self, figures: typing.List) -> None:

        for id_, f in enumerate(figures):
            if f['type'] == 'rect':
                points = [self.from_image_to_canvas_coords(*point) for point in f['points']]
                point_1 = points[0][0], points[0][1]
                point_2 = points[1][0], points[0][1]
                point_3 = points[1][0], points[1][1]
                point_4 = points[0][0], points[1][1]

                self.drawing_frame_canvas.create_line(point_1, point_2, width=3)
                self.drawing_frame_canvas.create_line(point_2, point_3, width=3)
                self.drawing_frame_canvas.create_line(point_3, point_4, width=3)
                self.drawing_frame_canvas.create_line(point_4, point_1, width=3)

                for p_id, p in enumerate(points):
                    gr_id = self.drawing_frame_canvas.create_oval(p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5, fill='pink', width=5, tags=('#draw_figures'))

            elif f['type'] == 'poly':
                points = [self.from_image_to_canvas_coords(*point) for point in f['points']]
                p_idx = 0
                while p_idx < len(points):
                    self.drawing_frame_canvas.create_line(points[p_idx - 1], points[p_idx], width=3, fill='red', tags=('#draw_figures', '#insertable', f'#insertable-data={id_},{p_idx}'))
                    p_idx += 1

                for p_id, p in enumerate(points):
                    gr_id = self.drawing_frame_canvas.create_oval(p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5, fill='pink', width=5, tags=('#draw_figures', '#grabbable', f'#grabbable-data={id_},{p_id}'))

    def redraw_figures_as_polylines(self, figures: typing.List) -> None:

        for id_, f in enumerate(figures):
            if f['type'] == 'rect':
                points = [self.from_image_to_canvas_coords(*point) for point in f['points']]
                point_1 = points[0][0], points[0][1]
                point_2 = points[1][0], points[0][1]
                point_3 = points[1][0], points[1][1]
                point_4 = points[0][0], points[1][1]

                self.drawing_frame_canvas.create_line(point_1, point_2, width=3)
                self.drawing_frame_canvas.create_line(point_2, point_3, width=3)
                self.drawing_frame_canvas.create_line(point_3, point_4, width=3)
                self.drawing_frame_canvas.create_line(point_4, point_1, width=3)

                for p_id, p in enumerate(points):
                    gr_id = self.drawing_frame_canvas.create_oval(p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5, fill='pink', width=5, tags=('#draw_figures'))

            elif f['type'] == 'poly':
                points = [self.from_image_to_canvas_coords(*point) for point in f['points']]
                p_idx = 0
                while p_idx < len(points):
                    self.drawing_frame_canvas.create_line(points[p_idx - 1], points[p_idx], width=3, fill='red', tags=('#draw_figures', '#insertable', f'#insertable-data={id_},{p_idx}'))
                    p_idx += 1

                for p_id, p in enumerate(points):
                    gr_id = self.drawing_frame_canvas.create_oval(p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5, fill='pink', width=5, tags=('#draw_figures', '#grabbable', f'#grabbable-data={id_},{p_id}'))