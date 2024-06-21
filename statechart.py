import copy
import uuid

from miros import ActiveObject
from miros import Event
from miros import return_status
from miros import signals
from miros import spy_on

from common_bus import CommonBus
import helpers
from project import Project




class Statechart(ActiveObject):
    def __init__(self, name: str, bus: CommonBus):
        super().__init__(name=name)

        self.bus = bus
        self.bus.register_item('statechart', self)

        self.project = None

        self.points = []

    def _redraw_canvas_and_figures(self, highlight_figure_id: int = None, draggable=False):
        selected_file_id, selected_file_data = self.project.get_selected_file()
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

        self.bus.gui.load_image_into_canvas(selected_file_data['abs_path'])
        for figure_id, figure_data in enumerate(selected_file_data['figures']):
            highlight = True if (highlight_figure_id is not None) and (highlight_figure_id == figure_id) else False
            self.bus.gui.draw_figure(selected_file_id, figure_id, figure_data, highlight=highlight, draggable=draggable)
            self.bus.gui.insert_figure_into_figures_list(selected_file_id, figure_id, figure_data)

    def run(self):
        self.start_at(no_project)

    def empty_project(self):
        self.project = Project()

    def load_project(self, abs_path):
        self.project = Project(abs_path)

    def on_no_project_entry(self):
        self.bus.gui.disable_save_project_btn()
        self.bus.gui.disable_add_file_btn()
        self.bus.gui.disable_remove_file_btn()
        self.bus.gui.disable_draw_buttons()

    def on_in_project_entry(self):
        self.bus.gui.enable_save_project_btn()
        self.bus.gui.enable_add_file_btn()
        if self.project.get_files():
            self.bus.gui.enable_remove_file_btn()

        self.bus.gui.clear_files()
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

        for file_id, filedata in self.project.get_files():
            self.bus.gui.add_file(file_id, filedata)

        selected_file_id, _ = self.project.get_selected_file()

        if self.project.get_files():
            if selected_file_id:
                helpers.select_image_event(self, selected_file_id)
            else:
                for file_id, filedata in self.project.get_files():
                    helpers.select_image_event(self, file_id)
                    break

        self.bus.gui.bind_select_image_listener()
        self.bus.gui.bind_figure_delete_event()
        self.bus.gui.bind_figure_selection_event()

    def on_in_project_exit(self):
        self.bus.gui.unbind_select_image_listener()
        self.bus.gui.clear_files()
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

    def on_in_project_add_file(self, files):
        selected_file_id, _ = self.project.get_selected_file()
        for abs_path in files:
            self.project.add_file(abs_path)

        self.bus.gui.clear_files()
        for file_id, file_data in self.project.get_files():
            self.bus.gui.add_file(file_id, file_data)

        self.bus.gui.enable_remove_file_btn()

        if selected_file_id:
            helpers.select_image_event(self, selected_file_id)
        else:
            for file_id, _ in self.project.get_files():
                helpers.select_image_event(self, file_id)
                break

    def on_in_project_select_image(self, file_id):
        self.project.select_file(file_id)
        file_id, file_data = self.project.get_selected_file()

        self._redraw_canvas_and_figures()

        self.bus.gui.enable_draw_buttons()

        self.bus.gui.files_frame_treeview.selection_set([file_id])
        helpers.reset_drawing_event(self)

    def on_in_project_figure_selected(self, selected_figure_id):
        self._redraw_canvas_and_figures(highlight_figure_id=selected_figure_id)

    def on_in_project_delete_figure(self, figure_id):
        if figure_id is not None:
            self.project.delete_figure(figure_id)

        self._redraw_canvas_and_figures()

    def on_in_project_save_project(self, abs_path):
        self.project.save_project(abs_path)

    def on_in_project_undo_history(self):
        selected_file_id, _ = self.project.get_selected_file()
        if self.project.history.has_history(selected_file_id):
            self.project.undo_history()
            self._redraw_canvas_and_figures()

    def on_in_project_remove_file(self, file_id):
        selected_file_id, selected_file_data = self.project.get_selected_file()

        self.bus.gui.remove_file(file_id)
        self.project.remove_file(file_id)

        keys, _ = [k for k, _ in self.project.get_files()]

        if file_id == selected_file_id:
            self.bus.gui.clear_figures()
            self.bus.gui.clear_canvas()
            if len(keys) > 0:
                helpers.select_image_event(self, keys[0])

        self.bus.gui.disable_draw_buttons()
        if len(keys) > 0:
            self.bus.gui.enable_remove_file_btn()
        else:
            self.bus.gui.disable_remove_file_btn()

    def on_in_project_set_figure_category(self, file_id, figure_id, category):
        self.project.update_figure_category(file_id, figure_id, category)

        selected_file_id, selected_file_data = self.project.get_selected_file()

        if file_id == selected_file_id:
            self._redraw_canvas_and_figures()

    def on_drawing_rect_entry(self):
        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_rect_drawing_stage_1()

        self.points = []

    def on_drawing_rect_exit(self):
        self.bus.gui.unbind_canvas_click_event()
        self.bus.gui.unbind_canvas_motion_rect_drawing_stage_1()

    def on_drawing_rect_reset_drawing(self):
        self.points = []

    def on_drawing_rect_click(self, point):
        self.points.append(point)

    def on_drawing_rect_waiting_for_2_point_entry(self):
        self.bus.gui.drawing_rect_point_1 = self.points[0]

        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_rect_drawing_stage_2()

    def on_drawing_rect_waiting_for_2_point_exit(self):
        self.bus.gui.unbind_canvas_motion_rect_drawing_stage_2()
        self.bus.gui.unbind_canvas_click_event()

        self.bus.gui.drawing_rect_point_1 = None

        self.points = []

    def on_drawing_rect_waiting_for_2_point_click(self, point):
        self.points.append(point)
        points = [self.bus.gui.from_canvas_to_image_coords(*point) for point in self.points]
        new_figure_id = self.project.add_rectangle(points=points, color=helpers.pick_random_color())
        self.points = []

        selected_file_id, _ = self.project.get_selected_file()
        helpers.ask_for_category_name(self, copy.copy(selected_file_id), new_figure_id)

        helpers.select_image_event(self, selected_file_id)

    def on_drawing_rect_waiting_for_2_point_reset_drawing(self):
        self.points = []
        selected_file_id, _ = self.project.get_selected_file()
        helpers.select_image_event(self, selected_file_id)

    def on_drawing_poly_entry(self):
        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_poly_drawing()
        self.points = []
        self.bus.gui.drawing_poly_points = []

    def on_drawing_poly_exit(self):
        self.bus.gui.unbind_canvas_click_event()
        self.bus.gui.unbind_canvas_motion_poly_drawing()

    def on_drawing_poly_reset_drawing(self):
        self.points = []
        self.bus.gui.drawing_poly_points = []

    def on_drawing_poly_click(self, point):
        self.points.append(point)

        self.bus.gui.drawing_poly_points.append(point)

        if len(self.points) >= 3:
            point_start = self.points[0]
            point_finish = self.points[-1]

            if abs(point_finish[0] - point_start[0]) <= 5 and abs(point_finish[1] - point_start[1]) <= 5:
                selected_file_id, _ = self.project.get_selected_file()
                self.points.pop()
                new_figure_id = self.project.add_polygon(
                    points=[self.bus.gui.from_canvas_to_image_coords(*point) for point in self.points],
                    color=helpers.pick_random_color()
                )

                helpers.ask_for_category_name(self, copy.copy(selected_file_id), new_figure_id)
                helpers.select_image_event(self, selected_file_id)

    def on_moving_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True)

        self.bus.gui.bind_point_move_click()
        self.bus.gui.bind_point_move_motion_event()

    def on_moving_point_exit(self):
        self._redraw_canvas_and_figures()

        self.bus.gui.unbind_point_move_click()
        self.bus.gui.unbind_point_move_motion_event()

    def on_moving_point_update_figure_point_position(self, figure_id, point_id, new_coords):
        selected_file_id, _ = self.project.get_selected_file()
        new_coords = self.bus.gui.from_canvas_to_image_coords(*new_coords)
        self.project.update_figure_point_position(selected_file_id, figure_id, point_id, new_coords)

        self._redraw_canvas_and_figures(draggable=True)

    def on_removing_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True)

        self.bus.gui.bind_point_remove_click()

    def on_removing_point_exit(self):
        self._redraw_canvas_and_figures()

        self.bus.gui.bind_point_remove_click()

    def on_removing_point_update_figure_remove_point(self, figure_id, point_id):
        selected_file_id, selected_file_data = self.project.get_selected_file()

        self.project.update_figure_remove_point(selected_file_id, figure_id, point_id)

        self._redraw_canvas_and_figures(draggable=True)

    def on_adding_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True)

        self.bus.gui.bind_point_add_click()

    def on_adding_point_exit(self):
        self._redraw_canvas_and_figures()

        self.bus.gui.unbind_point_add_click()

    def on_adding_point_update_figure_insert_point(self, figure_id, point_id, coords):
        selected_file_id, selected_file_data = self.project.get_selected_file()
        coords = self.bus.gui.from_canvas_to_image_coords(*coords)
        self.project.update_figure_insert_point(selected_file_id, figure_id, point_id, coords)

        self._redraw_canvas_and_figures(draggable=True)


@spy_on
def no_project(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_no_project_entry()
    elif e.signal == signals.NEW_PROJECT:
        status = c.trans(in_project)
        c.empty_project()
    elif e.signal == signals.LOAD_PROJECT:
        status = c.trans(in_project)
        c.load_project(e.payload)
    else:
        status = return_status.SUPER
        c.temp.fun = c.top

    return status


@spy_on
def in_project(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_in_project_entry()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_in_project_exit()
    elif e.signal == signals.UNDO_HISTORY:
        status = return_status.HANDLED
        c.on_in_project_undo_history()
    elif e.signal == signals.ADD_FILE:
        status = return_status.HANDLED
        c.on_in_project_add_file(e.payload)
    elif e.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED
        c.on_in_project_remove_file(e.payload)
    elif e.signal == signals.SELECT_IMAGE:
        status = return_status.HANDLED
        c.on_in_project_select_image(e.payload)
    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        abs_path = e.payload
        c.on_in_project_save_project(abs_path)
    elif e.signal == signals.DRAW_RECT:
        status = c.trans(drawing_rect)
    elif e.signal == signals.DRAW_POLY:
        status = c.trans(drawing_poly)
    elif e.signal == signals.ADD_POINT:
        status = c.trans(adding_point)
    elif e.signal == signals.REMOVE_POINT:
        status = c.trans(removing_point)
    elif e.signal == signals.MOVE_POINT:
        status = c.trans(moving_point)
    elif e.signal == signals.FIGURE_SELECTED:
        status = return_status.HANDLED
        selected_figure_id = e.payload
        c.on_in_project_figure_selected(selected_figure_id)
    elif e.signal == signals.DELETE_FIGURE:
        status = return_status.HANDLED
        figure_id = e.payload
        c.on_in_project_delete_figure(figure_id)
    elif e.signal == signals.SET_FIGURE_CATEGORY:
        status = return_status.HANDLED

        file_id = e.payload['file_id']
        figure_id = e.payload['figure_id']
        category = e.payload['category']

        c.on_in_project_set_figure_category(file_id, figure_id, category)
    else:
        status = return_status.SUPER
        c.temp.fun = no_project

    return status


@spy_on
def drawing_rect(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_rect_entry()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_rect_exit()
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)
        c.on_drawing_rect_reset_drawing()
    elif e.signal == signals.CLICK:
        status = c.trans(drawing_rect_waiting_for_2_point)
        c.on_drawing_rect_click(e.payload)
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def drawing_rect_waiting_for_2_point(c: Statechart, e: Event) -> return_status:
    status = return_status.HANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_rect_waiting_for_2_point_entry()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_rect_waiting_for_2_point_exit()
    if e.signal == signals.CLICK:
        status = c.trans(in_project)
        c.on_drawing_rect_waiting_for_2_point_click(e.payload)
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)
        c.on_drawing_rect_waiting_for_2_point_reset_drawing()
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def drawing_poly(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_poly_entry()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_drawing_poly_exit()
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)
        c.on_drawing_poly_reset_drawing()
    elif e.signal == signals.CLICK:
        status = return_status.HANDLED
        c.on_drawing_poly_click(e.payload)
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def moving_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_moving_point_entry()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_moving_point_exit()
    if e.signal == signals.UPDATE_FIGURE_POINT_POSITION:
        status = return_status.HANDLED
        c.on_moving_point_update_figure_point_position(e.payload['figure_idx'], e.payload['point_idx'], e.payload['coords'])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def removing_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_removing_point_entry()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_removing_point_exit()
    if e.signal == signals.UPDATE_FIGURE_REMOVE_POINT:
        status = return_status.HANDLED
        c.on_removing_point_update_figure_remove_point(e.payload['figure_idx'], e.payload['point_idx'])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def adding_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.on_adding_point_entry()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_adding_point_exit()
    if e.signal == signals.UPDATE_FIGURE_INSERT_POINT:
        status = return_status.HANDLED
        c.on_adding_point_update_figure_insert_point(e.payload['figure_idx'], e.payload['point_idx'], e.payload['coords'])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status
