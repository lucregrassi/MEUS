class Agent:
    def __init__(self, n, curr_node=0, dest_node=0, distance=0, path={}, error=0, moving=False, road=0, num_info_sent=0, num_info_seen=0):
        self.n = n
        self.curr_node  = curr_node
        self.dest_node  = dest_node
        self.distance   = distance
        self.path       = path
        self.error      = error
        self.moving     = moving
        self.road       = road # distance (between 2 nodes) traveled so far by agent
        self.reputation = 0.5
        self.num_info_sent = num_info_sent
        self.num_info_seen = num_info_seen
        self.visited_nodes = []
        self.seen_events = []
        self.met_agents = []
        self.met_in_node = []
        self.met_in_loop = []
        self.global_conn = []
        self.local_conn = []
        self.ies = []

    def __str__(self):
        return "\nAgent id: " + str(self.n) + " \n " \
                "Current node: " + str(self.curr_node) + " \n " \
                "Destination node: " + str(self.dest_node) + " \n " \
                "Distance from destination: " + str(self.distance) + " \n " \
                "Error: " + str(self.error) + " \n " \
                "Moving: " + str(self.moving) + " \n "  \
                "Road: " + str(self.road) + "\n" \
                "Visited nodes: " + str(self.visited_nodes) + " \n "  \
                "Seen events: " + str(self.seen_events) + " \n " \
                "Met agents: " + str(self.met_agents) + " \n " \
                "Met in node: " + str(self.met_in_node) + " \n " \
                "Met in loop: " + str(self.met_in_loop) + " \n " \
                "Global connections: " + str(self.global_conn) + " \n "  \
                "Local connections: " + str(self.local_conn)
                 #"Path to follow: " + str(self.path) + "\n" \