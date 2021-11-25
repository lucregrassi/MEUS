# MEUS: Management of Emergencies through Ubiquitous Sensing
This project in Python 3 allows to simulate the behaviour of people moving between the nodes of a graph imported from OpenStreetMap.
Each node contains the information about how many people are in that node, and which kind of connection is available.

## How to create a virtual env and install dependencies

``` 
$ conda config --prepend channels conda-forge
$ conda create -n <env> --strict-channel-priority osmnx
$ conda activate <env>
```
To install dependencies:
```
$ pip install -r requirements.txt
```

## Launch local server and set up database
run the command ```python main_database3.py```
copy the base address which will show up in the terminal upon launching the script.
Open a python shell and type:
```
>> from main_database3 import db
>> db.reate_all()
```
This command has generated the database file where to store the data from the simulation.

## Start the simulation
To change the simulation parameters type the -h flag to get help and change parameters ($python main.py -h): you can set the number of people moving in the graph, the number of iterations, and the distance traveled by each person in each loop.
To run the simulation with default parameters, open the terminal and type:
```
$ python main.py
```
## Database structure
The database has 2 main tables:
1)"dir_obs_tab": 
```
class dirObsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)                             # Integer uniquely identifying the entry in the db
    situation       = db.Column(db.String(50), nullable=False)                            # situation "field" of an event
    obj             = db.Column(db.String(50), nullable=False)                            # object "field" of an event
    when            = db.Column(db.Integer, nullable=False)                               # loop at which the event=(situation, object) has ben observed
    where           = db.Column(db.Integer, nullable=False)                               # node wherein the observation has occurred
    who             = db.Column(db.Integer, nullable=False)                               # agent who has made the observation
    info_histories  = db.relationship('infoHistoryTab', backref="dir_obs_tab", lazy=True) # relation with the history_tab
```
2)"info_history_tab":
```
class infoHistoryTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)                 # Integer uniquely identifying the entry in the db
    dir_obs_id      = db.Column(db.Integer, db.ForeignKey("dir_obs_tab.id"))  # integer saying to which observation this jump is belonging to
    observer        = db.Column(db.Integer, nullable=False)                   # who has made the observation (= to the who field of the dir_obs_tab)
    a1              = db.Column(db.Integer, nullable=False)                   # agent communicating the info
    a2              = db.Column(db.Integer, nullable=False)                   # agent the receiving the info
    sender          = db.Column(db.Integer, nullable=False)                   # agent who has sent the info to the db (It has to be a gateway agent)
    where           = db.Column(db.Integer, nullable=False)                   # node wherein the communication has taken place
    when            = db.Column(db.Integer, nullable=False)                   # loop at which the communication has taken place
    sent_at_loop    = db.Column(db.Integer, nullable=False)                   # loop at which the info has been sent to the db
    sent_where      = db.Column(db.Integer, nullable=False)                   # node in which the info has been sent to the db
```

Each field in each class corresponds to a column in the respective db tab. This structure allows to have the possibility, given the unique direct observation, to track how this information has traveled among agent's iEs prior to being stores in the db.
It has to be noticed that whenever the simulation is interrupted before its completion the database has to be cleared as well. To do so:
open a python shell and run the following command
```
>> import requests
>> requests.delete(<base_address> + 'IE/1')
```

## Authors
| Name | E-mail |
|------|--------|
| Lucrezia Grassi| lucrezia.grassi@edu.unige.it |
| Mario Ciranni | mario.ciranni@gmail.com |
