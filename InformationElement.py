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
                + str(self.what) + "]"# "\nroot:" + str(self.root) + "]"

    def __eq__(self, other):
        if isinstance(other, InformationElement):
            if self.n == other.n and self.where == other.where and self.what == other.what and \
                self.history == other.history and self.when == other.when:
                return True
        return False

    def asdict(self):
        return {'id': self.n, 'history': self.history, 'where': self.where, 'when': self.when, 'what': self.what}#, 'root': self.root}
    
#     def __iter__(self):
#         return InformationElementIterator(self)

# class InformationElementIterator:
#     def __init__(self, infoelem):#, nestedLevels):
#         self._infoelem = infoelem
#         self._index = nestedLevels
    
#     def __next__(self):
#         # iterate over the 'what' fields
#         if self._index > 0:
#             result = self._infoelem.what
#             self._index -= 1

#         return result

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
    
    def asdict(self):
        return {'event': self.event, 'error': self.error}