from ..common_bus import CommonBus


class YoloExporter:
    def __init__(self, bus: CommonBus):
        self.bus = bus
        self.bus.register_item('yolo_exporter', self)

    def show_options(self):
        pass

    def export(self, options, path):
        pass