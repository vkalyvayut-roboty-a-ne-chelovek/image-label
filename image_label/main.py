from image_label.common_bus import CommonBus
from image_label.gui import Gui
from image_label.statechart import Statechart
from image_label.exporters.yolo import YoloExporter


def run():
    b = CommonBus()
    s = Statechart('statechart', bus=b)
    y = YoloExporter(bus=b)
    g = Gui(bus=b)

    s.run()
    g.run()


if __name__ == '__main__':
    run()
