import os
import csv
import json
import copy
import logging
import itertools
import numpy as np
import krippendorff
from pprint import pprint
from flask import Flask, request
from flask_restful import Api, fields
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields as mafields, ValidationError
from utils import NewpreProcessing, compute_KrippendorffAlpha, compute_CVR, logger, cvr as CVR


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']    = False
app.config['SQLALCHEMY_DATABASE_URI']           = 'sqlite:///databaseMEUS.db'
db = SQLAlchemy(app)
# ma = Marshmallow(app)



# -- MODEL --
class dirObsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    when            = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    who             = db.Column(db.Integer, nullable=False)
    info_histories  = db.relationship('infoHistoryTab', backref="dir_obs_tab", lazy=True)

    # def __repr__(self):
    #     return f"dirObsTab(id = {id}, situation = {situation}\n object = {obj}\n when = {when}\n where = {where}\n who = {who}\n"


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

    # def __repr__(self):
    #     return f"InfohistoryTab(id = {id}\n dir_obs_id = {dir_obs_id}\n \
    #                 observer = {observer}\n a1 = {a1}\n a2 = {a2}\n sender = {sender}\n \
    #                     where = {where}\n when = {when}\n sent_at_loop = {sent_at_loop}\n \
    #                         sent_where = {sent_where}\n)"


class eventsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    observations    = db.relationship('observedEventsTab', backref='events_tab', lazy=True)
    # ratings         = db.relationship('ratingsTab', backref='events_tab', lazy=True)


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
agents_dict = {}
events_dict = {}

agents_dict2 = {}
agents_perf  = {}
events_dict2 = {}
gateways = 10

CVR_performace      = {'correct': 0, 'times': 0}
Kalpha_performance  = {'corect': 0, 'times': 0}


outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/'
fields = ['Ncoders', 'who', 'when', 'what', 'observations', 'ground_truth', 'distance', 'CVR', 'Kalpha']


@app.route("/IE/events", methods=["PUT"])
def receiving_events_list():

    json_data = json.loads(request.data)
    events.extend(json_data['events'])
    global gateways
    gateways = json_data['n_gateways']

    print('gateways:', gateways)

    CVR_performace['correct']   = 0
    CVR_performace['times']     = 0


    # filling up the first event tab in the db
    for event in events:
        ev = eventsTab( situation   = event['situation'],
                        obj         = event['object'],
                        where       = event['where'])
        db.session.add(ev)
        db.session.commit()
        events_dict[str(ev.id)]     = {'obs': [], 'reps': [], 'whos': [], 'whens': []}
        events_dict2[str(ev.id)]    = {'obs': [], 'reps': [], 'reps1': [], 'whos': [], 'votes': [], 'times': [], 'whens': [], 'rels': []}
    
    for agent in range(json_data['n_agents']):
        agents_dict[str(agent)]     = {'positive': 0, 'negative': 0, 'times': 0}
        agents_dict2[str(agent)]    = {'positive': 0, 'negative': 0, 'times': 0, 'weight': 1}
        agents_perf[str(agent)]     = []

    pprint(events)

    return{"message": "registered events in the environments", "events": events}


@app.route("/IE/<int:e_id>/<sit>/<obj>", methods=['GET'])
def get(e_id,sit,obj):

    event_query = eventsTab.query.filter_by(id=id).first()
    
    outcome = True if event_query.situation==sit and event_query.obj==obj else False

    return {'coorect_event': outcome}



@app.route("/IE/<int:DO_id>", methods=["PUT"])
def put(DO_id):

    json_data                   = json.loads(request.data)
    data_do, data_ih, distances = NewpreProcessing(json_data)


    all_events_db   = False
    flag            = False
    return_flag     = False
    repetition_flag = False

    if not data_do:
        return {"message": "No input data provided"}, 400

    # Validate and deserialize input
    elif not data_ih:
        flag = True
    info_history = []
    try:
        direct_obs = do_schemas.load(data_do)
        for nest in data_ih:
            info_history.append(ih_schemas.load(nest))

    except ValidationError as err:
        return err.messages, 422

    result_do   = []
    reputations = []
    reputations2 = []
    events2 = []
    latency = []

    ids = []

    ag_ids      = []
    ag_weights  = []

    for i, dobs in enumerate(direct_obs):
        
        events_types    = []
        query_ev        = eventsTab.query.filter_by(where=dobs['where']).first()

        ev_id = str(query_ev.id)
        ag_id = str(dobs['who'])

        try:

            ''' Reputation based on a voting approach '''
            token=0
            # observations = dirObsTab.query.filter_by(where=dobs['where']).all()
            # observers    = [observations[i].who for i in range(len(observations))]
            # evs          = set(json.dumps(  {'situation': observations[i].situation,
            #                                     'object': observations[i].obj}) for i in range(len(observations)))
            # evs          = [json.loads(d) for d in evs]

            # pprint(observers)
            # print(dobs['who'])
            # print("ev_id:", ev_id)

            # avoiding any redundant information about a certain event:
            # an agent cannot say twice his observation about one event.
            # print(list(np.any(dobs['who'] in nest for nest in events_dict2[ev_id]['whos'])))
            # print(bool(not np.any(dobs['who'] in nest for nest in events_dict2[ev_id]['whos'])))
            # print(not any(dobs['who'] in nest for nest in events_dict2[ev_id]['whos']))
            # print(bool(not any(dobs['who'] in nest for nest in events_dict2[ev_id]['whos'])))
            # input()
            if not any(dobs['who'] in nest for nest in events_dict2[ev_id]['whos']):
                if {'situation': dobs['situation'], 'object': dobs['obj']} not in events_dict2[ev_id]['obs']:

                    events_dict2[ev_id]['obs'].append({      'situation':   dobs['situation'],
                                                                'object':   dobs['obj']})

                    events_dict2[ev_id]['whos'].append([dobs['who']])
                    events_dict2[ev_id]['times'].append([1])
                    if dobs['who']>gateways:
                        events_dict2[ev_id]['votes'].append(2)
                    else:
                        events_dict2[ev_id]['votes'].append(6)

                    events_dict2[ev_id]['whens'].append([[dobs['when']]])
                    events_dict2[ev_id]['rels'].append([(len(events_dict2[ev_id]['obs'])-1, dobs['who'])])


                    # for ag in events_dict2[ev_id]['whos'][-1]:
                    #     if ag<gateways:
                    #         agents_dict2[str(ag)]['weight'] += 1

                    #         ag_ids.append(ag)
                    #         ag_weights.append(agents_dict2[ag_id]['weight'])

                    # for ag in list(itertools.chain(events_dict2[ev_id]['whos'][i] for i in range(len(events_dict2[ev_id]['whos'])-1))):
                    #     if ag<gateways:
                    #         agents_dict2[str(ag)]['weight'] -= 1
                        
                    #         ag_ids.append(ag)
                    #         ag_weights.append(agents_dict2[ag]['weight'])


                    '''CVR method'''
                    input("im in")
                    cvr_res = compute_CVR( events_dict2[ev_id], query_ev, CVR, gateways)
                    logger( ev_id,
                            dobs['who'],
                            dobs['when'],
                            events_dict2[ev_id],
                            cvr_res,
                            round(compute_KrippendorffAlpha(events_dict2[ev_id], gateways), 3),
                            outpath,
                            fields,
                            query_ev,
                            gateways,
                            distances[i])


                else:
                    index = events_dict2[ev_id]['obs'].index({'situation': dobs['situation'], 'object': dobs['obj']})

                    token = 1

                    # if this agent has not reported this observation before
                    if dobs['who'] not in events_dict2[ev_id]['whos'][index]:

                        events_dict2[ev_id]['whos'][index].append(dobs['who'])
                        events_dict2[ev_id]['whens'][index].append([dobs['when']])
                        if dobs['who'] > gateways:
                            events_dict2[ev_id]['votes'][index] += 2
                        else:
                            events_dict2[ev_id]['votes'][index] += 6

                        index2 = events_dict2[ev_id]['whos'][index].index(dobs['who'])
                        events_dict2[ev_id]['times'][index].append(1)

                        events_dict2[ev_id]['rels'][index].append((index, dobs['who']))


                        # if dobs['who']>gateways:
                        #     if any(ag<gateways for ag in events_dict2[ev_id]['whos'][-1]):
                        #         agents_dict2[ag_id]['weight'] += 1

                        #         ag_ids.append(ag_id)
                        #         ag_weights.append(agents_dict2[ag_id]['weight'])

                        #     elif any(ag<gateways for ag in list(itertools.chain(events_dict2[ev_id]['whos'][i] for i in range(len(events_dict2[ev_id]['whos'])-1))) ):
                        #         agents_dict2[ag_id]['weight'] -= 1
                            
                        #         ag_ids.append(ag_id)
                        #         ag_weights.append(agents_dict2[ag_id]['weight'])


                        '''CVR method'''
                        cvr_res = compute_CVR(events_dict2[ev_id], query_ev, CVR, gateways)

                        logger( ev_id,
                                dobs['who'],
                                dobs['when'],
                                events_dict2[ev_id],
                                cvr_res,
                                round(compute_KrippendorffAlpha(events_dict2[ev_id], gateways), 3),
                                outpath,
                                fields,
                                query_ev,
                                gateways,
                                distances[i])
                    else:
                        token=3

            new_weights = {str(i):j for i in ag_ids for j in ag_weights} if not token==3 else {}


        except Exception as error:
            raise error
        

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

            do = dirObsTab( situation       = dobs['situation'],
                            obj             = dobs['obj'],
                            where           = dobs["where"],
                            when            = dobs["when"],
                            who             = dobs["who"])
 

            # ackowledging we are adding a new direct observation to the db
            elem = {'situation': do.situation, 'object': do.obj, 'where': do.where, 'who': do.who}

                # if the observation corresponds to the actual situation
            if (query_ev.situation == elem['situation'] and query_ev.obj == elem['object']) and query_ev.where==elem['where']:
                try:
                    if events[query_ev.id-1]['correct']==0 and events[query_ev.id-1]['mistaken']['times']==0:
                        latency.append({
                            'sender':       info_history[i][0]['sender'],
                            'sit':          dobs['situation'],
                            'obj':          dobs['obj'],
                            'when':         dobs['when'],
                            'where':        dobs['where'],
                            'who':          dobs['who'],
                            'sent_at_loop': info_history[i][0]['sent_at_loop']
                        })
                        events[query_ev.id-1]['first_time'] = 1

                    events[query_ev.id-1]['correct'] += 1

                except Exception as err:
                    raise err

            # if the element is a "distorted" observation instead
            elif (query_ev.situation != elem['situation'] or query_ev.obj != elem['object']) and query_ev.where == elem['where']:

                if events[query_ev.id-1]['correct']==0 and events[query_ev.id-1]['mistaken']['times']==0:
                    latency.append({
                            'sender':       info_history[i][0]['sender'],
                            'sit':          dobs['situation'],
                            'obj':          dobs['obj'],
                            'when':         dobs['when'],
                            'where':        dobs['where'],
                            'who':          dobs['who'],
                            'sent_at_loop': info_history[i][0]['sent_at_loop']
                        })
                    events[query_ev.id-1]['first_time'] = 1

                events[query_ev.id-1]['mistaken']['times'] += 1
                events[query_ev.id-1]['mistaken']['difference'].append(elem)

            else:
                input()

        
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
    db.session.commit()

    # keep track if the event has been uploaded on the db for the first time
    if return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, "events": events, 'latency': latency, 'reputation': reputations, 'reputation2': reputations2, 'weights': new_weights}
    elif not return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, 'reputation': reputations, 'reputation2': reputations2, 'weights': new_weights}



@app.route("/IE/<int:DO_id>", methods=["DELETE"])
def delete(DO_id):

    print(CVR_performace['correct'])
    print(CVR_performace['times'])
    # print(round((CVR_performace['correct'] / CVR_performace['times'])*100, 3))

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

    # counter1 = dirObsTab.query.count()
    # counter2 = infoHistoryTab.query.count()

    # dirObsTab.query.delete()
    # infoHistoryTab.query.delete()
    # eventsTab.query.delete()
    # observedEventsTab.query.delete()
    # agentsVotesTab.query.delete()
    # latencyTab.query.delete()
    
    # clearing up events Tabs
    for event in query_events:
        for observed_event in event.observations:
            db.session.delete(observed_event)
        db.session.delete(event)
    db.session.commit()

    events.clear()
    agents_dict.clear()
    events_dict.clear()


    return {"message": "tabs are cleared", "size_tab1": counter1, "size_tab2": counter2, "events_dict2": events_dict2, "agents_perf": agents_perf}


if __name__=="__main__":
    app.run(debug=True)#, threaded=True)