
class YoloExporter:
    def __init__(self, bus):
        self.bus = bus
        self.bus.register_item('exporters[yolo]', self)

    def register_in_gui(self, gui):
        pass

    def show_options(self):
        pass

    def export(self, options, path):
        pass