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
        self.active_image = None
        self.points = []

    def run(self):
        self.start_at(no_project)


@spy_on
def no_project(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.save_project_btn['state'] = 'disabled'
        c.bus.gui.add_file_btn['state'] = 'disabled'
        c.bus.gui.remove_file_btn['state'] = 'disabled'
        c.bus.gui.draw_rectangle_btn['state'] = 'disabled'
        c.bus.gui.draw_polygon_btn['state'] = 'disabled'
        
        helpers.new_project_event(c)

    elif e.signal == signals.NEW_PROJECT:
        status = c.trans(in_project)

        c.files = {}
        c.active_image = None
        c.points = []

    elif e.signal == signals.LOAD_PROJECT:
        status = c.trans(in_project)

        c.files = {}
        c.active_image = None
        c.points = []

    else:
        status = return_status.SUPER
        c.temp.fun = c.top

    return status


@spy_on
def in_project(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED

        c.bus.gui.save_project_btn['state'] = 'normal'
        c.bus.gui.add_file_btn['state'] = 'normal'
        if len(c.files) > 0:
            c.bus.gui.remove_file_btn['state'] = 'normal'

        if c.bus.gui.files_frame_treeview.tag_has('#files'):
            c.bus.gui.files_frame_treeview.delete(c.bus.gui.files_frame_treeview.get_children(''))
        if c.bus.gui.figures_frame_treeview.tag_has('#figures'):
            c.bus.gui.figures_frame_treeview.delete(c.bus.gui.figures_frame_treeview.get_children())
        if c.bus.gui.drawing_frame_canvas.gettags('#draw_figures'):
            c.bus.gui.drawing_frame_canvas.delete('#draw_figures')

        for id_, filedata in c.files.items():
            c.bus.gui.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

        if c.files:
            helpers.select_image_event(c, list(c.files.keys())[0])
    elif e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED

        c.post_fifo(Event(signal=signals.ADD_FILE,
                          payload=['/home/user28/projects/python/booba-label/prev/tests/assets/domiki.png' for _ in range(50)]))

    elif e.signal == signals.SELECT_IMAGE:
        status = return_status.HANDLED

        if c.bus.gui.figures_frame_treeview.tag_has('#figures'):
            c.bus.gui.figures_frame_treeview.delete(c.bus.gui.figures_frame_treeview.get_children())
        if c.bus.gui.drawing_frame_canvas.gettags('#draw_figures'):
            c.bus.gui.drawing_frame_canvas.delete('#draw_figures')

        img_data = c.files[e.payload]
        c.active_image = ImageTk.PhotoImage(file=img_data['abs_path'])
        c.bus.gui.drawing_frame_canvas.create_image(
            c.bus.gui.drawing_frame_canvas.winfo_width() // 2,
            c.bus.gui.drawing_frame_canvas.winfo_height() // 2,
            image=c.active_image
        )

        c.bus.gui.draw_rectangle_btn['state'] = 'normal'
        c.bus.gui.draw_polygon_btn['state'] = 'normal'

    if e.signal == signals.ADD_FILE:
        status = return_status.HANDLED

        for filename in e.payload:
            c.files[uuid.uuid4()] = {
                'abs_path': filename,
                'figures': []
            }

        if c.bus.gui.files_frame_treeview.tag_has('#files'):
            c.bus.gui.files_frame_treeview.delete(c.bus.gui.files_frame_treeview.get_children(''))
        for id_, filedata in c.files.items():
            c.bus.gui.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

        if len(c.files) > 0:
            c.bus.gui.remove_file_btn['state'] = 'normal'
        else:
            c.bus.gui.remove_file_btn['state'] = 'disabled'

        if len(c.files) > 0:
            helpers.select_image_event(c, list(c.files.keys())[0])

    elif e.signal == signals.REMOVE_FILE:
        status = return_status.HANDLED

        del c.files[e.payload]

        if c.bus.gui.files_frame_treeview.tag_has('#files'):
            c.bus.gui.files_frame_treeview.delete(c.bus.gui.files_frame_treeview.get_children(''))
        for id_, filedata in c.files.items():
            c.bus.gui.files_frame_treeview.insert('', 'end', id=id_, values=(filedata['abs_path']), tags=('#files',))

        if len(c.files) > 0:
            c.bus.gui.remove_file_btn['state'] = 'normal'
        else:
            c.bus.gui.remove_file_btn['state'] = 'disabled'

        c.bus.gui.draw_rectangle_btn['state'] = 'disabled'
        c.bus.gui.draw_polygon_btn['state'] = 'disabled'

        if len(c.files) > 0:
            helpers.select_image_event(c, list(c.files.keys())[0])

    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
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
