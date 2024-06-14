import uuid

from miros import ActiveObject
from miros import Event
from miros import return_status
from miros import signals
from miros import spy_on

from PIL import ImageTk

from common_bus import CommonBus
import helpers


class Statechart(ActiveObject):
    def __init__(self, name: str, bus: CommonBus):
        super().__init__(name=name)

        self.bus = bus
        self.bus.register_item('statechart', self)

        self.files = {}
        self.active_file_id = None
        self.points = []

    def run(self):
        self.start_at(no_project)

    def empty_project(self):
        self.files = {}
        self.active_file_id = None
        self.points = []

    def load_project(self, abs_path):
        self.files = helpers.read_project_file_from_path(abs_path)
        self.active_file_id = None
        self.points = []

    def on_save_project_in_project_state(self, e):
        helpers.save_project_file_to_path(e.payload, self.files)

    def on_enter_in_project_state(self):
        self.bus.gui.enable_save_project_btn()
        self.bus.gui.enable_add_file_btn()
        if len(self.files.keys()) > 0:
            self.bus.gui.enable_remove_file_btn()

        self.bus.gui.clear_files()
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

        for id_, filedata in self.files.items():
            self.bus.gui.add_file(id_, filedata)

        if len(self.files.keys()) > 0:
            if self.active_file_id and self.active_file_id in self.files.keys():
                helpers.select_image_event(self, self.active_file_id)
            else:
                helpers.select_image_event(self, list(self.files.keys())[0])

        self.bus.gui.bind_select_image_listener()

    def on_exit_in_project_state(self):
        self.bus.gui.unbind_select_image_listener()
        self.bus.gui.clear_files()
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()

    def on_add_file_in_project_state(self, e: Event):
        prev_files_count = len(self.files.keys())

        for filename in e.payload:
            self.files[str(uuid.uuid4())] = {
                'abs_path': filename,
                'figures': []
            }

        self.bus.gui.clear_files()
        for id_, filedata in self.files.items():
            self.bus.gui.add_file(id_, filedata)

        if len(self.files.keys()) > 0:
            self.bus.gui.enable_remove_file_btn()
        else:
            self.bus.gui.disable_remove_file_btn()

        if prev_files_count == 0:
            helpers.select_image_event(self, list(self.files.keys())[0])
        else:
            helpers.select_image_event(self, self.active_file_id)

    def on_remove_file_in_project_state(self, e: Event):
        del self.files[e.payload]

        self.bus.gui.remove_file(e.payload)
        if e.payload == self.active_file_id:
            self.bus.gui.clear_figures()
            self.bus.gui.clear_canvas()

        if len(self.files.keys()) > 0:
            self.bus.gui.enable_remove_file_btn()
        else:
            self.bus.gui.disable_remove_file_btn()

        self.bus.gui.disable_draw_buttons()

        if e.payload == self.active_file_id:
            if len(self.files.keys()) > 0:
                helpers.select_image_event(self, list(self.files.keys())[0])

    def on_select_file_in_project_state(self, e: Event):
        self.bus.gui.clear_figures()
        self.bus.gui.clear_canvas()
        self.bus.gui.load_image_into_canvas(self.files[e.payload]['abs_path'])
        self.bus.gui.redraw_figures(self.files[self.active_file_id]['figures'])

        self.bus.gui.enable_draw_buttons()

        self.bus.gui.files_frame_treeview.selection_set([e.payload])
        helpers.reset_drawing_event(self)

@spy_on
def no_project(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.disable_save_project_btn()
        c.bus.gui.disable_add_file_btn()
        c.bus.gui.disable_remove_file_btn()
        c.bus.gui.disable_draw_buttons()

    elif e.signal == signals.NEW_PROJECT:
        status = c.trans(in_project)

        c.empty_project()

        c.post_fifo(Event(signal=signals.LOAD_PROJECT, payload='/home/user28/projects/python/booba-label/tests/assets/domik.blp'))

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
        c.on_enter_in_project_state()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
        c.on_exit_in_project_state()
    elif e.signal == signals.ADD_FILE:
        status = return_status.HANDLED
        c.on_add_file_in_project_state(e)
    elif e.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED
        c.on_remove_file_in_project_state(e)
    elif e.signal == signals.SELECT_IMAGE:
        c.active_file_id = e.payload
        c.on_select_file_in_project_state(e)
    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        c.on_save_project_in_project_state(e)
    elif e.signal == signals.DRAW_RECT:
        status = c.trans(drawing_rect)
    elif e.signal == signals.DRAW_POLY:
        status = c.trans(drawing_poly)
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
            'points': c.points
        })
        c.points = []
        helpers.select_image_event(c, c.active_file_id)
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
                    'points': c.points
                })
                c.points = []
                helpers.select_image_event(c, c.active_file_id)

                status = c.trans(in_project)

    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status
