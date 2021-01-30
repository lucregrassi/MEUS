class InformationElement:
    def __init__(self, n, where=0, when=0, what=None):
        self.n = n
        self.where = where
        self.when = when
        # Information element or direct observation
        self.what = what

    def __str__(self):
        return "[Information Element: " + str(self.n) + ", " + str(self.where) + ", " + str(self.when) + ", " \
                + str(self.what) + "]"


class DirectObservation:
    def __init__(self, what=None, error=0):
        self.what = what
        self.error = error

    def __str__(self):
        return "[Direct Observation: " + str(self.what) + ", " + str(self.error) + "]"


# agent 1
# [1, 10, 5, [persona morta, 0]]          [2, 12, 6, [2, 5, 4, [cane, 1]]]

# agent 2
# [2, 5, 4, [cane, 1]]                    [1, 12, 6, [1, 10, 5, [persona morta, 0]]]

# InformationElement(1, 10, 5, DirectObservation("persona morta", 0))
# InformationElement(2, 12, 6, InformationElement(2, 5, 4, DirectObservation("cane", 1)))