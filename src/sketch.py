class Graph:
    def __init__(self, adjac_lis, H):
        self.adjac_lis = adjac_lis
        self.H = H

    def get_neighbors(self, v):
        return self.adjac_lis[v]

    # This is heuristic function which is having equal values for all nodes
    def h(self, n):
        # H = {
        #     'A': 1,
        #     'B': 1,
        #     'C': 1,
        #     'D': 1
        # }

        return self.H[n]

    def a_star_algorithm(self, start, stop):
        # In this open_lst is a list of nodes which have been visited, but who's
        # neighbours haven't all been always inspected, It starts off with the start 
        # node
        # And closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
        open_lst = {start}
        closed_lst = set([])

        # poo has present distances from start to all other nodes
        # the default value is +infinity
        poo = {start: 0}

        # par contains an adjac mapping of all nodes
        par = {start: start}

        while len(open_lst) > 0:
            n = None

            # it will find a node with the lowest value of f() -
            for v in open_lst:
                if n is None or poo[v] + self.h(v) < poo[n] + self.h(n):
                    n = v

            if n is None:
                print('Path does not exist!')
                return None

            # if the current node is the stop
            # then we start again from start
            if n == stop:
                reconst_path = []

                while par[n] != n:
                    reconst_path.append(n)
                    n = par[n]

                reconst_path.append(start)

                reconst_path.reverse()

                print('Path found: {}'.format(reconst_path))
                return reconst_path

            # for all the neighbors of the current node do
            for (m, weight) in self.get_neighbors(n):
                # if the current node is not present in both open_lst and closed_lst
                # add it to open_lst and note n as it's par
                if m not in open_lst and m not in closed_lst:
                    open_lst.add(m)
                    par[m] = n
                    poo[m] = poo[n] + weight

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update par data and poo data
                # and if the node was in the closed_lst, move it to open_lst
                else:
                    if poo[m] > poo[n] + weight:
                        poo[m] = poo[n] + weight
                        par[m] = n

                        if m in closed_lst:
                            closed_lst.remove(m)
                            open_lst.add(m)

            # remove n from the open_lst, and add it to closed_lst
            # because all of his neighbors were inspected
            open_lst.remove(n)
            closed_lst.add(n)

        print('Path does not exist!')
        return None


adjac_lis = {
    'A': [('B', 1), ('C', 3), ('D', 7)],
    'B': [('D', 5)],
    'C': [('D', 12)]
}

lis = {'Situation': [('EmergencyBuilding', 1), ('BlockedBuilding', 2), ('CollapsedBuilding', 2), ('FloodedBuilding', 2),
                     ('OnFireBuilding', 2), ('EmergencyOutdoor', 1), ('BlockedByDebris', 2), ('TrafficJam', 2),
                     ('EmergencyPeople', 1), ('DeadPeople', 2), ('InjuredPeople', 2), ('MildlyInjuredPeople', 3),
                     ('SeverelyInjuredPeople', 3), ('PanickedPeople', 2), ('StarvingPeople', 2), ('NoFoodPeople', 3),
                     ('NoMedicinePeople', 3), ('NoWaterPeople', 3)],

       'EmergencyBuilding': [('Situation', 1), ('BlockedBuilding', 1), ('CollapsedBuilding', 1),
                             ('FloodedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyOutdoor', 1),
                             ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyPeople', 1),
                             ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 2),
                             ('SeverelyInjuredPeople', 2), ('PanickedPeople', 1), ('StarvingPeople', 1),
                             ('NoFoodPeople', 2), ('NoMedicinePeople', 2), ('NoWaterPeople', 2)],

       'EmergencyOutdoor': [('Situation', 1), ('BlockedBuilding', 1), ('CollapsedBuilding', 1),
                            ('FloodedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyBuilding', 1),
                            ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyPeople', 1),
                            ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 2),
                            ('SeverelyInjuredPeople', 2), ('PanickedPeople', 1), ('StarvingPeople', 1),
                            ('NoFoodPeople', 2), ('NoMedicinePeople', 2), ('NoWaterPeople', 2)],

       'EmergencyPeople': [('Situation', 1), ('BlockedBuilding', 1), ('CollapsedBuilding', 1),
                           ('FloodedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyBuilding', 1),
                           ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                           ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 2),
                           ('SeverelyInjuredPeople', 2), ('PanickedPeople', 1), ('StarvingPeople', 1),
                           ('NoFoodPeople', 2), ('NoMedicinePeople', 2), ('NoWaterPeople', 2)],

       'BlockedBuilding': [('Situation', 2), ('EmergencyPeople', 1), ('CollapsedBuilding', 1),
                           ('FloodedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyBuilding', 1),
                           ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                           ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                           ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                           ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'CollapsedBuilding': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                             ('FloodedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyBuilding', 1),
                             ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                             ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                             ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                             ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'FloodedBuilding': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                           ('CollapsedBuilding', 1), ('OnFireBuilding', 1), ('EmergencyBuilding', 1),
                           ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                           ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                           ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                           ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'OnFireBuilding': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                          ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                          ('BlockedByDebris', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                          ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                          ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                          ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'BlockedByDebris': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                           ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                           ('OnFireBuilding', 1), ('TrafficJam', 1), ('EmergencyOutdoor', 1),
                           ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                           ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                           ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'TrafficJam': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                      ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                      ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 1),
                      ('DeadPeople', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                      ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                      ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'DeadPeople': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                      ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                      ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 1),
                      ('TrafficJam', 1), ('InjuredPeople', 1), ('MildlyInjuredPeople', 1),
                      ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                      ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'InjuredPeople': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                         ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                         ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 1),
                         ('TrafficJam', 1), ('DeadPeople', 1), ('MildlyInjuredPeople', 1),
                         ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                         ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'MildlyInjuredPeople': [('Situation', 3), ('EmergencyPeople', 2), ('BlockedBuilding', 1),
                               ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 2),
                               ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 2),
                               ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                               ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                               ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'SeverelyInjuredPeople': [('Situation', 3), ('EmergencyPeople', 2), ('BlockedBuilding', 1),
                                 ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 2),
                                 ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 2),
                                 ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                                 ('MildlyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                                 ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'PanickedPeople': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                          ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                          ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 1),
                          ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                          ('MildlyInjuredPeople', 1), ('SeverelyInjuredPeople', 1), ('StarvingPeople', 1),
                          ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'StarvingPeople': [('Situation', 2), ('EmergencyPeople', 1), ('BlockedBuilding', 1),
                          ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 1),
                          ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 1),
                          ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                          ('MildlyInjuredPeople', 1), ('SeverelyInjuredPeople', 1), ('PanickedPeople', 1),
                          ('NoFoodPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'NoFoodPeople': [('Situation', 3), ('EmergencyPeople', 2), ('BlockedBuilding', 1),
                        ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 2),
                        ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 2),
                        ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                        ('MildlyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                        ('SeverelyInjuredPeople', 1), ('NoMedicinePeople', 1), ('NoWaterPeople', 1)],

       'NoMedicinePeople': [('Situation', 3), ('EmergencyPeople', 2), ('BlockedBuilding', 1),
                            ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 2),
                            ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 2),
                            ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                            ('MildlyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                            ('SeverelyInjuredPeople', 1), ('NoFoodPeople', 1), ('NoWaterPeople', 1)],

       'NoWaterPeople': [('Situation', 3), ('EmergencyPeople', 2), ('BlockedBuilding', 1),
                         ('CollapsedBuilding', 1), ('FloodedBuilding', 1), ('EmergencyBuilding', 2),
                         ('OnFireBuilding', 1), ('BlockedByDebris', 1), ('EmergencyOutdoor', 2),
                         ('TrafficJam', 1), ('DeadPeople', 1), ('InjuredPeople', 1),
                         ('MildlyInjuredPeople', 1), ('PanickedPeople', 1), ('StarvingPeople', 1),
                         ('SeverelyInjuredPeople', 1), ('NoFoodPeople', 1), ('NoMedicinePeople', 1)],
       }


def Compute_dist(cls1, cls2, lis):
    for t, val in enumerate(lis[cls1]):
        if val[0] == cls2:
            return lis[cls1][t][1]

# print(Compute_dist('NoFoodPeople', 'Situation', lis))
# input()
# # H = {
# #             'A': 1,
# #             'B': 1,
# #             'C': 1,
# #             'D': 1
# #         }
# H = {key:1 for key in lis.keys()}
# graph1 = Graph(lis, H)
# graph1.a_star_algorithm('NoFoodPeople', 'Situation')
