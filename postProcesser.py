import csv
import statistics
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

fieldnames = ["sizeTab1_mean", "sizeTab2_mean",
              "duration", "perc_of_seen_events",
              "latency"]

db_size         = pd.read_csv('db_size.csv')
performances    = pd.read_csv('performances.csv')
experiments     = pd.read_csv('experiments.csv')

sizeTab1_tmp    = db_size['sizeTab1']
sizeTab2_tmp    = db_size['sizeTab2']
time            = performances['time']
perc_events     = performances['perc_of_seen_events'] 
latency         = experiments['latency']


print(statistics.mean(time))
sizeTab1 = []
sizeTab2 = []
counter = 0

for i in range(len(sizeTab1_tmp)):
        sizeTab1.append(sizeTab1_tmp[i])
        sizeTab2.append(sizeTab2_tmp[i])

sizeTab1.pop()
sizeTab2.pop()

# print(sizeTab1)
# print(sizeTab2)

sums1 = 0
sums2 = 0
for i in range(len(sizeTab1)):
        sums1 += int(sizeTab1[i])
        sums2 += int(sizeTab2[i])


print(f"mean for size of the first Tab in the db in this batch is                       {sums1:0.2f} rows")
print(f"mean for size of the second Tab in the db in this batch is                      {sums2:0.2f} rows")
print(f"mean for duration of the experiments in this batch is                           {statistics.mean(time):0.2f} seconds")
print(f"mean for the percentage of seen events in this batch is                         {statistics.mean(perc_events):0.2f}%")
print(f"mean for the latency of the events to be loaded on the db in this batch is      {statistics.mean(latency):0.2f} loops")


with open('results/50%-9-1over10.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            info = {
                    'sizeTab1_mean': sums1,
                    'sizeTab2_mean': sums2,
                    'duration': round(statistics.mean(time), 2),
                    'perc_of_seen_events': round(statistics.mean(perc_events), 2),
                    'latency': round(statistics.mean(latency), 2)
            }

            csv_writer.writerow(info)

# plt.plot()