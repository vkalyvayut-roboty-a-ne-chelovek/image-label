from common_bus import CommonBus
from gui import Gui
from statechart import Statechart


if __name__ == '__main__':
    b = CommonBus()
    s = Statechart('statechart', bus=b)
    g = Gui(bus=b)

    s.live_spy = True
    s.live_trace = True

    s.run()
    g.run()
