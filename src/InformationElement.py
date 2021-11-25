import json

class InformationElement:
    def __init__(self, n, history=None, where=0, when=0, what=None, root=None):
        super().__init__()
        self.n = n
        self.history = history
        self.where = where
        self.when = when
        # Information element or direct observation
        self.what = what
        self.root = root

    def __str__(self):
        return "[Information Element: " + str(self.n) + ", " + str(self.history) + ", " + str(self.where) + ", " + str(self.when) + ", " \
                + str(self.what) + "]"# "\nroot:" + str(self.root) + "]"

    def __eq__(self, other):
        if isinstance(other, InformationElement):
            if self.n == other.n and self.where == other.where and self.what == other.what and \
                self.history == other.history and self.when == other.when:
                return True
        return False

    def asdict(self):
        return {'id': self.n, 'history': self.history, 'where': self.where, 'when': self.when, 'what': self.what}#, 'root': self.root}

class NewInformationElement:
    def __init__(self, n, where=0, when=0, what=None):
        super().__init__()
        self.n = n
        self.where = where
        self.when = when
        self.what = what

    def __str__(self):
        return "IE: " + str(self.n) + ", " + str(self.where) + ", " + str(self.when) + ", " \
            + str(self.what)

    def __eq__(self, other):
        if isinstance(other, NewInformationElement):
            if self.n == other.n and self.where == other.where and self.what == other.what and \
                self.when == other.when:
                return True
        return False

    def asdict(self):
        return {'id': self.n, 'where': self.where, 'when': self.when, 'what': self.what}

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

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


class NewDirectObservation:
    def __init__(self, event=None, error=0):
        super().__init__()
        # self.who = who
        # self.where = where
        # self.when = when
        self.event = event
        self.error = error

    def __str__(self):
        # return "[Direct Observation: " + str(self.who) + ", " + str(self.where) + ", " +\
        #     str(self.when) + ", " + str(self.event) + ", " + str(self.error) + "]"
        return "DO: " + str(self.event) + ", " + str(self.error)

    def __eq__(self, other):
        if self.event == other.event and self.error == other.error:
            return True
        return False
    
    def asdict(self):
        return {'event': self.event, 'error': self.error}
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)