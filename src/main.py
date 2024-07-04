from src.common_bus import CommonBus
from src.gui import Gui
from src.statechart import Statechart
from src.exporters.yolo import YoloExporter


if __name__ == '__main__':
    b = CommonBus()
    s = Statechart('statechart', bus=b)
    y = YoloExporter(bus=b)
    g = Gui(bus=b)

    s.run()
    g.run()
