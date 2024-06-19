import pathlib
import tempfile
import time
import unittest
from prev.main import GuiForTest
from prev.main import Statechart
import helpers
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

        assert statechart._app_data == dict()

    def test_load_project_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_empty_project_file = pathlib.Path('', 'assets', 'empty.boobalp').absolute()
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
        gui.run()

        abs_path_to_project_file = pathlib.Path('', 'assets', 'empty.boobalp').absolute()
        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project_file))

        time.sleep(0.1)

        assert helpers.read_project_file_from_path(abs_path_to_project_file) == statechart.get_app_data()

    def test_load_project_signal_non_empty_project_content(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_project_file = pathlib.Path('', 'assets', 'non-empty.boobalp').absolute()
        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project_file))

        time.sleep(0.1)

        assert helpers.read_project_file_from_path(abs_path_to_project_file) == statechart.get_app_data()

    def test_save_project_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_project_file_to_load = pathlib.Path('', 'assets', 'empty.boobalp').absolute()
        abs_path_to_project_file_to_save = tempfile.mktemp()

        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project_file_to_load))
        statechart.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=abs_path_to_project_file_to_save))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-09 21:00:58.933378] [statechart] e->start_at() top->empty
        [2024-06-09 21:01:04.755613] [statechart] e->LOAD_PROJECT() empty->not_empty
        [2024-06-09 21:01:08.394898] [statechart] e->SAVE_PROJECT() not_empty->not_empty
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)

    def test_save_project_project_content(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_project_file_to_load = pathlib.Path('', 'assets', 'non-empty.boobalp').absolute()
        abs_path_to_project_file_to_save = tempfile.mktemp()

        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_project_file_to_load))
        statechart.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=abs_path_to_project_file_to_save))

        time.sleep(0.1)

        assert helpers.read_project_file_from_path(abs_path_to_project_file_to_load) == helpers.read_project_file_from_path(abs_path_to_project_file_to_save)

    def test_add_file_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_image_files_to_load = [
            pathlib.Path('', 'assets', 'domik.jpg').absolute(),
            pathlib.Path('', 'assets', 'domik.bmp').absolute(),
            pathlib.Path('', 'assets', 'domik.png').absolute(),
        ]

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))
        statechart.post_fifo(Event(signal=signals.ADD_FILE, payload=abs_path_to_image_files_to_load))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-09 23:46:33.113116] [statechart] e->start_at() top->empty
        [2024-06-09 23:46:35.068902] [statechart] e->NEW_PROJECT() empty->not_empty
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)

    def test_add_file_total_files_count(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_image_files_to_load = [
            pathlib.Path('', 'assets', 'domik.jpg').absolute(),
            pathlib.Path('', 'assets', 'domik.bmp').absolute(),
            pathlib.Path('', 'assets', 'domik.png').absolute(),
        ]

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))
        statechart.post_fifo(Event(signal=signals.ADD_FILE, payload=abs_path_to_image_files_to_load))

        time.sleep(0.1)

        assert 3 == len(statechart.get_app_data())

    def test_remove_file_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_image_files_to_load = [
            pathlib.Path('', 'assets', 'domik.jpg').absolute(),
            pathlib.Path('', 'assets', 'domik.bmp').absolute(),
            pathlib.Path('', 'assets', 'domik.png').absolute(),
        ]

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))
        statechart.post_fifo(Event(signal=signals.ADD_FILE, payload=abs_path_to_image_files_to_load))

        time.sleep(0.1)

        idx = list(statechart.get_app_data().keys())[1]
        statechart.post_fifo(Event(signal=signals.REMOVE_FILE, payload=[idx]))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-10 00:28:39.055237] [statechart] e->start_at() top->empty
        [2024-06-10 00:28:41.059027] [statechart] e->NEW_PROJECT() empty->not_empty
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)

    def test_remove_file_total_files_count(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_image_files_to_load = [
            pathlib.Path('', 'assets', 'domik.jpg').absolute(),
            pathlib.Path('', 'assets', 'domik.bmp').absolute(),
            pathlib.Path('', 'assets', 'domik.png').absolute(),
        ]

        statechart.post_fifo(Event(signal=signals.NEW_PROJECT))
        statechart.post_fifo(Event(signal=signals.ADD_FILE, payload=abs_path_to_image_files_to_load))

        time.sleep(0.1)

        idx = list(statechart.get_app_data().keys())[1]
        statechart.post_fifo(Event(signal=signals.REMOVE_FILE, payload=[idx]))

        time.sleep(0.1)

        assert 2 == len(statechart.get_app_data())

    def test_select_image_signal_state(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_load_project = pathlib.Path('', 'assets', 'domik.boobalp').absolute()

        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_load_project))

        time.sleep(0.1)

        image_idx = list(statechart.get_app_data().keys())[0]
        statechart.post_fifo(Event(signal=signals.SELECT_IMAGE, payload=image_idx))

        time.sleep(0.1)

        expected_trace = '''
        [2024-06-10 09:55:33.619636] [statechart] e->start_at() top->empty
        [2024-06-10 09:55:39.974101] [statechart] e->LOAD_PROJECT() empty->not_empty
        [2024-06-10 09:55:41.850258] [statechart] e->SELECT_IMAGE() not_empty->image_selected
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)

    def test_drawing_rect_signal_states(self):
        gui = GuiForTest()
        statechart = Statechart('statechart', gui=gui)
        gui.run()

        abs_path_to_load_project = pathlib.Path('', 'assets', 'domik.boobalp').absolute()

        statechart.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=abs_path_to_load_project))

        time.sleep(0.1)

        image_idx = list(statechart.get_app_data().keys())[0]
        statechart.post_fifo(Event(signal=signals.SELECT_IMAGE, payload=image_idx))

        time.sleep(0.1)
        statechart.post_fifo(Event(signal=signals.DRAW_RECT))
        time.sleep(0.1)
        statechart.post_fifo(Event(signal=signals.CLICK, payload=(0, 0)))
        statechart.post_fifo(Event(signal=signals.CLICK, payload=(50, 50)))
        time.sleep(0.1)


        expected_trace = '''
        [2024-06-11 09:44:58.460406] [statechart] e->start_at() top->empty
        [2024-06-11 09:45:03.740702] [statechart] e->LOAD_PROJECT() empty->not_empty
        [2024-06-11 09:45:06.747053] [statechart] e->SELECT_IMAGE() not_empty->image_selected
        [2024-06-11 09:45:08.730957] [statechart] e->DRAW_RECT() image_selected->drawing_rectangle_first_point
        [2024-06-11 09:45:09.559043] [statechart] e->CLICK() drawing_rectangle_first_point->drawing_rectangle_second_point
        [2024-06-11 09:45:11.694492] [statechart] e->CLICK() drawing_rectangle_second_point->image_selected
        '''

        actual_trace = statechart.trace()

        self._assert_trace_check(actual_trace, expected_trace)


if __name__ == '__main__':
    unittest.main()