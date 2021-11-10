from owlready2 import *
import random
import math
import copy
import numpy as np

# Import and load the ontology from the owl file
onto = get_ontology("ontology/MEUS.owl")
onto.load()

random.seed(1)


# This function takes a random leaf of a class
def get_leaf(cls):
    leafs = []
    for c in onto.search(is_a=cls, subclasses=[]):
        if not list(c.subclasses()):
            leafs.append(c)
    rand_leaf = random.choice(leafs)
    return rand_leaf


def random_event():
    input_cls = onto.Situation
    situation = get_leaf(input_cls)
    sit_copy = situation
    while not list(sit_copy.hasObject):
        # Take the nearest ancestor until you find the ancestor with th object property
        sit_copy = sit_copy.is_a[0]

    # Store the type of object related to the ancestor of the situation
    input_obj = sit_copy.hasObject[0]
    obj = get_leaf(input_obj)

    result = situation.name, obj.name
    return result


def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in the list
        dict_obj[key].append(value)
    else:
        # As key is not in dict, add key-value pair
        dict_obj[key] = value

    # print("************************************************")
    # print(dict_obj)
    # input()


def recursive_up(cls, dictionary, i):

    parent_cls = cls.is_a[0]

    # print("************************************************")
    # print(parent_cls)
    # print(dictionary)

    if i not in dictionary:
        dictionary[i] = [parent_cls]
    else:
        append_value(dictionary, i, parent_cls)

    if parent_cls == onto.Situation or parent_cls == onto.Object or parent_cls == onto.Thing:
        # print(dictionary)
        # print("yo")
        return
    else:
        i +=1
        recursive_up(parent_cls, dictionary, i)



def recursive_down(start_cls, dictionary, i):
    if i in dictionary:
        for cls in dictionary[i]:
            for subclass in cls.subclasses():

                t = list(dictionary.values())
                flat_list = []

                for sublist in t:
                    for item in sublist:

                        flat_list.append(item)

                if subclass not in flat_list and subclass != start_cls:
                    if i+1 in dictionary:

                        append_value(dictionary, i+1, subclass)

                    else:
                        dictionary[i+1] = [subclass]
                        
        recursive_down(start_cls, dictionary, i+1)
    else:
        return


# Return a randomly chosen class among those at a certain distance from the starting one
def get_cls_at_dist(start_cls_name, err_rate, distance):
    start_cls = onto.Situation
    
    for cls in onto.classes():
        if cls.name == start_cls_name:
            start_cls = cls
            break

    if distance == 0:
        return start_cls
    else:
        dictionary = {}
        recursive_up(start_cls, dictionary, 1)
        # print("returned")

    recursive_down(start_cls, dictionary, 1)
    # print(dictionary)

    if distance not in dictionary:
        distance = max(dictionary.keys())
    return random.choice(dictionary[distance])


# seen_situation = get_cls_at_dist(onto.CollapsedBuilding, 2)
# print(seen_situation)


# def compute_distance(estimate, real):
    
#     up_jumps    = 0
#     down_jumps  = 0
#     arr = []
#     flag = False

#     _estimate = copy.deepcopy(estimate)
#     _destimate = copy.deepcopy(estimate)

#     if _estimate==real:
#         return np.abs(up_jumps-down_jumps)

#     # while real not in arr:

#     #     # I have to climb down the ontology tree
#     #     if _destimate==onto.Situation  or _destimate==onto.Object:
#     #         flag=True
#     #         if _destimate :
                
#     #             down_jumps += 1
#     #             _destimate==[subcls for subcls in list(_destimate.subclasses())].index(_destimate)
            
#     #         else:

#     #     else:
#     #         # If I have reached the top I have now to keep going down
#     #         if flag:

#     #         # I have to check if I have to climb till the top of the ontology tree or go down
#     #         else:
#             # Not at the same layer
#     if _destimate not in _destimate.is_a[0].subclasses():
        
#         # check if it is in the layer just below
#         if any(_destimate in nest for nest in \
#             [list(list(_destimate.is_a[0].subclasses())[i].subclasses()) \
#             for i in range(len(list(_destimate.is_a[0].subclasses()))) ]):

#                 down_jumps += 1

#                 return np.abs(up_jumps-down_jumps)

#             # for i, nest in enumerate([list(list(_destimate.is_a[0].subclasses())[i].subclasses()) \
#             #     for i in range(len(list(_destimate.is_a[0].subclasses()))) ]):

#             #     if _destimate in nest:
#             #         for j, val in enumerate(nest):
#             #             _destimate=[list(list(_destimate.is_a[0].subclasses())[i].subclasses()) \
#             #                     \for i in range(len(list(_destimate.is_a[0].subclasses()))) ][i][j]

#         else:
#             # if the level below contains any parent of the real class
#             if real.is_a[0] in [list(list(_destimate.is_a[0].subclasses())[i].subclasses()) \
#             for i in range(len(list(_destimate.is_a[0].subclasses())))]:

#                 down_jumps += 2

#                 return np.abs(up_jumps-down_jumps)

#             else:
#                 # I have to climb upward
#                 up_jumps += 1   
#                 _destimate = _destimate.is_a[0]

#                 if 

#     # return np.abs(up_jumps-down_jumps)



