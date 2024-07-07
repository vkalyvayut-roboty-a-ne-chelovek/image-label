import copy
import typing

from miros import ActiveObject
from miros import Event
from miros import return_status
from miros import signals
from miros import spy_on

from src.common_bus import CommonBus
from src import helpers
from src.project import Project


class Statechart(ActiveObject):
    def __init__(self, name: str, bus: CommonBus):
        super().__init__(name=name)

        self.bus = bus
        self.bus.register_item('statechart', self)

        self.project = None

        self.points = []

    def _redraw_canvas_and_figures(self, highlight_figure_id: int = None, draggable: bool = False,
                                   update_figure_list: bool = True, update_image: bool = False):
        selected_file_id, selected_file_data = self.project.get_selected_file()
        if update_figure_list:
            self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

        if update_image:
            self.bus.gui.load_image_into_canvas(selected_file_data['abs_path'], selected_file_data['transformations'])

        for figure_id, figure_data in enumerate(selected_file_data['figures']):
            highlight = bool((highlight_figure_id is not None) and (highlight_figure_id == figure_id))
            self.bus.gui.draw_figure(selected_file_id, figure_id, figure_data, highlight=highlight, draggable=draggable)
            if update_figure_list:
                self.bus.gui.insert_figure_into_figures_list(selected_file_id, figure_id, figure_data)

    def ask_category_name(self, file_id, figure_id):
        categories = self.project.get_all_categories()
        default_category = categories[0] if len(categories) > 0 else ''

        if self.project.get_quick_categories() is not None:
            helpers.ask_for_quick_category_name(self, copy.copy(file_id), figure_id,
                                                quick_categories=self.project.get_quick_categories())
        else:
            helpers.ask_for_category_name(self,
                                          copy.copy(file_id),
                                          figure_id,
                                          default_val=default_category,
                                          values=categories)

    def check_if_there_are_any_undo_actions_available_and_then_change_state_of_the_undo_button(self):
        check_result = False
        if self.project:
            selected_file_id, _ = self.project.get_selected_file()
            check_result = True if selected_file_id and self.project.history.has_history(selected_file_id) else False

        if check_result:
            self.bus.gui.enable_undo_action_button()
        else:
            self.bus.gui.disable_undo_action_button()

    def check_if_there_are_any_changes_made_in_project(self):
        result = False

        if self.project:
            for file_id, _ in self.project.get_files():
                if self.project.history.has_history(file_id) and self.project.history.get_history_len(file_id) > 0:
                    result = True
                    break

        return result

    def run(self):
        self.start_at(no_project)

    def empty_project(self):
        self.project = Project()

    def load_project(self, abs_path):
        self.project = Project(abs_path)
        self.bus.gui.update_title(self.project.get_project_name())

    def on_no_project_entry(self):
        self.bus.gui.disable_save_project_btn()
        self.bus.gui.disable_add_file_btn()
        self.bus.gui.disable_remove_file_btn()
        self.bus.gui.disable_rotate_buttons()
        self.bus.gui.disable_draw_buttons()
        self.bus.gui.disable_point_actions_buttons()
        self.check_if_there_are_any_undo_actions_available_and_then_change_state_of_the_undo_button()
        self.bus.gui.disable_quick_categories_settings_button()

    def on_in_project_entry(self):
        self.bus.gui.enable_save_project_btn()
        self.bus.gui.enable_add_file_btn()
        self.bus.gui.enable_quick_categories_settings_button()

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

        helpers.init_temp_save_event(self)

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
            for file_id, _ in reversed(self.project.get_files()):
                helpers.select_image_event(self, file_id)
                break

    def on_in_project_select_image(self, file_id):
        self.project.select_file(file_id)
        file_id, _ = self.project.get_selected_file()

        self._redraw_canvas_and_figures(update_image=True)

        self.bus.gui.enable_draw_buttons()

        self.bus.gui.enable_rotate_buttons()

        self.bus.gui.enable_point_actions_buttons()

        self.check_if_there_are_any_undo_actions_available_and_then_change_state_of_the_undo_button()

        self.bus.gui.set_files_selection(file_id)
        helpers.reset_drawing_event(self)

        self.bus.gui.set_default_pointer()

    def on_in_project_figure_selected(self, selected_figure_id):
        self._redraw_canvas_and_figures(highlight_figure_id=selected_figure_id, update_figure_list=False)

    def on_in_project_delete_figure(self, figure_id):
        if figure_id is not None:
            self.project.delete_figure(figure_id)

        self._redraw_canvas_and_figures()

    def on_in_project_save_project(self, abs_path):
        self.project.save_project(abs_path)
        self.bus.gui.update_title(self.project.get_project_name())

    def on_in_project_undo_history(self):
        selected_file_id, _ = self.project.get_selected_file()
        if self.project.history.has_history(selected_file_id):
            self.project.undo_history()
            self._redraw_canvas_and_figures()

        self.check_if_there_are_any_undo_actions_available_and_then_change_state_of_the_undo_button()

    def on_in_project_remove_file(self, file_id):
        selected_file_id, _ = self.project.get_selected_file()

        self.bus.gui.remove_file(file_id)
        self.project.remove_file(file_id)

        files = self.project.get_files()

        if file_id == selected_file_id:
            self.bus.gui.clear_figures()
            self.bus.gui.clear_canvas()
            if len(files) > 0:
                helpers.select_image_event(self, files[-1][0])

        self.bus.gui.disable_rotate_buttons()
        self.bus.gui.disable_draw_buttons()
        if len(files) > 0:
            self.bus.gui.enable_remove_file_btn()
        else:
            self.bus.gui.disable_remove_file_btn()

    def on_in_project_set_figure_category(self, file_id, figure_id, category):
        self.project.update_figure_category(file_id, figure_id, category)

        selected_file_id, _ = self.project.get_selected_file()

        if file_id == selected_file_id:
            self._redraw_canvas_and_figures()

    def on_in_project_update_quick_categories(self, new_categories: typing.Optional[typing.List[str]]) -> None:
        self.project.set_quick_categories(new_categories)

    def on_drawing_rect_entry(self):
        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_rect_drawing_stage_1()

        self.bus.gui.set_drawing_pointer()

        self.points = []

    def on_drawing_rect_exit(self):
        self.bus.gui.unbind_canvas_click_event()
        self.bus.gui.unbind_canvas_motion_rect_drawing_stage_1()

        self.bus.gui.set_default_pointer()

    def on_drawing_rect_reset_drawing(self):
        self.points = []
        self._redraw_canvas_and_figures()

    def on_drawing_rect_click(self, point):
        self.points.append(point)

    def on_drawing_rect_waiting_for_2_point_entry(self):
        # TODO переписать в метод
        self.bus.gui.drawing_rect_point_1 = self.points[0]

        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_rect_drawing_stage_2()

        self.bus.gui.set_drawing_pointer()

    def on_drawing_rect_waiting_for_2_point_exit(self):
        self.bus.gui.unbind_canvas_motion_rect_drawing_stage_2()
        self.bus.gui.unbind_canvas_click_event()

        self.bus.gui.set_default_pointer()

        # TODO переписать в метод
        self.bus.gui.drawing_rect_point_1 = None

        self.points = []

    def on_drawing_rect_waiting_for_2_point_click(self, point):
        self.points.append(point)

        # TODO переписать в метод
        points = [self.bus.gui.from_canvas_to_image_coords(*point) for point in self.points]
        new_figure_id = self.project.add_rectangle(points=points, color=helpers.pick_random_color())
        self.points = []

        selected_file_id, _ = self.project.get_selected_file()

        self.ask_category_name(selected_file_id, new_figure_id)

        self._redraw_canvas_and_figures()

    def on_drawing_rect_waiting_for_2_point_reset_drawing(self):
        self.points = []
        selected_file_id, _ = self.project.get_selected_file()
        self._redraw_canvas_and_figures()

    def on_drawing_poly_entry(self):
        self.bus.gui.bind_canvas_click_event()
        self.bus.gui.bind_canvas_motion_poly_drawing()
        self.points = []
        self.bus.gui.drawing_poly_points = []

        self.bus.gui.set_drawing_pointer()

    def on_drawing_poly_exit(self):
        self.bus.gui.unbind_canvas_click_event()
        self.bus.gui.unbind_canvas_motion_poly_drawing()

        self.bus.gui.set_default_pointer()

    def on_drawing_poly_reset_drawing(self):
        self.points = []

        # TODO переписать в метод
        self.bus.gui.drawing_poly_points = []

        self._redraw_canvas_and_figures()

    def on_drawing_poly_click(self, point):
        self.points.append(point)

        # TODO переписать в метод
        self.bus.gui.drawing_poly_points.append(point)

    def on_drawing_poly_click_check_if_have_to_finish_drawing(self) -> bool:
        result = False

        if len(self.points) > 3:
            point_start = self.points[0]
            point_finish = self.points[-1]

            if abs(point_finish[0] - point_start[0]) <= 5 and abs(point_finish[1] - point_start[1]) <= 5:
                result = True

        return result

    def on_drawing_poly_finish_drawing(self):
        self.points.pop()
        self.save_current_polygon_as_is()

    def save_current_polygon_as_is(self):
        selected_file_id, _ = self.project.get_selected_file()

        # TODO переписать в метод
        new_figure_id = self.project.add_polygon(
            points=[self.bus.gui.from_canvas_to_image_coords(*point) for point in self.points],
            color=helpers.pick_random_color()
        )

        self.ask_category_name(selected_file_id, new_figure_id)
        self._redraw_canvas_and_figures()

    def on_moving_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True, update_figure_list=False)

        self.bus.gui.bind_point_move_click()
        self.bus.gui.bind_point_move_motion_event()

        self.bus.gui.set_grab_pointer()

    def on_moving_point_exit(self):
        self._redraw_canvas_and_figures(update_figure_list=False)

        self.bus.gui.unbind_point_move_click()
        self.bus.gui.unbind_point_move_motion_event()

        self.bus.gui.set_default_pointer()

    def on_moving_point_update_figure_point_position(self, figure_id, point_id, new_coords):
        selected_file_id, _ = self.project.get_selected_file()

        # TODO переписать в метод
        new_coords = self.bus.gui.from_canvas_to_image_coords(*new_coords)
        self.project.update_figure_point_position(selected_file_id, figure_id, point_id, new_coords)

        self._redraw_canvas_and_figures(draggable=True, update_figure_list=False)

    def on_removing_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True)

        self.bus.gui.bind_point_remove_click()

        self.bus.gui.set_remove_pointer()

    def on_removing_point_exit(self):
        self._redraw_canvas_and_figures()

        self.bus.gui.unbind_point_remove_click()

        self.bus.gui.set_default_pointer()

    def on_removing_point_update_figure_remove_point(self, figure_id, point_id):
        selected_file_id, _ = self.project.get_selected_file()

        self.project.update_figure_remove_point(selected_file_id, figure_id, point_id)

        self._redraw_canvas_and_figures(draggable=True)

    def on_adding_point_entry(self):
        self._redraw_canvas_and_figures(draggable=True)

        self.bus.gui.bind_point_add_click()

        self.bus.gui.set_add_pointer()

    def on_adding_point_exit(self):
        self._redraw_canvas_and_figures()

        self.bus.gui.unbind_point_add_click()

        self.bus.gui.set_default_pointer()

    def on_adding_point_update_figure_insert_point(self, figure_id, point_id, coords):
        selected_file_id, _ = self.project.get_selected_file()

        # TODO переписать в метод
        new_coords = self.bus.gui.from_canvas_to_image_coords(*coords)
        self.project.update_figure_insert_point(selected_file_id, figure_id, point_id, new_coords)

        self._redraw_canvas_and_figures(draggable=True)

    def on_in_project_save_temp(self):
        self.project.temp_save()
        helpers.init_temp_save_event(self)

    def on_in_project_rotate_cw(self):
        selected_file_id, _ = self.project.get_selected_file()
        self.project.rotate_cw(selected_file_id)

        self._redraw_canvas_and_figures(
            update_image=True,
            update_figure_list=False)

    def on_in_project_rotate_ccw(self):
        selected_file_id, _ = self.project.get_selected_file()
        self.project.rotate_ccw(selected_file_id)

        self._redraw_canvas_and_figures(
            update_image=True,
            update_figure_list=False)


@spy_on
def no_project(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_no_project_entry()
    elif event.signal == signals.NEW_PROJECT:
        status = chart.trans(in_project)
        chart.empty_project()
    elif event.signal == signals.LOAD_PROJECT:
        status = chart.trans(in_project)
        chart.load_project(event.payload)
    else:
        status = return_status.SUPER
        chart.temp.fun = chart.top

    return status


@spy_on
def in_project(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_in_project_entry()
    elif event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_in_project_exit()
    elif event.signal == signals.UNDO_HISTORY:
        status = return_status.HANDLED
        chart.on_in_project_undo_history()
    elif event.signal == signals.ADD_FILE:
        status = return_status.HANDLED
        chart.on_in_project_add_file(event.payload)
    elif event.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED
        chart.on_in_project_remove_file(event.payload)
    elif event.signal == signals.SELECT_IMAGE:
        status = return_status.HANDLED
        chart.on_in_project_select_image(event.payload)
    elif event.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        abs_path = event.payload
        chart.on_in_project_save_project(abs_path)
    elif event.signal == signals.DRAW_RECT:
        status = chart.trans(drawing_rect)
    elif event.signal == signals.DRAW_POLY:
        status = chart.trans(drawing_poly)
    elif event.signal == signals.ADD_POINT:
        status = chart.trans(adding_point)
    elif event.signal == signals.REMOVE_POINT:
        status = chart.trans(removing_point)
    elif event.signal == signals.MOVE_POINT:
        status = chart.trans(moving_point)
    elif event.signal == signals.FIGURE_SELECTED:
        status = return_status.HANDLED
        selected_figure_id = event.payload
        chart.on_in_project_figure_selected(selected_figure_id)
    elif event.signal == signals.DELETE_FIGURE:
        status = return_status.HANDLED
        figure_id = event.payload
        chart.on_in_project_delete_figure(figure_id)
    elif event.signal == signals.SET_FIGURE_CATEGORY:
        status = return_status.HANDLED

        file_id = event.payload['file_id']
        figure_id = event.payload['figure_id']
        category = event.payload['category']

        chart.on_in_project_set_figure_category(file_id, figure_id, category)
    elif event.signal == signals.SAVE_TEMP:
        status = return_status.HANDLED
        chart.on_in_project_save_temp()
    elif event.signal == signals.ROTATE_CW:
        status = return_status.HANDLED
        chart.on_in_project_rotate_cw()
    elif event.signal == signals.ROTATE_CCW:
        status = return_status.HANDLED
        chart.on_in_project_rotate_ccw()
    elif event.signal == signals.UPDATE_QUICK_CATEGORIES:
        status = return_status.HANDLED
        chart.on_in_project_update_quick_categories(event.payload)
    else:
        status = return_status.SUPER
        chart.temp.fun = no_project

    return status


@spy_on
def drawing_rect(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_rect_entry()
    elif event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_rect_exit()
    elif event.signal == signals.RESET_DRAWING or event.signal == signals.RIGHT_CLICK:
        status = chart.trans(in_project)
        chart.on_drawing_rect_reset_drawing()
    elif event.signal == signals.CLICK:
        status = chart.trans(drawing_rect_waiting_for_2_point)
        chart.on_drawing_rect_click(event.payload)
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status


@spy_on
def drawing_rect_waiting_for_2_point(chart: Statechart, event: Event) -> return_status:
    status = return_status.HANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_rect_waiting_for_2_point_entry()
    elif event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_rect_waiting_for_2_point_exit()
    if event.signal == signals.CLICK:
        status = chart.trans(in_project)
        chart.on_drawing_rect_waiting_for_2_point_click(event.payload)
    elif event.signal == signals.RESET_DRAWING or event.signal == signals.RIGHT_CLICK:
        status = chart.trans(in_project)
        chart.on_drawing_rect_waiting_for_2_point_reset_drawing()
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status


@spy_on
def drawing_poly(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_poly_entry()
    elif event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_drawing_poly_exit()
    elif event.signal == signals.RESET_DRAWING:
        status = chart.trans(in_project)
        chart.on_drawing_poly_reset_drawing()
    elif event.signal == signals.CLICK:
        status = return_status.HANDLED
        chart.on_drawing_poly_click(event.payload)
        if chart.on_drawing_poly_click_check_if_have_to_finish_drawing():
            chart.on_drawing_poly_finish_drawing()
            status = chart.trans(in_project)
    elif event.signal == signals.RIGHT_CLICK:
        status = chart.trans(in_project)
        chart.save_current_polygon_as_is()
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status


@spy_on
def moving_point(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_moving_point_entry()
    if event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_moving_point_exit()
    if event.signal == signals.UPDATE_FIGURE_POINT_POSITION:
        status = return_status.HANDLED
        chart.on_moving_point_update_figure_point_position(event.payload['figure_idx'],
                                                           event.payload['point_idx'],
                                                           event.payload['coords'])
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status


@spy_on
def removing_point(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_removing_point_entry()
    if event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_removing_point_exit()
    if event.signal == signals.UPDATE_FIGURE_REMOVE_POINT:
        status = return_status.HANDLED
        chart.on_removing_point_update_figure_remove_point(event.payload['figure_idx'], event.payload['point_idx'])
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status


@spy_on
def adding_point(chart: Statechart, event: Event) -> return_status:
    status = return_status.UNHANDLED

    if event.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        chart.on_adding_point_entry()
    if event.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        chart.on_adding_point_exit()
    if event.signal == signals.UPDATE_FIGURE_INSERT_POINT:
        status = return_status.HANDLED
        chart.on_adding_point_update_figure_insert_point(event.payload['figure_idx'], event.payload['point_idx'], event.payload['coords'])
    else:
        status = return_status.SUPER
        chart.temp.fun = in_project

    return status
