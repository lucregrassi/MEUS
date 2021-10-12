import os
import csv
import json
import logging
import itertools
import statistics
import numpy as np
import krippendorff
from pprint import pprint
from collections import Counter
from flask import Flask, request
from utils import NewpreProcessing, compute_KrippendorffAlpha, compute_CVR, logger
from collections import defaultdict
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_restful import Api, reqparse, abort, fields, marshal_with, inputs
from marshmallow import Schema, fields as mafields, ValidationError, INCLUDE, EXCLUDE, pre_load

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    # class Meta:
    #     unknown=INCLUDE
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



# content validity ratio critical values per size rater's panel
CVR = {
    5: 5,
    6: 6,
    7: 7,
    8: 7,
    9: 8,
    10: 9,
    11: 9,
    12: 10,
    13: 10,
    14: 11,
    15: 12,
    16: 12,
    17: 13,
    18: 13,
    19: 14,
    20: 15,
    21: 15,
    22: 16,
    23: 16,
    24: 17,
    25: 18,
    26: 18,
    27: 19,
    28: 19,
    29: 20,
    30: 20,
    31: 21,
    32: 22,
    33: 22,
    34: 23,
    35: 23,
    36: 24,
    37: 24,
    38: 25,
    39: 26,
    40: 26
}

events  = []
agents_dict = {}
events_dict = {}

agents_dict2 = {}
agents_perf  = {}
events_dict2 = {}

CVR_performace      = {'correct': 0, 'times': 0}
Kalpha_performance  = {'corect': 0, 'times': 0}

outpath = '/Users/mario/Desktop/Fellowship_Unige/MEUS/MEUS/'
fields = ['Ncoders', 'who', 'when', 'what', 'observations', 'ground_truth', 'CVR', 'Kalpha']


@app.route("/IE/events", methods=["PUT"])
def receiving_events_list():


    json_data = json.loads(request.data)
    events.extend(json_data['events'])

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




@app.route("/IE/<int:DO_id>", methods=["PUT"])
def put(DO_id):

    json_data           = json.loads(request.data)
    data_do, data_ih    = NewpreProcessing(json_data)
            # reputation,\
            #     reputation2,\
            #         reliability = NewpreProcessing(json_data)

    all_events_db = False
    flag = False
    return_flag = False
    repetition_flag = False
    if not data_do:
        print("2")
        print("_________________________________________________")
        print(data_do)
        print("No input data provided")
        input("checking")
        return {"message": "No input data provided"}, 400
    # Validate and deserialize input
    elif not data_ih:
        print("3")
        flag = True
    print("4")
    info_history = []
    try:
        print("5")
        direct_obs = do_schemas.load(data_do)#, unknown=INCLUDE)
        for nest in data_ih:
            info_history.append(ih_schemas.load(nest))
        print("6")

    except ValidationError as err:
        print("7")
        return err.messages, 422

    print("9")
    result_do   = []
    reputations = []
    reputations2 = []
    events2 = []
    latency = []


    for i, dobs in enumerate(direct_obs):

        ag_ids      = []
        ag_weights  = []
        
        events_types    = []
        query_ev        = eventsTab.query.filter_by(where=dobs['where']).first()

        ev_id = str(query_ev.id)
        ag_id = str(dobs['who'])

        try:
            # if the observation corresponds to the truth
            # v = 0
            # w = 0
            # flag1=False
            # if dobs['situation']==query_ev.situation and dobs['obj']==query_ev.obj:

            #     if {'situation': dobs['situation'], 'object': dobs['obj']} not in events_dict[ev_id]['obs']:

            #         agents_dict[ag_id]['positive']  += 1
            #         agents_dict[ag_id]['times']     += 1

            #         events_dict[ev_id]['obs'].append({   'situation':    dobs['situation'],
            #                                                 'object':       dobs['obj']})
            #         events_dict[ev_id]['whos'].append([dobs['who']])
            #         events_dict[ev_id]['whens'].append([[dobs['when']]])

            #         flag1=True
            #         v=1

            #     else:
            #         ind1 = events_dict[ev_id]['obs'].index({'situation':dobs['situation'], 'object': dobs['obj']})
                   
            #         # if the current observer has not been reported in the observers' list yet
            #         if dobs['who'] not in events_dict[ev_id]['whos'][ind1]:

            #             agents_dict[ag_id]['positive']  += 1
            #             agents_dict[ag_id]['times']     += 1

            #             events_dict[ev_id]['whos'][ind1].append(dobs['who'])
            #             events_dict[ev_id]['whens'][ind1].append([dobs['when']])
            #             v=1

            #         else:
            #             # checking the time the observation has occurred in order to avoid redunant infos
            #             if not any(dobs['when'] in nest for nest in events_dict[ev_id]['whens'][ind1]):

            #                 agents_dict[ag_id]['positive']  += 1
            #                 agents_dict[ag_id]['times']     += 1

            #                 ind2 = events_dict[ev_id]['whos'][ind1].index(dobs['who'])
            #                 events_dict[ev_id]['whens'][ind1][ind2].append(dobs['when'])
            #                 v=1

            #     if v!=0:
            #         reputation[i] = agents_dict[ag_id]['positive'] /\
            #                 (agents_dict[ag_id]['positive'] + agents_dict[ag_id]['negative'])

            #     if flag1:
            #         events_dict[ev_id]['reps'].append([reputation[i]])
            #     elif not flag1 and v!=0:
            #        events_dict[ev_id]['reps'][ind1].append(reputation[i]) 

            # else:

            #     if {'situation': dobs['situation'], 'object': dobs['obj']} not in events_dict[ev_id]['obs']:
                    
            #         agents_dict[ag_id]['negative']  += 1
            #         agents_dict[ag_id]['times']     += 1

            #         events_dict[ev_id]['obs'].append({   'situation':    dobs['situation'],
            #                                                 'object':       dobs['obj']})
            #         events_dict[ev_id]['whos'].append([dobs['who']])
            #         events_dict[ev_id]['whens'].append([[dobs['when']]])

            #         flag1=True
            #         w=1

            #     else:
            #         ind1 = events_dict[ev_id]['obs'].index({'situation': dobs['situation'], 'object': dobs['obj']})
                   
            #         # if the current observer has not been reported in the observers' list yet
            #         if dobs['who'] not in events_dict[ev_id]['whos'][ind1]:

            #             agents_dict[ag_id]['negative']  += 1
            #             agents_dict[ag_id]['times']     += 1

            #             events_dict[ev_id]['whos'][ind1].append(dobs['who'])
            #             events_dict[ev_id]['whens'][ind1].append([dobs['when']])
            #             w=1

            #         else:
            #             # checking the time the observation has occurred in order to avoid redunant infos
            #             if not any(dobs['when'] in nest for nest in events_dict[ev_id]['whens'][ind1]):

            #                 agents_dict[ag_id]['negative']  += 1
            #                 agents_dict[ag_id]['times']     += 1

            #                 ind2 = events_dict[ev_id]['whos'][ind1].index(dobs['who'])
            #                 events_dict[ev_id]['whens'][ind1][ind2].append(dobs['when'])

            #                 w=1

            #     if w!=0:
            #         reputation[i] = agents_dict[ag_id]['positive'] /\
            #                 (agents_dict[ag_id]['positive'] + agents_dict[ag_id]['negative'])

            #     if flag1:
            #         events_dict[ev_id]['reps'].append([reputation[i]])
            #     elif not flag1 and w!=0:
            #        events_dict[ev_id]['reps'][ind1].append(reputation[i])

            # if v!=0 or w!=0:
            #     reputations.append({
            #     'id':       dobs['who'],
            #     'rep':      reputation[i],    # success rate
            #     'times':    agents_dict[ag_id]['times'],
            #     'when':     dobs['when'],
            #     'rel':      reliability[i]
            #     })



            ''' Reputation based on a voting approach '''
            tf = 1 if dobs['situation']==query_ev.situation and dobs['obj']==query_ev.obj else 0
            cons = 'maj'
            token=0
            if not any( dobs['who'] in nest for nest in events_dict2[ev_id]['whos']):

                if {'situation': dobs['situation'], 'object': dobs['obj']} not in events_dict2[ev_id]['obs']:

                    events_dict2[ev_id]['obs'].append({      'situation':   dobs['situation'],
                                                                'object':   dobs['obj']})


                    events_dict2[ev_id]['whos'].append([dobs['who']])
                    events_dict2[ev_id]['times'].append([1])
                    if dobs['who']>=50:
                        events_dict2[ev_id]['votes'].append(1)
                    else:
                        events_dict2[ev_id]['votes'].append(6)

                    events_dict2[ev_id]['whens'].append([[dobs['when']]])
                    events_dict2[ev_id]['rels'].append([(len(events_dict2[ev_id]['obs'])-1, dobs['who'])])


                    print("first")
                    pprint(events_dict2[ev_id]['obs'])
                    print("---")

                    '''Krippendorff's alpha'''
                    if len(events_dict2[ev_id]['obs'])>=2:
                        print(compute_KrippendorffAlpha(events_dict2[ev_id]))


                    '''CVR method'''
                    if compute_CVR(events_dict2[ev_id], query_ev, CVR)==1:
                        logger( ev_id,
                                dobs['who'],
                                dobs['when'],
                                events_dict2[ev_id],
                                1,
                                round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                outpath,
                                fields,
                                query_ev)

                        CVR_performace['times'] += 1
                        CVR_performace['correct'] += 1
                        
                        for ag in list(np.unique(np.asarray(list(itertools.chain(events_dict2[ev_id]['whos'][-1]))))):
                            
                            agents_dict2[str(ag)]['weight'] += 1
                            ag_ids.append(ag)
                            ag_weights.append(agents_dict2[str(ag)]['weight'])

                    elif compute_CVR(events_dict2[ev_id], query_ev, CVR)==0:
                        # input("duedue")
                        flag2=True
                        logger( ev_id,
                                dobs['who'],
                                dobs['when'],
                                events_dict2[ev_id],
                                0,
                                round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                outpath,
                                fields,
                                query_ev)

                        CVR_performace['times'] += 1
                        print(events_dict2[ev_id]['whos'])
                        print(list(np.unique(np.asarray(list(itertools.chain(events_dict2[ev_id]['whos'][-1]))))))
                        for ag in list(np.unique(np.asarray(list(itertools.chain(events_dict2[ev_id]['whos'][-1]))))):
                            if agents_dict2[str(ag)]['weight'] > 1:

                                agents_dict2[str(ag)]['weight'] -= 1
                                ag_ids.append(ag)
                                ag_weights.append(agents_dict2[str(ag)]['weight'])
                    
                    elif compute_CVR(events_dict2[ev_id], query_ev, CVR)==-1:

                        # pprint(events_dict2[ev_id])
                        # print(len(events_dict2[ev_id]['obs'])-1)
                        # print(query_ev.situation)
                        # print(query_ev.obj)
                        # input()

                        logger( ev_id,
                                dobs['who'],
                                dobs['when'],
                                events_dict2[ev_id],
                                -1,
                                round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                outpath,
                                fields,
                                query_ev)
                    else:
                        pass


                    # reputation2[i] = 1 # agents_dict2[ag_id]['positive'] /\
                                    #(agents_dict2[ag_id]['positive'] + agents_dict2[ag_id]['negative'])

                    # events_dict2[ev_id]['reps'].append([reputation2[i]])
                    # events_dict2[ev_id]['reps1'].append([reputation[i]])


                    agVotes = agentsVotesTab(   agents_id   = dobs['who'],
                                                when        = dobs['when'],
                                                where       = dobs['where'],
                                                t_f         = tf,
                                                cons        = cons)

                    db.session.add(agVotes)


                else:
                    index = events_dict2[ev_id]['obs'].index({'situation': dobs['situation'], 'object': dobs['obj']})

                    token = 1


                    #     agVotes = agentsVotesTab(   agents_id   = dobs['who'],
                    #                                 when        = dobs['when'],
                    #                                 where       = dobs['where'],
                    #                                 t_f         = tf,
                    #                                 cons        = cons)

                    #     db.session.add(agVotes)

                    # if this agent has not reported this observation before
                    if dobs['who'] not in events_dict2[ev_id]['whos'][index]:

                        events_dict2[ev_id]['whos'][index].append(dobs['who'])
                        events_dict2[ev_id]['whens'][index].append([dobs['when']])
                        if dobs['who'] >= 50:
                            events_dict2[ev_id]['votes'][index] += 1
                        else:
                            events_dict2[ev_id]['votes'][index] += 6

                        index2 = events_dict2[ev_id]['whos'][index].index(dobs['who'])
                        events_dict2[ev_id]['times'][index].append(1)

                        events_dict2[ev_id]['rels'][index].append((index, dobs['who']))


                        print("third")

                        '''Krippendorff's alpha'''
                        if len(events_dict2[ev_id]['obs'])>=2:
                            print(compute_KrippendorffAlpha(events_dict2[ev_id]))

                        '''CVR method'''
                        if compute_CVR(events_dict2[ev_id], query_ev, CVR)==1:
                            logger( ev_id,
                                    dobs['who'],
                                    dobs['when'],
                                    events_dict2[ev_id],
                                    1,
                                    round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                    outpath,
                                    fields,
                                    query_ev)

                            CVR_performace['times'] += 1
                            CVR_performace['correct'] += 1
                        
                            for ag in list(np.unique(np.asarray(list(itertools.chain(events_dict2[ev_id]['whos'][index]))))):
                                
                                agents_dict2[str(ag)]['weight'] += 1

                                ag_ids.append(ag)
                                ag_weights.append(agents_dict2[str(ag)]['weight'])
                        elif compute_CVR(events_dict2[ev_id], query_ev, CVR)==0:
                            flag2=True
                            logger( ev_id,
                                    dobs['who'],
                                    dobs['when'],
                                    events_dict2[ev_id],
                                    0,
                                    round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                    outpath,
                                    fields,
                                    query_ev)

                            CVR_performace['times'] += 1
                            for ag in list(np.unique(np.asarray(list(itertools.chain(events_dict2[ev_id]['whos'][index]))))):
                                if agents_dict2[str(ag)]['weight'] > 1:

                                    agents_dict2[str(ag)]['weight'] -= 1

                                    ag_ids.append(ag)
                                    ag_weights.append(agents_dict2[str(ag)]['weight'])

                        elif compute_CVR(events_dict2[ev_id], query_ev, CVR)==-1:

                            # pprint(events_dict2[ev_id])
                            # print(len(events_dict2[ev_id]['obs'])-1)
                            # print(query_ev.situation)
                            # print(query_ev.obj)
                            # input()


                            logger( ev_id,
                                    dobs['who'], 
                                    dobs['when'],
                                    events_dict2[ev_id],
                                    -1,
                                    round(compute_KrippendorffAlpha(events_dict2[ev_id]), 3),
                                    outpath,
                                    fields,
                                    query_ev)
                        
                        else:
                            pass


                        agVotes = agentsVotesTab(   agents_id   = dobs['who'],
                                                    when        = dobs['when'],
                                                    where       = dobs['where'],
                                                    t_f         = tf,
                                                    cons        = cons)

                        db.session.add(agVotes)
                    else:
                        token=3

                    # if not token==3:

                    #     reputation2[i] = 1#agents_dict2[ag_id]['positive'] /\
                                        #(agents_dict2[ag_id]['positive'] + agents_dict2[ag_id]['negative'])

                        # reputation2[i] = agents_dict2[ag_id]['numAgs'] / agents_dict2[ag_id]['denAgs']

                    # if token==2:
                    #     events_dict2[ev_id]['reps'][index][index2] = reputation2[i]
                    #     events_dict2[ev_id]['reps1'][index][index2] = reputation[i]
                    #     # events_dict2[ev_id]['votes'][index] += 1
                    # elif token==1:
                    #     events_dict2[ev_id]['reps'][index].append(reputation2[i])
                    #     events_dict2[ev_id]['reps1'][index].append(reputation[i])
                        # events_dict2[ev_id]['votes'][index] += 1

            # new_weights = {}
            # if not token==3:
                # reputations2.append({
                #             'id':       dobs['who'],
                #             'rep':      reputation2[i],
                #             'times':    agents_dict2[ag_id]['times'],
                #             'when':     dobs['when'],
                #             'rel':      reliability[i]
                #             })
                
                # for y in range(len(ag_ids)):

                #     reputations2.append({
                #         'id':   ag_ids[y],
                #         'rep':  ag_weights[y]
                #     })

                # new_weights = {str(i):j for i in ag_ids for j in ag_weights}


        except Exception as error:
            raise error


        # print("a")
        # # first time
        # if len(query_ev.observations)==0:

        #     ev = observedEventsTab( obs_situation   = dobs['situation'],
        #                             obs_object      = dobs['obj'],
        #                             confidence      = 1.)
        #     db.session.add(ev)
        #     query_ev.observations.append(ev)
        #     # query_ev.observations[-1].event_id = query_ev.id
        #     query_ev.observations[query_ev.observations.index(ev)].event_id = query_ev.id
        #     print("b")

        # elif len(query_ev.observations) > 0:
        #     for k, val in enumerate(query_ev.observations):
        #         if val not in events_types:
        #             events_types.append({'observation': val, 'times': 1})

        #             for h in range(k, len(query_ev.observations)):
        #                 if query_ev.observations[h] == events_types[-1]['observation']:

        #                     events_types[-1]['times'] += 1


        #     zipped_obs_db   = list(zip( [obs['observation'].obs_situation for obs in events_types],\
        #                                  [obs['observation'].obs_object for obs in events_types] ))
        #     ob              = (dobs['situation'], dobs['obj'])

        #     print("c")
        #     # if this observation has been already reported, update the confidence for all the observations
        #     if ob in zipped_obs_db:
                
        #         index = zipped_obs_db.index(ob)
        #         events_types[index]['times'] += 1

        #         total_cases = sum(obs['times'] for obs in events_types)

        #         for m, ob in enumerate(query_ev.observations):
        #             if sum(el[i] for el in events_dict[ev_id]['reps'] for i in range(len(el)))==0:
        #                 ob.confidence = round( 1/len(query_ev.observations), 3)
        #             else:
        #                 ob.confidence = round(sum(el for el in events_dict[ev_id]['reps'][m])\
        #                                                                 / sum(el[i] for el in events_dict[ev_id]['reps'] for i in range(len(el))), 3)
        #             print("d")
            
        #     # if its the first time this observation has been reported
        #     elif ob not in zipped_obs_db:

        #         total_cases = sum(obs['times'] for obs in events_types) + 1

        #         ev = observedEventsTab( obs_situation   = dobs['situation'],
        #                                 obs_object      = dobs['obj'],
        #                                 confidence      = round(1 / total_cases, 3))

        #         db.session.add(ev)
        #         query_ev.observations.append(ev)
        #         # query_ev.observations[-1].event_id = query_ev.id
        #         query_ev.observations[query_ev.observations.index(ev)].event_id = query_ev.id 
        #         events_types.append({'observation': ev, 'times': 1})


        #         for n, ob in enumerate(query_ev.observations):
        #             if sum(el[i] for el in events_dict[ev_id]['reps'] for i in range(len(el)))==0:
        #                 ob.confidence = round( 1/len(query_ev.observations), 3)
        #             else:
        #                 ob.confidence = round(sum(el for el in events_dict[ev_id]['reps'][n])\
        #                                     / sum(el[i] for el in events_dict[ev_id]['reps'] for i in range(len(el)) ), 3)

        #         print("e")
            
        #     if abs(1 - sum(query_ev.observations[counter].confidence for counter in range(len(query_ev.observations)) )) >= 0.1:
        #         print("************************************")
        #         for el in query_ev.observations:
        #             print("obs_sit: ", el.obs_situation, "obs_object: ", el.obs_object, "conf: ", el.confidence, "event_id: ", el.event_id)
        #         input("ouch")
        



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
        return {"message": "Created a new DO and IH.",  "DO": result_do, "events": events, 'latency': latency, 'reputation': reputations, 'reputation2': reputations2}#, 'weights': new_weights}
    elif not return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, 'reputation': reputations, 'reputation2': reputations2}#, 'weights': new_weights}



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