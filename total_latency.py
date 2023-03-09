avg_path = "experiments/Assisi/epidemic/1_GA_ratio/exp3_10K_200GA"

with open(avg_path + '/stats/total_latency.csv', 'w') as f:
    lats = []
    with open(avg_path + '/sent_to_db_loop.csv', 'r') as file:
        for line in file.readlines()[1:]:
            lats.append(int(line))
    avg = sum(lats) / len(lats)
    f.write(str(avg))