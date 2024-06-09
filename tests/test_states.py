import json
import pathlib
import time
import typing
import unittest
from main import AppGui
from miros import stripped
from miros import Event
from miros import signals


class TestStates(unittest.TestCase):
    def setUp(self):
        self.gui = AppGui('app', debug=True)
        self.gui.run()

    @staticmethod
    def _assert_trace_check(actual_trace, expected_trace):
        with stripped(expected_trace) as _expected_trace, stripped(actual_trace) as _actual_trace:
            for expected, actual in zip(_expected_trace, _actual_trace):
                assert expected == actual, f'{expected} != {actual}'

    def test_app_starts_in_empty_state(self):
        actual_trace = self.gui.trace()
        expected_trace = '''
        [2024-06-09 15:57:32.914362] [app] e->start_at() top->empty
        '''
        self._assert_trace_check(actual_trace, expected_trace)

    def test_new_project_signal(self):
        self.gui.post_fifo(Event(signal=signals.NEW_PROJECT))
        time.sleep(0.1)
        actual_trace = self.gui.trace()
        expected_trace = '''
        [2024-06-09 16:34:01.096098] [app] e->start_at() top->empty
        [2024-06-09 16:34:07.155594] [app] e->NEW_PROJECT() empty->not_empty
        '''

        self._assert_trace_check(actual_trace, expected_trace)
        self.assertIsNotNone(self.gui._app_data)

    def test_load_project_signal(self):
        abs_path_to_project = pathlib.Path('.', 'empty.blp').absolute()
        self.gui.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project))
        time.sleep(0.1)
        actual_trace = self.gui.trace()
        expected_trace = '''
        [2024-06-09 17:20:53.633744] [app] e->start_at() top->empty
        [2024-06-09 17:20:57.730133] [app] e->LOAD_PROJECT() empty->not_empty
        '''

        self._assert_trace_check(actual_trace, expected_trace)
        self.assertIsNotNone(self.gui._app_data)

    def test_load_non_empty_project_signal(self):
        abs_path_to_project = pathlib.Path('.', 'non-empty.blp').absolute()
        self.gui.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project))
        time.sleep(0.1)
        actual_trace = self.gui.trace()
        expected_trace = '''
        [2024-06-09 17:20:53.633744] [app] e->start_at() top->empty
        [2024-06-09 17:20:57.730133] [app] e->LOAD_PROJECT() empty->not_empty
        '''

        self._assert_trace_check(actual_trace, expected_trace)
        self.assertIsNotNone(self.gui._app_data)
        with open(abs_path_to_project, 'r') as f:
            data = json.loads(f.read())
            assert data == self.gui._app_data


if __name__ == '__main__':
    unittest.main()
