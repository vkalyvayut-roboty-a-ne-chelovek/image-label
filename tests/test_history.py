import tempfile
import unittest
from history import History


class TestHistory(unittest.TestCase):
    def test_create_history_with_no_defaults(self):
        h = History()

        assert isinstance(h, History)

    def test_create_history_with_some_defaults(self):
        data = {"1": {"abs_path": None}}

        h = History(defaults=data)

        assert isinstance(h, History)
        assert h.history != dict()
        assert len(h.history) == len(data)

    def test_create_empty_history_and_add_some_defaults(self):
        data = {"1": {"abs_path": None}}

        h = History()

        assert isinstance(h, History)
        assert h.history == dict()
        assert len(h.history) == 0

        for k, v in data.items():
            h.set_defaults(k, v)

        assert h.history != dict()
        assert len(h.history) == len(data)

    def test_create_empty_history_and_add_snapshot(self):
        data = {"1": {"abs_path": tempfile.mktemp()}}
        data2 = {"1": {"abs_path": tempfile.mktemp(), "figures": []}}

        h = History(data)

        for k, v in data2.items():
            h.add_snapshot(k, v)

        assert h.history != dict()
        assert h.pop_history('1') == data2['1']

    def test_create_empty_history_and_check_for_snapshots(self):
        h = History()

        assert not h.has_history('1')

    def test_create_not_empty_history_and_check_for_snapshots(self):
        data = {"1": {"abs_path": tempfile.mktemp()}}

        h = History(data)

        assert h.has_history('1')
        assert not h.has_history('2')

    def test_create_not_empty_history_and_check_pop_history(self):
        data = {"1": {"abs_path": tempfile.mktemp()}}

        h = History(data)

        assert h.pop_history('1') == data['1']


if __name__ == '__main__':
    unittest.main()
