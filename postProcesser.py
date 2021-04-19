import csv
import json
import statistics
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt


plt.style.use('fivethirtyeight')

fieldnames = ["sizeTab1_mean", "sizeTab2_mean",\
         "duration", "perc_of_seen_events",
                 "latency_mean", "num_loops"]


# db_size         = pd.read_csv('db_size.csv')
performances    = pd.read_csv('performances.csv')
experiments     = pd.read_csv('experiments.csv')

sizeTab1        = experiments['sizeTab1']
sizeTab2        = experiments['sizeTab2']
time            = performances['time']
perc_events     = performances['perc_of_seen_events']
latency         = experiments['latency']
num_loops       = experiments['num_loops']
# events          = experiments['event']

# pprint(latency)
# input()

# print(experiments)
# print(latency)
# input()

# events_list = []
# events_list.append([])
# counter1 = 0
# for i in range(len(events)):
#         if events[i] != '#':
#                 print(events[i])
#                 events[i] = json.loads(str(events[i]))
#                 events_list.append(events[i])
#         elif events[i] == '#':
#                 events_list.append([])
#                 counter1 += 1
#         else:
#                 print("Somethings wrong")

# count = 0
# while(events.remove('#'))
# {
#         print("I have removed yet another")
#         count += 1
# }

# print(events)
# print(type(events))
# print(events[0])
# print(type(events[0]))
# pprint(events_list)
# input()

# pprint(sizeTab1_tmp)
# print(sizeTab1_tmp)

# sizeTab1 = []
# sizeTab2 = []
# # sizeTab1.append([])
# # sizeTab2.append([])
# counter = 0

# for i in range(len(sizeTab1_tmp)):
#         # if sizeTab1_tmp[i] != '#':
#                 sizeTab1.append(sizeTab1_tmp[i])
#                 sizeTab2.append(sizeTab2_tmp[i])
#         # elif sizeTab1_tmp[i]=='#':
#         #         sizeTab1.append([])
#         #         sizeTab2.append([])
#         #         counter += 1
#         #         # pprint(sizeTab1[counter])
#         # else:
#         #         print("Somethings wrong!")

# sizeTab1.pop()
# sizeTab2.pop()
# # pprint(sizeTab1)

# # sum_list1 = []
# # sum_list2 = []
# sums1 = 0
# sums2 = 0
# for i in range(len(sizeTab1)):
#         # for j in range(len(sizeTab1[i])):
#         #         sums1 += int(sizeTab1[i][j])
#         #         sums2 += int(sizeTab2[i][j])
#         sums1 += int(sizeTab1[i])
#         sums2 += int(sizeTab2[i])
#         # sum_list1.append(sums1)
        # sum_list2.append(sums2)


print(f"mean for size of the first Tab in the db in this batch is                       {statistics.mean(sizeTab1):0.2f} rows")
print(f"mean for size of the second Tab in the db in this batch is                      {statistics.mean(sizeTab2):0.2f} rows")
print(f"mean for duration of the experiments in this batch is                           {statistics.mean(time):0.2f} seconds")
print(f"mean for the percentage of seen events in this batch is                         {statistics.mean(perc_events):0.2f}%")
print(f"mean for the latency of the events to be loaded on the db in this batch is      {statistics.mean(latency):0.2f} loops")


with open('/Users/mario/Desktop/experiments/100/Amatrice/seed28_t20/70%.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            info = {
                    'sizeTab1_mean':                    statistics.mean(sizeTab1),
                    'sizeTab2_mean':                    statistics.mean(sizeTab2),
                    'duration':                         statistics.mean(time),
                    'perc_of_seen_events':              statistics.mean(perc_events),
                    'latency_mean':                     statistics.mean(latency),
                    'num_loops':                        statistics.mean(num_loops)
            }

            csv_writer.writerow(info)

# plt.plot()