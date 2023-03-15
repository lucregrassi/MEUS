# loading in modules
import sqlite3
import pandas as pd
import csv


def from_db_table_to_csv(csv_filename):
    dbfile = "databaseMEUS.db"
    # Create a SQL connection to the database
    conn = sqlite3.connect(dbfile)

    # Get the info_history_table and export it to csv
    sql_query = pd.read_sql_query("SELECT * FROM info_history_tab", conn)
    sql_query.to_csv(csv_filename, index=False)

    # Close the connection
    conn.close()


def count_contributing_agents(csv_filename, output_filename):
    with open(csv_filename) as f:
        csv_file = csv.DictReader(f)
        observers = []
        contributing_agents = []

        # iterating over each row and append
        # values to empty list
        for row in csv_file:
            observers.append(row['observer'])
            contributing_agents.append(row['a1'])
            contributing_agents.append(row['a2'])

        n_observers = len(set(observers))
        n_contributing_agents = len(set(contributing_agents))

    header = ['n_observers', 'n_contributors']
    data = [n_observers, n_contributing_agents]

    with open(output_filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write the data
        writer.writerow(data)