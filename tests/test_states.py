import pathlib
import time
import unittest

from miros import stripped

from src import helpers

from src.common_bus import CommonBus
from src.statechart import Statechart
from src.gui import PlaceholderGui


class TestStates(unittest.TestCase):
    @staticmethod
    def _assert_trace_check(actual_trace, expected_trace):
        with stripped(expected_trace) as _expected_trace, stripped(actual_trace) as _actual_trace:
            assert len(_expected_trace) == len(
                _actual_trace), f'Not enough events: expected ({len(_expected_trace)}) != actual({len(_actual_trace)})'
            for expected, actual in zip(_expected_trace, _actual_trace):
                assert expected == actual, f'{expected} != {actual}'

    @staticmethod
    def _assert_spy_check(actual_spy, expected_spy):
        assert len(expected_spy) == len(actual_spy), f'Not enough events: expected ({len(expected_spy)}) != actual({len(actual_spy)})'
        for expected, actual in zip(actual_spy, expected_spy):
            assert expected == actual, f'{expected} != {actual}'

    def setUp(self):
        self.b = CommonBus()
        self.s = Statechart('statechart', bus=self.b)
        self.g = PlaceholderGui(bus=self.b)

        # self.s.live_spy = True
        # self.s.live_trace = True

        self.s.run()
        self.g.run()

    def test_from_no_project_to_in_project_on_new_project(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 14:09:37.319643] [statechart] e->start_at() top->no_project
        [2024-06-28 14:09:37.319643] [statechart] e->NEW_PROJECT() no_project->in_project
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_from_no_project_to_in_project_on_load_project(self):
        helpers.load_project_event(self.s, pathlib.Path('./assets/domik.boobalp'))
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 15:14:35.233332] [statechart] e->start_at() top->no_project
        [2024-06-28 15:14:41.406999] [statechart] e->LOAD_PROJECT() no_project->in_project
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_from_no_project_to_in_project_on_new_project_on_add_file(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:no_project', 'ENTRY_SIGNAL:no_project', 'INIT_SIGNAL:no_project', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:no_project', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)', 'ADD_FILE:in_project', 'POST_FIFO:SELECT_IMAGE', 'ADD_FILE:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'SELECT_IMAGE:in_project', 'POST_FIFO:RESET_DRAWING', 'SELECT_IMAGE:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'RESET_DRAWING:in_project', 'RESET_DRAWING:no_project', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.s.spy()
        self._assert_spy_check(actual_spy, expected_spy)

    def test_project_no_project_to_in_project_on_new_project_on_add_file_on_remove_file(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)

        selected_file_id, _ = self.s.project.get_selected_file()
        helpers.remove_file_event(self.s, file_id=selected_file_id, force=True)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:no_project', 'ENTRY_SIGNAL:no_project', 'INIT_SIGNAL:no_project', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:no_project', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)', 'ADD_FILE:in_project', 'POST_FIFO:SELECT_IMAGE', 'ADD_FILE:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'SELECT_IMAGE:in_project', 'POST_FIFO:RESET_DRAWING', 'SELECT_IMAGE:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'RESET_DRAWING:in_project', 'RESET_DRAWING:no_project', '<- Queued:(0) Deferred:(0)', 'REMOVE_FILE:in_project', 'REMOVE_FILE:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.s.spy()

        self._assert_spy_check(actual_spy, expected_spy)

    def test_project_no_project_to_in_project_to_drawing_rect_on_new_project_on_add_file_on_draw_rect(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)
        helpers.draw_rect_event(self.s)
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 15:55:31.905542] [statechart] e->start_at() top->no_project
        [2024-06-28 15:55:34.006727] [statechart] e->NEW_PROJECT() no_project->in_project
        [2024-06-28 15:55:38.815240] [statechart] e->DRAW_RECT() in_project->drawing_rect
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_project_no_project_to_in_project_to_drawing_rect_to_drawing_rect_waiting_for_2_point_to_in_project_on_new_project_on_add_file_on_draw_rect_on_click_on_click(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)
        helpers.draw_rect_event(self.s)
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(0, 0))
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(0, 0))
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 15:58:43.797013] [statechart] e->start_at() top->no_project
        [2024-06-28 15:58:48.040171] [statechart] e->NEW_PROJECT() no_project->in_project
        [2024-06-28 15:58:56.777206] [statechart] e->DRAW_RECT() in_project->drawing_rect
        [2024-06-28 15:58:57.922233] [statechart] e->CLICK() drawing_rect->drawing_rect_waiting_for_2_point
        [2024-06-28 15:59:00.724389] [statechart] e->CLICK() drawing_rect_waiting_for_2_point->in_project
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_project_no_project_to_in_project_to_drawing_poly_on_new_project_on_add_file_on_draw_poly(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)
        helpers.draw_poly_event(self.s)
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 15:55:31.905542] [statechart] e->start_at() top->no_project
        [2024-06-28 15:55:34.006727] [statechart] e->NEW_PROJECT() no_project->in_project
        [2024-06-28 15:55:38.815240] [statechart] e->DRAW_POLY() in_project->drawing_poly
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_project_no_project_to_in_project_to_drawing_poly_to_in_project_on_new_project_on_add_file_on_draw_poly_on_click_on_click_on_click(self):
        helpers.new_project_event(self.s)
        time.sleep(0.1)
        helpers.add_file_event(self.s, [pathlib.Path('./assets/domiki.png').absolute()])
        time.sleep(0.1)
        helpers.draw_poly_event(self.s)
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(0, 0))
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(100, 0))
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(100, 50))
        time.sleep(0.1)
        helpers.click_canvas_event(self.s, coords=(0, 0))
        time.sleep(0.1)

        expected_states = '''
        [2024-06-28 16:22:39.068617] [statechart] e->start_at() top->no_project
        [2024-06-28 16:22:40.689900] [statechart] e->NEW_PROJECT() no_project->in_project
        [2024-06-28 16:22:45.130358] [statechart] e->DRAW_POLY() in_project->drawing_poly
        [2024-06-28 16:22:48.828693] [statechart] e->CLICK() drawing_poly->in_project
        '''
        actual_states = self.s.trace()

        self._assert_trace_check(actual_states, expected_states)

    def test_no_project_to_in_project_on_load_project_on_select_image_on_remove_figure(self):
        helpers.load_project_event(self.s, pathlib.Path('./assets/domik.boobalp'))
        time.sleep(0.1)
        helpers.figure_selected_event(self.s, 1)
        time.sleep(0.1)
        helpers.delete_figure_event(self.s, 1)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:no_project', 'ENTRY_SIGNAL:no_project', 'INIT_SIGNAL:no_project', '<- Queued:(0) Deferred:(0)', 'LOAD_PROJECT:no_project', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'POST_FIFO:SELECT_IMAGE', 'INIT_SIGNAL:in_project', '<- Queued:(1) Deferred:(0)', 'SELECT_IMAGE:in_project', 'POST_FIFO:RESET_DRAWING', 'SELECT_IMAGE:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'RESET_DRAWING:in_project', 'RESET_DRAWING:no_project', '<- Queued:(0) Deferred:(0)', 'FIGURE_SELECTED:in_project', 'FIGURE_SELECTED:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'DELETE_FIGURE:in_project', 'DELETE_FIGURE:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.s.spy()

        self._assert_spy_check(actual_spy, expected_spy)



if __name__ == '__main__':
    unittest.main()