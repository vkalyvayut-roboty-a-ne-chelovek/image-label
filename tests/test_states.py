import json
import pathlib
import tempfile
import time
import typing
import unittest
from main import GuiForTest
from main import Statechart
from main import empty
from miros import stripped
from miros import Event
from miros import signals


class TestStates(unittest.TestCase):
    @staticmethod
    def _assert_trace_check(actual_trace, expected_trace):
        with stripped(expected_trace) as _expected_trace, stripped(actual_trace) as _actual_trace:
            assert len(_expected_trace) == len(
                _actual_trace), f'Not enough events: expected ({len(_expected_trace)}) != actual({len(_actual_trace)})'
            for expected, actual in zip(_expected_trace, _actual_trace):
                assert expected == actual, f'{expected} != {actual}'


    def test_new_project_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-09 20:06:29.828994] [statechart] e->start_at() top->empty
        [2024-06-09 20:06:29.829579] [statechart] e->NEW_PROJECT() empty->not_empty
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)


    def test_new_project_signal_app_data(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))

        time.sleep(0.1)

        assert statechart._app_data == []

    def test_load_project_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_empty_project_file = pathlib.Path('.', 'empty.blp').absolute()
        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_empty_project_file))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-09 20:22:03.931939] [statechart] e->start_at() top->empty
        [2024-06-09 20:22:11.626905] [statechart] e->LOAD_PROJECT() empty->not_empty
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)

    def test_load_project_signal_empty_project_content(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        statechart.live_trace = True
        statechart.live_spy = True
        gui.run()

        abs_path_to_empty_project_file = pathlib.Path('.', 'empty.blp').absolute()
        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_empty_project_file))

        time.sleep(0.1)

        with open(abs_path_to_empty_project_file, 'r') as f:
            assert json.loads(f.read()) == statechart._app_data

    def test_load_project_signal_non_empty_project_content(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        statechart.live_trace = True
        statechart.live_spy = True
        gui.run()

        abs_path_to_empty_project_file = pathlib.Path('.', 'non-empty.blp').absolute()
        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_empty_project_file))

        time.sleep(0.1)

        with open(abs_path_to_empty_project_file, 'r') as f:
            assert json.loads(f.read()) == statechart._app_data




if __name__ == '__main__':
    unittest.main()