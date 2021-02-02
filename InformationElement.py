class InformationElement:
    def __init__(self, n, history=None, where=0, when=0, what=None, root=None):
        self.n = n
        self.history = history
        self.where = where
        self.when = when
        # Information element or direct observation
        self.what = what
        self.root = root

    def __str__(self):
        return "[Information Element: " + str(self.n) + ", " + str(self.history) + ", " + str(self.where) + ", " + str(self.when) + ", " \
                + str(self.what) + "]"

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
        return "[Direct Observation: " + str(self.event) + ", " + str(self.error) + "]"

    def __eq__(self, other):
        if self.event == other.event and self.error == other.error:
            return True
        return False

# agent 1
# [1, 10, 5, [persona morta, 0]]          [2, 12, 6, [2, 5, 4, [cane, 1]]]

# agent 2
# [2, 5, 4, [cane, 1]]                    [1, 12, 6, [1, 10, 5, [persona morta, 0]]]

# InformationElement(1, 10, 5, DirectObservation("persona morta", 0))
# InformationElement(2, 12, 6, InformationElement(2, 5, 4, DirectObservation("cane", 1)))