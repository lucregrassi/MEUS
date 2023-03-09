import json
import copy


class InformationElement:
    def __init__(self, n, where=0, when=0, what=None, ie_copies=64):
        super().__init__()
        self.n = n
        self.where = where
        self.when = when
        self.what = what
        self.ie_copies = ie_copies

    def __str__(self):
        return "[Information Element: " + str(self.n) + ", " + str(self.where) + ", " + str(self.when) + ", " \
               + str(self.what) + ", " + str(self.ie_copies) + "]"

    def __eq__(self, other):
        if isinstance(other, InformationElement):
            if self.n == other.n and self.where == other.where and self.when == other.when and self.what == other.what:
                return True
        return False

    def asdict(self):
        return {'id': self.n, 'where': self.where, 'when': self.when, 'what': self.what, "ie_copies": self.ie_copies}

    def toJson(self):
        return self.__dict__


class DirectObservation:
    def __init__(self, event=None, error=0):
        super().__init__()
        self.event = event
        self.error = error

    def __str__(self):
        return "[Direct Observation: " + str(self.event) + ", " + str(self.error) + "]"

    def __eq__(self, other):
        if self.event == other.event and self.error == other.error:
            return True
        return False

    def asdict(self):
        return {'event': self.event, 'error': self.error}

    def toJson(self):
        return self.__dict__
