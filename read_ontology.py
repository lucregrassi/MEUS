from owlready2 import *
import random

# Import and load the ontology from the owl file
onto = get_ontology("ontology/MEUS.owl")
onto.load()


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


def recursive_up(cls, dictionary, i):
    parent_cls = cls.is_a[0]
    if i not in dictionary:
        dictionary[i] = [parent_cls]
    else:
        append_value(dictionary, i, parent_cls)
    if parent_cls == onto.Situation or parent_cls == onto.Object or parent_cls == onto.Thing:
        return
    else:
        i = i+1
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
def get_cls_at_dist(start_cls_name, distance):
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

    recursive_down(start_cls, dictionary, 1)
    # print(dictionary)

    if distance not in dictionary:
        distance = max(dictionary.keys())
    return random.choice(dictionary[distance])


# seen_situation = get_cls_at_dist(onto.CollapsedBuilding, 2)
# print(seen_situation)
