import pandas as pd
import os
from glob import glob
import json
from utils import lawshe_values
from ontology_utils import distance_between_two_classes

city = "amatrice"
folder_name = "/experiments/exp3_stddev_" + city + "_new_seed69/"
exp_folder_path = os.getcwd() + folder_name
folders = sorted(glob(exp_folder_path + '/exp[0-8]'))


def first_valid_observation():
    result = {}
    exp_number = 0
    for folder in folders:
        outcomes_dict = {"correct": 0, "wrong": 0, "distances": []}
        csv_folder = folder + "/csv/"
        # For each file in the csv folder of the experiment compute tp and fp
        for file in os.listdir(csv_folder):
            csv_file = pd.read_csv(csv_folder + file)
            ground_truth = json.loads(csv_file["ground_truth"][0].replace("'", '"'))

            for i in range(len(csv_file["CVR"])):
                # Fix CVR values
                panel_size = csv_file["Ncoders"][i]
                obs_string = csv_file["observations"][i].replace("'", '"')
                obs_dict = json.loads(obs_string)
                majority = obs_dict[0]["coders"]
                csv_file["CVR"][i] = -2
                if panel_size in lawshe_values.keys():
                    csv_file["CVR"][i] = 0
                    # if the threshold majority is reached
                    if majority >= lawshe_values[panel_size]:
                        csv_file["CVR"][i] = 1

                # the first time there is a majority of voters
                if csv_file["CVR"][i] == 1:
                    # if the majority correct, it is a true positive
                    if (obs_dict[0]["situation"] == ground_truth["situation"]) and \
                            (obs_dict[0]["object"] == ground_truth["object"]):
                        outcomes_dict["correct"] = outcomes_dict["correct"] + 1
                        outcomes_dict["distances"].append(0)
                        print("Experiment", exp_number)
                        print(file)
                    else:
                        distance = distance_between_two_classes(ground_truth["situation"], obs_dict[0]["situation"])
                        outcomes_dict["distances"].append(distance)
                        print(file)
                        print(ground_truth, obs_dict[0])
                        print("Distance", distance)
                        outcomes_dict["wrong"] = outcomes_dict["wrong"] + 1
                    break

        result[exp_number] = outcomes_dict
        exp_number = exp_number + 1

    print(result)
    json_object = json.dumps(result, indent=4)
    with open(exp_folder_path + "first_valid_observations_" + city + ".json", 'w') as f:
        f.write(json_object)


def all_valid_observations():
    result = {}
    exp_number = 0
    for folder in folders:
        print("Experiment", exp_number)
        outcomes_dict = {"correct": 0, "wrong": 0, "distances": []}
        csv_folder = folder + "/csv/"
        # For each file in the csv folder of the experiment compute tp and fp
        for file in os.listdir(csv_folder):
            csv_file = pd.read_csv(csv_folder + file)
            ground_truth = json.loads(csv_file["ground_truth"][0].replace("'", '"'))
            for i in range(len(csv_file["CVR"])):
                # Fix CVR values
                panel_size = csv_file["Ncoders"][i]
                obs_string = csv_file["observations"][i].replace("'", '"')
                obs_dict = json.loads(obs_string)
                majority = obs_dict[0]["coders"]
                csv_file["CVR"][i] = -2
                if panel_size in lawshe_values.keys():
                    csv_file["CVR"][i] = 0
                    # if the threshold majority is reached
                    if majority >= lawshe_values[panel_size]:
                        csv_file["CVR"][i] = 1

                # the first time there is a majority of voters
                if csv_file["CVR"][i] == 1:
                    # if the majority correct, it is a true positive
                    if(obs_dict[0]["situation"] == ground_truth["situation"]) and \
                            (obs_dict[0]["object"] == ground_truth["object"]):
                        outcomes_dict["correct"] = outcomes_dict["correct"] + 1
                        outcomes_dict["distances"].append(0)
                    else:
                        distance = distance_between_two_classes(ground_truth["situation"], obs_dict[0]["situation"])
                        outcomes_dict["distances"].append(distance)
                        print(file)
                        print(ground_truth, obs_dict[0])
                        print("Distance", distance)
                        outcomes_dict["wrong"] = outcomes_dict["wrong"] + 1

        result[exp_number] = outcomes_dict
        exp_number = exp_number + 1

    print(result)
    json_object = json.dumps(result, indent=4)
    with open(exp_folder_path + "all_valid_observations_" + city + ".json", 'w') as f:
        f.write(json_object)


first_valid_observation()
all_valid_observations()

