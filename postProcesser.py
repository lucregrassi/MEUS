import csv
import json
import statistics
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt


plt.style.use('fivethirtyeight')

fieldnames = ["sizeTab1_mean", "sizeTab1_stdev", "sizeTab2_mean", "sizeTab2_stdev",\
         "duration_mean", "duration_stdev", "perc_of_seen_events_mean", "perc_of_seen_events_stdev",\
                 "latency_mean", "latency_stdev"]


db_size         = pd.read_csv('/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/db_size.csv')
performances    = pd.read_csv('/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/performances.csv')
experiments     = pd.read_csv('/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/experiments.csv')

sizeTab1_tmp    = db_size['sizeTab1']
sizeTab2_tmp    = db_size['sizeTab2']
time            = performances['time']
perc_events     = performances['perc_of_seen_events'] 
latency         = experiments['latency']
# events          = experiments['event']


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
print(sizeTab1_tmp)

sizeTab1 = []
sizeTab2 = []
sizeTab1.append([])
sizeTab2.append([])
counter = 0

for i in range(len(sizeTab1_tmp)):
        if sizeTab1_tmp[i] != '#':
                sizeTab1[counter].append(sizeTab1_tmp[i])
                sizeTab2[counter].append(sizeTab2_tmp[i])
        elif sizeTab1_tmp[i]=='#':
                sizeTab1.append([])
                sizeTab2.append([])
                counter += 1
                # pprint(sizeTab1[counter])
        else:
                print("Somethings wrong!")

sizeTab1.pop()
sizeTab2.pop()
# pprint(sizeTab1)

sum_list1 = []
sum_list2 = []
for i in range(len(sizeTab1)):
        sums1 = 0
        sums2 = 0
        for j in range(len(sizeTab1[i])):
                sums1 += int(sizeTab1[i][j])
                sums2 += int(sizeTab2[i][j])
        sum_list1.append(sums1)
        sum_list2.append(sums2)

# print(latency)
# input()

print(f"mean for size of the first Tab in the db in this batch is                       {statistics.mean(sum_list1):0.2f} rows")
print(f"mean for size of the second Tab in the db in this batch is                      {statistics.mean(sum_list2):0.2f} rows")
print(f"mean for duration of the experiments in this batch is                           {statistics.mean(time):0.2f} seconds")
print(f"mean for the percentage of seen events in this batch is                         {statistics.mean(perc_events):0.2f}%")
print(f"mean for the latency of the events to be loaded on the db in this batch is      {statistics.mean(latency):0.2f} loops")


with open('/Users/mario/Desktop/experiments_new/50/20-1over10-5Antonio.csv', 'w') as csv_file:#Fellowship_Unige/MEUS/MEUS/experiments/100-1over20-9/100-1over20-9.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            info = {
                    'sizeTab1_mean':                    statistics.mean(sum_list1),
                    'sizeTab1_stdev':                   statistics.stdev(sum_list1),
                    'sizeTab2_mean':                    statistics.mean(sum_list2),
                    'sizeTab2_stdev':                   statistics.stdev(sum_list2),
                    'duration_mean':                    statistics.mean(time),
                    'duration_stdev':                   statistics.stdev(time),
                    'perc_of_seen_events_mean':         statistics.mean(perc_events),
                    'perc_of_seen_events_stdev':        statistics.stdev(perc_events),
                    'latency_mean':                     statistics.mean(latency),
                    'latency_stdev':                    statistics.stdev(latency)
            }

            csv_writer.writerow(info)

# plt.plot()