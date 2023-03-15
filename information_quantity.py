import os
import json

city = "Assisi"
routing = "spray&wait"
root_dir = os.getcwd() + "/experiments/" + city + "/" + routing + "/4_Information_quantity/"


def compute_information_load():
    exp_folders = [f for f in sorted(os.listdir(root_dir)) if os.path.isdir(os.path.join(root_dir, f))]
    print(exp_folders)
    for folder in exp_folders:
        average_do = []
        average_jumps = []
        json_file = root_dir + folder + "/agents_ies_log.json"
        with open(json_file) as f:
            ies_dict = json.load(f)
            for _, loop_info in ies_dict.items():
                loop_dos = 0
                loop_jumps = 0
                for _, agent_info in loop_info.items():
                    loop_dos = loop_dos + agent_info[0]
                    loop_jumps = loop_jumps + agent_info[1]
                average_do.append(loop_dos/len(loop_info))
                average_jumps.append(loop_jumps/len(loop_info))
        print(average_do)
        print(average_jumps)

        with open(root_dir + folder + "/average_dos_per_loop.txt", 'w') as f:
            for elem in average_do:
                f.write(str(elem) + "\n")
        with open(root_dir + folder + "/average_jumps_per_loop.txt", 'w') as f:
            for elem in average_jumps:
                f.write(str(elem) + "\n")


compute_information_load()
