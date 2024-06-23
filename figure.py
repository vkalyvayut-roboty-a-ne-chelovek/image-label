from tkinter import Canvas
from PIL import ImageTk
from helpers import from_image_to_canvas_coords


class Figure:
    def __init__(self, file_id, figure_id, figure_data, image_on_canvas: ImageTk, canvas: Canvas):
        self.file_id = file_id
        self.figure_id = figure_id
        self.figure_data = figure_data
        self.image_on_canvas = image_on_canvas
        self.canvas = canvas

        self._points = self._convert_coords()

    def _convert_coords(self):
        i_w, i_h = self.image_on_canvas.width(), self.image_on_canvas.height()
        c_w, c_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        return [from_image_to_canvas_coords(i_w, i_h, c_w, c_h, *point) for point in self.figure_data['points']]

    def _make_figure_style(self, as_line=False):
        color = self.figure_data['color'] if 'color' in self.figure_data else 'red'
        if as_line:
            return {
                'fill': color,
                'width': 3
            }
        else:
            return {
                'fill': color,
                'outline': color,
                'width': 3
            }

    def draw(self, highlight=False, draggable=False):
        if self.figure_data['type'] == 'rect':
            if highlight:
                self._draw_rect_figure()
            else:
                self._draw_rect_as_polylines()
        elif self.figure_data['type'] == 'poly':
            if highlight:
                self._draw_poly_figure()
            else:
                self._draw_poly_as_polylines()

        if draggable:
            for point_id, point_data in enumerate(self._points):
                tags = ('#draw_figures', '#grabbable', f'#grabbable-data={self.file_id};{self.figure_id};{point_id}')
                self.canvas.create_oval(point_data[0] - 5, point_data[1] - 5,
                                        point_data[0] + 5, point_data[1] + 5,
                                        fill='pink', width=5,
                                        tags=tags)

    def _draw_rect_figure(self):
        tags = ('#draw_figures',)
        self.canvas.create_rectangle(self._points[0][0], self._points[0][1],
                                     self._points[1][0], self._points[1][1],
                                     tags=tags, **self._make_figure_style())

    def _draw_rect_as_polylines(self):
        tags = ('#draw_figures',)
        style = self._make_figure_style(as_line=True)
        point_1 = self._points[0][0], self._points[0][1]
        point_2 = self._points[1][0], self._points[0][1]
        point_3 = self._points[1][0], self._points[1][1]
        point_4 = self._points[0][0], self._points[1][1]

        self.canvas.create_line(point_1, point_2, tags=tags, **style)
        self.canvas.create_line(point_2, point_3, tags=tags, **style)
        self.canvas.create_line(point_3, point_4, tags=tags, **style)
        self.canvas.create_line(point_4, point_1, tags=tags, **style)

    def _draw_poly_figure(self):
        tags = ('#draw_figures',)
        self.canvas.create_polygon(self._points, tags=tags, **self._make_figure_style())

    def _draw_poly_as_polylines(self):
        style = self._make_figure_style(as_line=True)
        p_idx = 0
        while p_idx < len(self._points):
            tags = ('#draw_figures', '#insertable', f'#insertable-data={self.file_id};{self.figure_id};{p_idx}')
            self.canvas.create_line(self._points[p_idx - 1], self._points[p_idx], tags=tags, **style)
            p_idx += 1
