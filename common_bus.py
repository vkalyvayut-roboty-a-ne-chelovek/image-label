import typing


class CommonBus:
    def __init__(self):
        self.items = {}

    def register_item(self, name: str, item: typing.Any):
        self.items[name] = item

    def __getitem__(self, key):
        return self.items[key]

    def __getattr__(self, key):
        return self.items[key]
