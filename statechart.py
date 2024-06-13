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

    def save_project(self, abs_path):
        helpers.save_project_file_to_path(abs_path, self.files)



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

        c.bus.gui.enable_save_project_btn()
        c.bus.gui.enable_add_file_btn()
        if len(c.files.keys()) > 0:
            c.bus.gui.enable_remove_file_btn()

        c.bus.gui.clear_files()
        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()

        for id_, filedata in c.files.items():
            c.bus.gui.add_file(id_, filedata)

        if c.files:
            helpers.select_image_event(c, list(c.files.keys())[0])

        c.bus.gui.bind_select_image_listener()
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.unbind_select_image_listener()
        c.bus.gui.clear_files()
        c.bus.gui.clear_figures()
        c.bus.gui.clear_canvas()

    elif e.signal == signals.ADD_FILE:
        status = return_status.HANDLED

        prev_files_count = len(c.files.keys())

        for filename in e.payload:
            c.files[str(uuid.uuid4())] = {
                'abs_path': filename,
                'figures': []
            }

        c.bus.gui.clear_files()
        for id_, filedata in c.files.items():
            c.bus.gui.add_file(id_, filedata)

        if len(c.files.keys()) > 0:
            c.bus.gui.enable_remove_file_btn()
        else:
            c.bus.gui.disable_remove_file_btn()

        if prev_files_count == 0:
            helpers.select_image_event(c, list(c.files.keys())[0])
        else:
            helpers.select_image_event(c, c.active_file_id)

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

        if c.active_file_id != e.payload:
            c.bus.gui.clear_figures()
            c.bus.gui.clear_canvas()

            c.bus.gui.load_image_into_canvas(c.files[e.payload]['abs_path'])

            c.bus.gui.enable_draw_buttons()

            c.active_file_id = e.payload
        c.bus.gui.files_frame_treeview.selection_set([e.payload])

    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED

        c.save_project(e.payload)

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

    if e.signal == signals.CLICK:
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status


@spy_on
def drawing_poly(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.CLICK:
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        c.temp.fun = in_project

    return status
