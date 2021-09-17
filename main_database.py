import csv
import json
import logging
import statistics
from pprint import pprint
from collections import Counter
from flask import Flask, request
from utils import NewpreProcessing
from collections import defaultdict
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_restful import Api, reqparse, abort, fields, marshal_with, inputs
from marshmallow import Schema, fields as mafields, ValidationError, INCLUDE, EXCLUDE, pre_load

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databaseMEUS.db'
db = SQLAlchemy(app)
# ma = Marshmallow(app)



# -- MODEL --

class dirObsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    when            = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    # Information element or direct observation
    who             = db.Column(db.Integer, nullable=False)
    info_histories  = db.relationship('infoHistoryTab', backref="dir_obs_tab", lazy=True)

    def __repr__(self):
        return f"dirObsTab(id = {id}, situation = {situation}\n object = {obj}\n when = {when}\n where = {where}\n who = {who}\n"


class infoHistoryTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    dir_obs_id      = db.Column(db.Integer, db.ForeignKey("dir_obs_tab.id"))
    observer        = db.Column(db.Integer, nullable=False)
    a1              = db.Column(db.Integer, nullable=False)
    a2              = db.Column(db.Integer, nullable=False)
    sender          = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    when            = db.Column(db.Integer, nullable=False)
    sent_at_loop    = db.Column(db.Integer, nullable=False)
    sent_where      = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"InfohistoryTab(id = {id}\n dir_obs_id = {dir_obs_id}\n \
                    observer = {observer}\n a1 = {a1}\n a2 = {a2}\n sender = {sender}\n \
                        where = {where}\n when = {when}\n sent_at_loop = {sent_at_loop}\n \
                            sent_where = {sent_where}\n)"


class eventsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    observations    = db.relationship('observedEventsTab', backref='events_tab', lazy=True)


class observedEventsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('events_tab.id'), nullable=False)
    obs_situation   = db.Column(db.String(50), nullable=False)
    obs_object      = db.Column(db.String(50), nullable=False)
    confidence      = db.Column(db.Float, nullable=False)


class agentsVotesTab(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    agents_id   = db.Column(db.Integer, nullable=False)
    when        = db.Column(db.Integer, nullable=False)
    where       = db.Column(db.Integer, nullable=False)
    t_f         = db.Column(db.Integer, nullable=False)
    cons        = db.Column(db.String(50), nullable=False)

class latencyTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    when            = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    who             = db.Column(db.Integer, nullable=False)
    lat             = db.Column(db.Integer, nullable=False)


##### SCHEMAS #####


class dirObsSchema(Schema):
    id                  = mafields.Integer(dump_only=True)
    dir_obs             = mafields.Dict(keys=mafields.Str(), values=mafields.Str())
    situation           = mafields.Str()
    obj                 = mafields.Str()
    when                = mafields.Integer()
    where               = mafields.Integer()
    who                 = mafields.Integer()


class infoHistorySchema(Schema):
    id              = mafields.Integer(dump_only=True)
    observer        = mafields.Integer()
    a1              = mafields.Integer()
    a2              = mafields.Integer()
    sender          = mafields.Integer()
    where           = mafields.Integer()
    when            = mafields.Integer()
    sent_at_loop    = mafields.Integer()
    sent_where      = mafields.Integer()



do_schema   = dirObsSchema()
do_schemas  = dirObsSchema(many=True)
ih_schema   = infoHistorySchema()
ih_schemas  = infoHistorySchema(many=True)



events  = []
events_dict = {}

agents_perf  = {}


@app.route("/IE/events", methods=["PUT"])
def receiving_events_list():


    json_data = json.loads(request.data)
    events.extend(json_data['events'])


    # filling up the first event tab in the db
    for event in events:
        ev = eventsTab( situation   = event['situation'],
                        obj         = event['object'],
                        where       = event['where'])
        db.session.add(ev)
        db.session.commit()
        events_dict[str(ev.id)]     = {'obs': [], 'reps': [], 'whos': [], 'whens': []}

    return{"message": "registered events in the environments", "events": events}




@app.route("/IE/<int:DO_id>", methods=["PUT"])
def put(DO_id):

    json_data           = json.loads(request.data)
    data_do, data_ih    = NewpreProcessing(json_data)

    all_events_db = False
    flag = False
    return_flag = False
    repetition_flag = False
    if not data_do:
        return {"message": "No input data provided"}, 400
    # Validate and deserialize input
    elif not data_ih:
        flag = True
    info_history = []
    try:
        direct_obs = do_schemas.load(data_do)#, unknown=INCLUDE)
        for nest in data_ih:
            info_history.append(ih_schemas.load(nest))

    except ValidationError as err:
        return err.messages, 422

    result_do   = []
    latency = []


    for i, dobs in enumerate(direct_obs):

        retro_whos = []
        retro_reps = []
        
        events_types    = []
        query_ev        = eventsTab.query.filter_by(where=dobs['where']).first()

        ev_id = str(query_ev.id)
        ag_id = str(dobs['who'])
        


        # First 2 tabs in the db
        query_do = dirObsTab.query.filter_by(   situation   = dobs['situation'],
                                                obj         = dobs['obj'],
                                                when        = dobs['when'],
                                                where       = dobs['where'],
                                                who         = dobs['who']).first()



        # if the direct observation is not in the db
        if not query_do:
            return_flag = True
            result_ih = []

            do  = dirObsTab(    situation       = dobs['situation'],
                                obj             = dobs['obj'],
                                where           = dobs["where"],
                                when            = dobs["when"],
                                who             = dobs["who"])


            # ackowledging we are adding a new direct observation to the db
            elem = {'situation': do.situation, 'object': do.obj, 'where': do.where, 'who': do.who}
            for n, el in enumerate(events):
                # if the observation corresponds to the actual situation
                if el['situation'] == elem['situation'] and el['object'] == elem['object'] and el['where']==elem['where']:
                    try:
                        if events[n]['correct']==0 and events[n]['mistaken']['times']==0:
                            latency.append({
                                'sender':       info_history[i][0]['sender'],
                                'sit':          dobs['situation'],
                                'obj':          dobs['obj'],
                                'when':         dobs['when'],
                                'where':        dobs['where'],
                                'who':          dobs['who'],
                                'sent_at_loop': info_history[i][0]['sent_at_loop']
                            })
                            events[n]['first_time'] = 1

                            
                        events[n]['correct'] += 1
                    except Exception as err:
                        raise err

                # if the element is a "distorted" observation instead
                elif (el['situation'] != elem['situation'] or el['object'] != elem['object']) and el['where'] == elem['where']:

                    if events[n]['correct']==0 and events[n]['mistaken']['times']==0:
                        latency.append({
                                'sender':       info_history[i][0]['sender'],
                                'sit':          dobs['situation'],
                                'obj':          dobs['obj'],
                                'when':         dobs['when'],
                                'where':        dobs['where'],
                                'who':          dobs['who'],
                                'sent_at_loop': info_history[i][0]['sent_at_loop']
                            })
                        events[n]['first_time'] = 1

                    events[n]['mistaken']['times'] += 1
                    events[n]['mistaken']['difference'].append(elem)

        
            if not flag:
                for j, val in enumerate(info_history[i]):
                    ih = infoHistoryTab(    observer        = info_history[i][j]['observer'],
                                            a1              = info_history[i][j]['a1'],
                                            a2              = info_history[i][j]['a2'],
                                            sender          = info_history[i][j]['sender'],
                                            where           = info_history[i][j]['where'],
                                            when            = info_history[i][j]['when'],
                                            sent_at_loop    = info_history[i][j]['sent_at_loop'],
                                            sent_where      = info_history[i][j]['sent_where'])
                    db.session.add(ih)
                    do.info_histories.append(ih)
                    do.info_histories[do.info_histories.index(ih)].dir_obs_id = do.id
                    result_ih.append(ih_schema.dump(ih))
                result_do.append(result_ih)
            print("10")
        # if the direct observation is already in the db
        else:
            repetition_flag = True
            
            # if all the events have been seen
            if len(events) == 0:
                all_events_db = True
            result_ih = []
            if not flag:
                for j, val in enumerate(info_history[i]):
                    query_ih = infoHistoryTab.query.filter_by(  observer        = info_history[i][j]['observer'],
                                                                a1              = info_history[i][j]['a1'],
                                                                a2              = info_history[i][j]['a2'],
                                                                sender          = info_history[i][j]['sender'],
                                                                where           = info_history[i][j]['where'],
                                                                when            = info_history[i][j]['when'],
                                                                sent_at_loop    = info_history[i][j]['sent_at_loop'],
                                                                sent_where      = info_history[i][j]['sent_where']).first()

                    if not query_ih:
                        ih = infoHistoryTab(    observer        = info_history[i][j]['observer'],
                                                a1              = info_history[i][j]['a1'],
                                                a2              = info_history[i][j]['a2'],
                                                sender          = info_history[i][j]['sender'],
                                                where           = info_history[i][j]['where'],
                                                when            = info_history[i][j]['when'],
                                                sent_at_loop    = info_history[i][j]['sent_at_loop'],
                                                sent_where      = info_history[i][j]['sent_where'])

                        db.session.add(ih)
                        query_do.info_histories.append(ih)

                        query_do.info_histories[query_do.info_histories.index(ih)].dir_obs_id = query_do.id
                        result_ih.append(ih_schema.dump(ih))

                result_do.append(result_ih)
            print("11")

    print("12")

    db.session.commit()


    # keep track if the event has been uploaded on the db for the first time
    if return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, "events": events, 'latency': latency}
    elif not return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do}



@app.route("/IE/<int:DO_id>", methods=["DELETE"])
def delete(DO_id):

    query           = dirObsTab.query.options(joinedload(dirObsTab.info_histories))
    query_events    = eventsTab.query.options(joinedload(eventsTab.observations))
    ag_votes        = agentsVotesTab.query.all()
    lat_tab         = latencyTab.query.all()

    for v in ag_votes:
        db.session.delete(v)
    
    for l in lat_tab:
        db.session.delete(l)

    counter1 = 0
    counter2 = 0


    for Obs in query:
        for jump in Obs.info_histories:
            db.session.delete(jump)
            counter2 += 1
        db.session.delete(Obs)
        counter1 += 1
    
    # clearing up events Tabs
    for event in query_events:
        for observed_event in event.observations:
            db.session.delete(observed_event)
        db.session.delete(event)
    db.session.commit()

    events.clear()
    events_dict.clear()


    return {"message": "tabs are cleared", "size_tab1": counter1, "size_tab2": counter2}


if __name__=="__main__":
    app.run(debug=True)
