import pandas as pd
import matplotlib.pyplot as plt


plt.style.use('fivethirtyeight')


db_size = pd.read_csv('/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/db_size.csv')

sizeTab1 = db_size['sizeTab1']
sizeTab2 = db_size['sizeTab2']

for el in sizeTab1:
    if el=='#':
        print("oki")