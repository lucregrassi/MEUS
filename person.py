class Person:
    def __init__(self, n, curr_node=0, dest_node=0, distance=0, error=0, moving=False):
        self.n = n
        self.curr_node = curr_node
        self.dest_node = dest_node
        self.distance = distance
        self.error = error
        self.moving = moving
        self.visited_nodes = []
        self.seen_events = []

    def __repr__(self):
        return "Person id: " + str(self.n) + " \n " \
               "curr_node: " + str(self.curr_node) + " \n " \
               "dest_node: " + str(self.dest_node) + " \n " \
                "distance: " + str(self.distance) + " \n " \
                "error: " + str(self.error) + " \n " \
               "moving: " + str(self.moving) + " \n "  \
               "visited nodes: " + str(self.visited_nodes) + " \n "  \
                "seen_events: " + str(self.seen_events)

