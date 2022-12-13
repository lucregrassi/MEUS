import pandas as pd
import os
import json
from ontology_utils import distance_between_two_classes

city = "Assisi"
root_dir = os.getcwd() + "/experiments/" + city + "/3_information_quality/"


def first_valid_observation():
    result = {}
    exp_number = 0
    exp_folders = sorted(os.listdir(root_dir))
    for exp_folder in exp_folders:
        # Exclude files from processing
        if not os.path.isfile(root_dir + "/" + exp_folder):
            outcomes_dict = {"correct": 0, "wrong": 0, "avg_kalpha": 0, "distances": []}
            csv_folder = root_dir + "/" + exp_folder + "/csv/"
            # For each file in the csv folder of the experiment compute tp and fp
            for file in os.listdir(csv_folder):
                csv_file = pd.read_csv(csv_folder + file)
                ground_truth = json.loads(csv_file["ground_truth"][0].replace("'", '"'))
                for i in range(len(csv_file["CVR"])):
                    # Fix CVR values
                    obs_string = csv_file["observations"][i].replace("'", '"')
                    obs_dict = json.loads(obs_string)

                    # the first time there is a majority of voters
                    if csv_file["CVR"][i] == 1:
                        # if the majority correct, it is a true positive
                        if (obs_dict[0]["situation"] == ground_truth["situation"]) and \
                                (obs_dict[0]["object"] == ground_truth["object"]):
                            outcomes_dict["correct"] = outcomes_dict["correct"] + 1
                            outcomes_dict["distances"].append(0)
                        else:
                            sit_dist = distance_between_two_classes(ground_truth["situation"], obs_dict[0]["situation"])
                            obj_dist = distance_between_two_classes(ground_truth["object"], obs_dict[0]["object"])
                            distance = sit_dist + obj_dist
                            outcomes_dict["distances"].append(distance)
                            outcomes_dict["wrong"] = outcomes_dict["wrong"] + 1
                        outcomes_dict["avg_kalpha"] = outcomes_dict["avg_kalpha"] + csv_file["Kalpha"][i]
                        break
            outcomes_dict["avg_kalpha"] = outcomes_dict["avg_kalpha"] / len(outcomes_dict["distances"])
            result[exp_number] = outcomes_dict
            exp_number = exp_number + 1

    for key, value in result.items():
        print(value["correct"], value["wrong"])
    json_object = json.dumps(result, indent=4)
    with open(root_dir + "first_valid_observations_" + city.lower() + ".json", 'w') as f:
        f.write(json_object)


def all_valid_observations():
    result = {}
    exp_number = 0
    exp_folders = sorted(os.listdir(root_dir))
    for exp_folder in exp_folders:
        # Exclude files from processing
        if not os.path.isfile(root_dir + "/" + exp_folder):
            outcomes_dict = {"correct": 0, "wrong": 0, "avg_kalpha": 0, "distances": []}
            csv_folder = root_dir + "/" + exp_folder + "/csv/"
            # For each file in the csv folder of the experiment compute tp and fp
            for file in os.listdir(csv_folder):
                csv_file = pd.read_csv(csv_folder + file)
                ground_truth = json.loads(csv_file["ground_truth"][0].replace("'", '"'))
                for i in range(len(csv_file["CVR"])):
                    # Fix CVR values
                    obs_string = csv_file["observations"][i].replace("'", '"')
                    obs_dict = json.loads(obs_string)

                    # the first time there is a majority of voters
                    if csv_file["CVR"][i] == 1:
                        # if the majority correct, it is a true positive
                        if(obs_dict[0]["situation"] == ground_truth["situation"]) and \
                                (obs_dict[0]["object"] == ground_truth["object"]):
                            outcomes_dict["correct"] = outcomes_dict["correct"] + 1
                            outcomes_dict["distances"].append(0)
                        else:
                            sit_dist = distance_between_two_classes(ground_truth["situation"], obs_dict[0]["situation"])
                            obj_dist = distance_between_two_classes(ground_truth["object"], obs_dict[0]["object"])
                            distance = sit_dist + obj_dist
                            outcomes_dict["distances"].append(distance)
                            outcomes_dict["wrong"] = outcomes_dict["wrong"] + 1
                        outcomes_dict["avg_kalpha"] = outcomes_dict["avg_kalpha"] + csv_file["Kalpha"][i]
            outcomes_dict["avg_kalpha"] = outcomes_dict["avg_kalpha"] / len(outcomes_dict["distances"])
            result[exp_number] = outcomes_dict
            exp_number = exp_number + 1

    for key, value in result.items():
        print(value["correct"], value["wrong"])
    json_object = json.dumps(result, indent=4)
    with open(root_dir + "all_valid_observations_" + city.lower() + ".json", 'w') as f:
        f.write(json_object)


def all_majority_observations():
    result = {}
    exp_number = 0
    exp_folders = sorted(os.listdir(root_dir))
    for exp_folder in exp_folders:
        # Exclude files from processing
        if not os.path.isfile(root_dir + "/" + exp_folder):
            outcomes_dict = {"correct": 0, "wrong": 0, "avg_kalpha": 0, "distances": []}
            csv_folder = root_dir + "/" + exp_folder + "/csv/"
            # For each file in the csv folder of the experiment compute tp and fp
            for file in os.listdir(csv_folder):
                csv_file = pd.read_csv(csv_folder + file)
                ground_truth = json.loads(csv_file["ground_truth"][0].replace("'", '"'))
                for i in range(len(csv_file["CVR"])):
                    obs_string = csv_file["observations"][i].replace("'", '"')
                    obs_dict = json.loads(obs_string)

                    # the observation made by the majority
                    if(obs_dict[0]["situation"] == ground_truth["situation"]) and \
                            (obs_dict[0]["object"] == ground_truth["object"]):
                        outcomes_dict["correct"] = outcomes_dict["correct"] + 1
                        outcomes_dict["distances"].append(0)
                    else:
                        sit_dist = distance_between_two_classes(ground_truth["situation"], obs_dict[0]["situation"])
                        obj_dist = distance_between_two_classes(ground_truth["object"], obs_dict[0]["object"])
                        distance = sit_dist + obj_dist
                        outcomes_dict["distances"].append(distance)
                        outcomes_dict["wrong"] = outcomes_dict["wrong"] + 1
                    outcomes_dict["avg_kalpha"] = outcomes_dict["avg_kalpha"] + csv_file["Kalpha"][i]
            outcomes_dict["avg_kalpha"] = round((outcomes_dict["avg_kalpha"] / len(outcomes_dict["distances"])), 2)
            result[exp_number] = outcomes_dict
            exp_number = exp_number + 1

    for key, value in result.items():
        print(value["correct"], value["wrong"])
    json_object = json.dumps(result, indent=4)
    with open(root_dir + "all_majority_observations_" + city.lower() + ".json", 'w') as f:
        f.write(json_object)


first_valid_observation()
all_valid_observations()
all_majority_observations()
