import copy
import typing

class History:
    def __init__(self, defaults: typing.Dict = None):
        self.history = {}

        if defaults:
            for file_id, new_state in defaults.items():
                self.set_defaults(file_id, new_state)

    def set_defaults(self, file_id, new_state):
        self.history[file_id] = [copy.deepcopy(new_state)]

    def add_snapshot(self, file_id, new_state):
        self.history[file_id].append(copy.deepcopy(new_state))

    def pop_history(self, file_id):
        if len(self.history[file_id]) > 0:
            return self.history[file_id].pop()

    def has_history(self, file_id):
        if file_id in self.history and len(self.history[file_id]) > 0:
            return True
        return False

    def reset_history(self):
        self.history = dict()
