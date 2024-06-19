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
                helpers.select_image_event(self, self.project.get_selected_file_id())
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

    def on_in_project_add_file(self, abs_path):
        selected_file_id, _ = self.project.get_selected_file()
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

        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

        self.bus.gui.load_image_into_canvas(file_data['abs_path'])
        for figure_id, figure_data in enumerate(file_data['figures']):
            self.bus.gui.draw_figure(file_id, figure_id, figure_data)
            self.bus.gui.insert_figure_into_figures_list(file_id, figure_id, figure_data)

        self.bus.gui.enable_draw_buttons()

        self.bus.gui.files_frame_treeview.selection_set([file_id])
        helpers.reset_drawing_event(self)

    def on_in_project_figure_selected(self, selected_figure_id):
        self.bus.gui.clear_canvas()

        selected_file_id, selected_file_data = self.project.get_selected_file()

        self.bus.gui.load_image_into_canvas(selected_file_data['abs_path'])
        for figure_id, figure_data in enumerate(selected_file_data['figures']):
            highlight_figure = selected_figure_id == figure_id
            self.bus.gui.draw_figure(selected_file_id, figure_id, figure_data, highlight_figure=highlight_figure)


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
    # elif e.signal == signals.UNDO_HISTORY:
    #     status = return_status.HANDLED
    #
    #     if c.history.has_history(c.active_file_id):
    #         snapshot = c.history.pop_history(c.active_file_id)
    #         c.files[c.active_file_id] = snapshot
    #
    #         c.bus.gui.clear_figures()
    #         c.bus.gui.clear_canvas()
    #         c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
    #         c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])

    elif e.signal == signals.ADD_FILE:
        status = return_status.HANDLED
        c.on_in_project_add_file(e.payload)
    elif e.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED
        del c.files[e.payload]

        c.bus.gui.remove_file(e.payload)
        if e.payload == c.active_file_id:
            c.bus.gui.clear_figures()
            c.bus.gui.clear_canvas()

        if len(c.files.keys()) > 0:
            c.bus.gui.enable_remove_file_btn()
        else:
            c.bus.gui.disable_remove_file_btn()

        c.bus.gui.disable_draw_buttons()

        if e.payload == c.active_file_id:
            if len(c.files.keys()) > 0:
                helpers.select_image_event(c, list(c.files.keys())[0])
    elif e.signal == signals.SELECT_IMAGE:
        status = return_status.HANDLED
        c.on_in_project_select_image(e.payload)
    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        helpers.save_project_file_to_path(e.payload, c.files)
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

        figure_idx = e.payload
        if figure_idx is not None:
            del c.files[c.active_file_id]['figures'][figure_idx]

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])

        c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])
    elif e.signal == signals.SET_FIGURE_CATEGORY:
        status = return_status.HANDLED

        file_id = e.payload['file_id']
        figure_id = e.payload['figure_id']
        category = e.payload['category']

        print('SET_FIGURE_CATEGORY', e.payload)
        print(c.files)

        if file_id in c.files and c.files[file_id]['figures'][figure_id] is not None:
            c.files[file_id]['figures'][figure_id]['category'] = category
            c.history.add_snapshot(file_id, c.files[file_id])

            print(c.files[c.active_file_id]['figures'])

            if file_id == c.active_file_id:
                c.bus.gui.clear_figures()
                c.bus.gui.clear_canvas()
                c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
                c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])
    else:
        status = return_status.SUPER
        c.temp.fun = no_project

    return status


@spy_on
def drawing_rect(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.bind_canvas_click_event()
        c.bus.gui.bind_canvas_motion_rect_drawing_stage_1()

        c.points = []
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.unbind_canvas_click_event()
        c.bus.gui.unbind_canvas_motion_rect_drawing_stage_1()
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)
        c.points = []

    elif e.signal == signals.CLICK:
        status = c.trans(drawing_rect_waiting_for_2_point)

        c.points.append(e.payload)
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def drawing_rect_waiting_for_2_point(c: Statechart, e: Event) -> return_status:
    status = return_status.HANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.drawing_rect_point_1 = c.points[0]

        c.bus.gui.bind_canvas_click_event()
        c.bus.gui.bind_canvas_motion_rect_drawing_stage_2()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.unbind_canvas_motion_rect_drawing_stage_2()
        c.bus.gui.unbind_canvas_click_event()

        c.bus.gui.drawing_rect_point_1 = None

        c.points = []
    if e.signal == signals.CLICK:
        status = c.trans(in_project)

        c.points.append(e.payload)
        c.files[c.active_file_id]['figures'].append({
            'type': 'rect',
            'points': [c.bus.gui.from_canvas_to_image_coords(*point) for point in c.points],
            'category': None
        })
        helpers.ask_for_category_name(c, copy.copy(c.active_file_id), len(c.files[c.active_file_id]['figures']) - 1)

        c.points = []
        helpers.select_image_event(c, c.active_file_id)

        c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)

        helpers.select_image_event(c, c.active_file_id)
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def drawing_poly(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.bind_canvas_click_event()
        c.bus.gui.bind_canvas_motion_poly_drawing()
    elif e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED

        c.points = []

        c.bus.gui.drawing_poly_points = []
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.bus.gui.unbind_canvas_click_event()
        c.bus.gui.unbind_canvas_motion_poly_drawing()
    elif e.signal == signals.RESET_DRAWING:
        status = c.trans(in_project)
        c.points = []

    elif e.signal == signals.CLICK:
        status = return_status.HANDLED

        c.points.append(e.payload)

        c.bus.gui.drawing_poly_points.append(e.payload)

        if len(c.points) >= 3:
            point_start = c.points[0]
            point_finish = c.points[-1]

            if abs(point_finish[0] - point_start[0]) <= 5 and abs(point_finish[1] - point_start[1]) <= 5:

                c.points.pop()
                c.files[c.active_file_id]['figures'].append({
                    'type': 'poly',
                    'points': [c.bus.gui.from_canvas_to_image_coords(*point) for point in c.points],
                    'category': None
                })

                helpers.ask_for_category_name(c, copy.copy(c.active_file_id), len(c.files[c.active_file_id]['figures']) - 1)

                c.points = []
                helpers.select_image_event(c, c.active_file_id)

                status = c.trans(in_project)

                c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])

    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def moving_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'], draw_grabbable_points=True)

        c.bus.gui.bind_point_move_click()
        c.bus.gui.bind_point_move_motion_event()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])

        c.bus.gui.unbind_point_move_click()
        c.bus.gui.unbind_point_move_motion_event()
    if e.signal == signals.UPDATE_FIGURE_POINT_POSITION:
        status = return_status.HANDLED

        c.files[c.active_file_id]['figures'][e.payload['figure_idx']]['points'][e.payload['point_idx']] = c.bus.gui.from_canvas_to_image_coords(*e.payload['coords'])

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'], draw_grabbable_points=True)

        c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def removing_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'], draw_grabbable_points=True)

        c.bus.gui.bind_point_remove_click()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])

        c.bus.gui.bind_point_remove_click()
    if e.signal == signals.UPDATE_FIGURE_REMOVE_POINT:
        status = return_status.HANDLED

        if c.files[c.active_file_id]['figures'][e.payload['figure_idx']]['type'] == 'rect':
            del c.files[c.active_file_id]['figures'][e.payload['figure_idx']]
        else:
            if len(c.files[c.active_file_id]['figures'][e.payload['figure_idx']]['points']) <= 3:
                del c.files[c.active_file_id]['figures'][e.payload['figure_idx']]
            else:
                del c.files[c.active_file_id]['figures'][e.payload['figure_idx']]['points'][e.payload['point_idx']]

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'], draw_grabbable_points=True)

        c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def adding_point(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures_as_polylines(c.files[c.active_file_id]['figures'])

        c.bus.gui.bind_point_add_click()
    if e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures(c.files[c.active_file_id]['figures'])

        c.bus.gui.unbind_point_add_click()
    if e.signal == signals.UPDATE_FIGURE_INSERT_POINT:
        status = return_status.HANDLED

        c.files[c.active_file_id]['figures'][e.payload['figure_idx']]['points'].insert(e.payload['point_idx'], c.bus.gui.from_canvas_to_image_coords(*e.payload['coords']))

        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()
        c.bus.gui.load_image_into_canvas(c.files[c.active_file_id]['abs_path'])
        c.bus.gui.redraw_figures_as_polylines(c.files[c.active_file_id]['figures'])

        c.history.add_snapshot(c.active_file_id, c.files[c.active_file_id])
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status
