
class YoloExporter:
    def __init__(self, bus):
        self.bus = bus
        self.bus.register_item('exporters[yolo]', self)

    def show_options(self):
        print('YOYOYO')

    def export(self, options, path):
        pass