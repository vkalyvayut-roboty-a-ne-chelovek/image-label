import re
import typing


class CommonBus:
    def __init__(self):
        self.items = {}

    def _check_if_array_and_return_groups(self, name: str):
        regex = r'^([a-zA-Z0-9\-]*)\[(\w*)\]$'
        matches = re.findall(regex, name, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        for match in matches:
            if len(match) == 2:
                return match

    def register_item(self, name: str, item: typing.Any):

        arr_data = self._check_if_array_and_return_groups(name)
        if arr_data:
            if arr_data[0] not in self.items:
                self.items[arr_data[0]] = {}
            self.items[arr_data[0]][arr_data[1]] = item
        else:
            self.items[name] = item

    def __getitem__(self, key):
        return self.items[key]

    def __getattr__(self, key):
        return self.items[key]
