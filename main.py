from common_bus import CommonBus
from gui import Gui
from statechart import Statechart
from exporters.yolo import YoloExporter


if __name__ == '__main__':
    b = CommonBus()
    s = Statechart('statechart', bus=b)
    g = Gui(bus=b)
    y = YoloExporter(bus=b)

    s.run()
    g.run()
