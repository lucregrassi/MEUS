# MEUS
This project in Python 3 allows to simulate the behaviour of people moving between the nodes of a graph imported from OpenStreetMap.
Each node contains the information about how many people are in that node, and which kind of connection is available.

## How to create a virtual env and install dependencies

```
conda config --prepend channels conda-forge
conda create -n <name_of_your_env> --strict-channel-priority osmnx
```
To install dependencies:
```
pip install -r requirements.txt
```

## Import the graph
Open the script save_graph.py, and set the parameter _place_ based on the location you want to run your simulation in.
To save the graph of the specified location open the terminal in the project folder and run:
```
python3 save_graph.py
```

## Initialize global connections
To setup the global connections in the graph (4G, 5G and Wi-Fi), open the terminal and run:
```
python3 connectivity.py
```

## Start the simulation
Now that the graph is ready, you can start the simulation. 
To change the simulation parameters, open the script explore_graph.py: you can set the number of people moving in the graph, the number of iterations, and the distance traveled by each person in each loop.
Once all the parameters have been set, open the terminal and type:
```
python3 explore_graph.py
```
For each loop, this script will print the state of each person in the graph and it will eventually generate a GIF containing the result of the simulation. 
