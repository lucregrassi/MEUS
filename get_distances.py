import os
import csv

location = "assisi"
for i in range(9):
    with open("exp3_stddev_" + location + "/exp" + str(i) + "/distances.txt", "w") as file:
        for filename in os.listdir(os.getcwd() + "/exp3_stddev_" + location + "/exp" + str(i) + "/csv"):
            first_line = True
            with open(os.path.join(os.getcwd() + "/exp3_stddev_" + location + "/exp" + str(i) + "/csv", filename), 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    # ignore first line
                    if not first_line:
                        print(row[-3])
                        file.write(row[-3])
                        file.write("\n")
                    else:
                        first_line = False
