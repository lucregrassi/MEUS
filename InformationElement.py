class InformationElement:
    def __init__(self, n, where=0, when=0, what=None):
        self.n = n
        self.where = where
        self.when = when
        # Information element or direct observation
        self.what = what

    def __str__(self):
        return "IE: " + str(self.n) + ", " + str(self.where) + ", " + str(self.when) + ", " \
                + str(self.what)

    def __eq__(self, other):
        if isinstance(other, InformationElement):
            # print("Teller IE root: ", self.n, self.where, self.what)
            # print("Listener IE root: ", other.n, other.where, other.what)
            if self.n == other.n and self.where == other.where and self.what == other.what:
                return True
        return False


class DirectObservation:
    def __init__(self, event=None, error=0):
        self.event = event
        self.error = error

    def __str__(self):
        return "DO: " + str(self.event) + ", " + str(self.error)

    def __eq__(self, other):
        if self.event == other.event and self.error == other.error:
            return True
        return False
