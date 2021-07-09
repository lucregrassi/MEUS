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
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, inputs
from marshmallow import Schema, fields as mafields, ValidationError, INCLUDE, EXCLUDE, pre_load

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databaseMEUS.db'
db = SQLAlchemy(app)
# ma = Marshmallow(app)


# logging.basicConfig(level=logging.INFO, filename='70%.log', filemode='w')

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
    # w1          = db.Column(db.Integer)
    # w2          = db.Column(db.Integer)
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
    # confidence2     = db.Column(db.Float, nullable=False)
    # times           = db.Column(db.Integer, nullable=False)

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
    # Information element or direct observation
    who             = db.Column(db.Integer, nullable=False)
    lat             = db.Column(db.Integer, nullable=False)

# db.create_all()


##### SCHEMAS #####


class dirObsSchema(Schema):
    # class Meta:
    #     unknown=INCLUDE
    id                  = mafields.Integer(dump_only=True)
    dir_obs             = mafields.Dict(keys=mafields.Str(), values=mafields.Str())
    situation           = mafields.Str()
    obj                 = mafields.Str()
    # situation           = mafields.Str()
    # obj                 = mafields.Str()
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
    # w1        = mafields.Integer()
    # w2        = mafields.Integer()
    when            = mafields.Integer()
    sent_at_loop    = mafields.Integer()
    sent_where      = mafields.Integer()

# class eventsSchema(Schema):
#     id          = mafields.Integer(dump_only=True)
#     situation   = mafields.Str()
#     obj         = mafields.Str()
#     confidence  = mafields.Float()



do_schema   = dirObsSchema()
do_schemas  = dirObsSchema(many=True)
ih_schema   = infoHistorySchema()
ih_schemas  = infoHistorySchema(many=True)


# fields  = ['sender', 'sit', 'obj', 'when', 'where', 'who', 'sent_at_loop', 'lat']


latency = []
# latency2 = []

events  = []
agents_dict = {}
events_dict = {}

agents_dict2 = {}
agents_perf  = {}
events_dict2 = {}


@app.route("/IE/events", methods=["PUT"])
def receiving_events_list():

    # with open('latency_tab_40%.csv', 'w') as f:
    #     wr = csv.DictWriter(f, fieldnames=fields)
    #     wr.writeheader()

    latency.clear()
    # latency2.clear()

    json_data = json.loads(request.data)
    events.extend(json_data['events'])

    # print(len(events))
    # input()

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
        agents_dict[str(agent)]     = {'positive': 1, 'negative': 1, 'times': 0}
        agents_dict2[str(agent)]    = {'positive': 1, 'negative': 1, 'times': 0}
        agents_perf[str(agent)]     = []

    pprint(events)

    return{"message": "registered events in the environments", "events": events}



@app.route("/IE/<int:DO_id>")
def get(DO_id):
    try:
        # do = dirObsTab.query.filter_by(id=DO_id).first()
        do = dirObsTab.query.all()
    except IntegrityError:
        return {"message": "DO_id could not be found."}, 400

    DO_res = []
    infos = []
    for res in do:
        DO_res.append(do_schema.dump(res))
        for elem in res.info_histories:
            infos.append(ih_schema.dump(infoHistoryTab.query.get(elem.id)))

    # dumped_do = do_schemas.dump(do)
    for i in range(len(do)):
        for j in range(len(do)):
            if i!=j and do[i] == do[j]:
                print("Houston we have a problem\n" +str(do[i]) + " is equal " + str(do[j]))
                print("at pos " +str(i))


    dupl = []

    for i in range(len(do)):
        for j in range(len(do[i].info_histories)):
            for k in range(j+1, len(do[i].info_histories)):
                if do[i].info_histories[j].dir_obs_id == do[i].info_histories[k].dir_obs_id and \
                    do[i].info_histories[j].observer == do[i].info_histories[k].observer and \
                        do[i].info_histories[j].a1 == do[i].info_histories[k].a1 and do[i].info_histories[j].a2 == do[i].info_histories[k].a2 and\
                            do[i].info_histories[j].sender == do[i].info_histories[k].sender:
                    dupl.append([ih_schema.dump(do[i].info_histories[j]), ih_schema.dump(do[i].info_histories[k])])
                    print("Houston we have a problem\n" +str(do[i].info_histories[j]) + " is equal " + str(do[i].info_histories[k]))
                    print("at pos " +str(i))

    return {"DO": DO_res, "infos": infos}
    # return {"res": dupl}




@app.route("/IE/<int:DO_id>", methods=["PUT"])
def put(DO_id):

    # print("#################################################")
    json_data = json.loads(request.data)
    # print(json_data)
    # input("put() first check")
    data_do, data_ih, reputation, reputation2, reliability = NewpreProcessing(json_data)

    # data_do, data_ih = NewpreProcessing(json_data)

    # reputation = 1-reputation
    # print ("processed_data:")
    # for el in data_do:
    #     print(el)
    # print("***********************************************")
    # for el in data_ih:
    #     print(el)
    # input()

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
        # print ("direct_obs: " +str(direct_obs))
        # print ("info_history: " +str(info_history))
    except ValidationError as err:
        print("7")
        return err.messages, 422

    print("9")
    result_do   = []
    reputations = []
    reputations2 = []
    events2 = []
    latency2 = []

    # print("sender:", sender)
    # pprint(direct_obs)

    for i in range(len(direct_obs)):

        # print(direct_obs[i])
        
        events_types    = []
        query_ev        = eventsTab.query.filter_by(where=direct_obs[i]['where']).first()

        try:
            # if the observation corresponds to the truth
            flag1=False
            if direct_obs[i]['situation']==query_ev.situation and direct_obs[i]['obj']==query_ev.obj:

                if {'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']} not in events_dict[str(query_ev.id)]['obs']:

                    agents_dict[str(direct_obs[i]['who'])]['positive']  += 1
                    agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                    events_dict[str(query_ev.id)]['obs'].append({   'situation':    direct_obs[i]['situation'],
                                                                    'object':       direct_obs[i]['obj']})
                    events_dict[str(query_ev.id)]['whos'].append([direct_obs[i]['who']])
                    events_dict[str(query_ev.id)]['whens'].append([[direct_obs[i]['when']]])

                    flag1=True

                else:
                    ind1 = events_dict[str(query_ev.id)]['obs'].index({'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']})
                   
                    # if the current observer has not been reported in the observers' list yet
                    if direct_obs[i]['who'] not in events_dict[str(query_ev.id)]['whos'][ind1]:

                        agents_dict[str(direct_obs[i]['who'])]['positive']  += 1
                        agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                        events_dict[str(query_ev.id)]['whos'][ind1].append(direct_obs[i]['who'])
                        events_dict[str(query_ev.id)]['whens'][ind1].append([direct_obs[i]['when']])

                    else:
                        # checking the time the observation has occurred in order to avoid redunant infos
                        if not any(direct_obs[i]['when'] in nest for nest in events_dict[str(query_ev.id)]['whens'][ind1]):

                            agents_dict[str(direct_obs[i]['who'])]['positive']  += 1
                            agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                            ind2 = events_dict[str(query_ev.id)]['whos'][ind1].index(direct_obs[i]['who'])
                            events_dict[str(query_ev.id)]['whens'][ind1][ind2].append(direct_obs[i]['when'])

                reputation[i] = agents_dict[str(direct_obs[i]['who'])]['positive'] /\
                            (agents_dict[str(direct_obs[i]['who'])]['positive'] + agents_dict[str(direct_obs[i]['who'])]['negative'])

                if flag1:
                    events_dict[str(query_ev.id)]['reps'].append([reputation[i]])
                else:
                   events_dict[str(query_ev.id)]['reps'][ind1].append(reputation[i]) 

            else:

                if {'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']} not in events_dict[str(query_ev.id)]['obs']:
                    
                    agents_dict[str(direct_obs[i]['who'])]['negative']  += 1
                    agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                    events_dict[str(query_ev.id)]['obs'].append({   'situation':    direct_obs[i]['situation'],
                                                                    'object':       direct_obs[i]['obj']})
                    events_dict[str(query_ev.id)]['whos'].append([direct_obs[i]['who']])
                    events_dict[str(query_ev.id)]['whens'].append([[direct_obs[i]['when']]])

                    flag1=True

                else:
                    ind1 = events_dict[str(query_ev.id)]['obs'].index({'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']})
                   
                    # if the current observer has not been reported in the observers' list yet
                    if direct_obs[i]['who'] not in events_dict[str(query_ev.id)]['whos'][ind1]:

                        agents_dict[str(direct_obs[i]['who'])]['negative']  += 1
                        agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                        events_dict[str(query_ev.id)]['whos'][ind1].append(direct_obs[i]['who'])
                        events_dict[str(query_ev.id)]['whens'][ind1].append([direct_obs[i]['when']])

                    else:
                        # checking the time the observation has occurred in order to avoid redunant infos
                        if not any(direct_obs[i]['when'] in nest for nest in events_dict[str(query_ev.id)]['whens'][ind1]):

                            agents_dict[str(direct_obs[i]['who'])]['negative']  += 1
                            agents_dict[str(direct_obs[i]['who'])]['times']     += 1

                            ind2 = events_dict[str(query_ev.id)]['whos'][ind1].index(direct_obs[i]['who'])
                            events_dict[str(query_ev.id)]['whens'][ind1][ind2].append(direct_obs[i]['when'])

                reputation[i] = agents_dict[str(direct_obs[i]['who'])]['positive'] /\
                            (agents_dict[str(direct_obs[i]['who'])]['positive'] + agents_dict[str(direct_obs[i]['who'])]['negative'])

                if flag1:
                    events_dict[str(query_ev.id)]['reps'].append([reputation[i]])
                else:
                   events_dict[str(query_ev.id)]['reps'][ind1].append(reputation[i])


            reputations.append({
            'id':       direct_obs[i]['who'],
            'rep':      1-reputation[i],
            'times':    agents_dict[str(direct_obs[i]['who'])]['times'],
            'when':     direct_obs[i]['when'],
            'rel':      reliability[i]
            })


            # reputation based on a voting approach
            tf = 1 if direct_obs[i]['situation']==query_ev.situation and direct_obs[i]['obj']==query_ev.obj else 0
            cons = 'maj'
            if {'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']} not in events_dict2[str(query_ev.id)]['obs']:

                events_dict2[str(query_ev.id)]['obs'].append({      'situation':    direct_obs[i]['situation'],
                                                                    'object':       direct_obs[i]['obj']})

                events_dict2[str(query_ev.id)]['whos'].append([direct_obs[i]['who']])
                events_dict2[str(query_ev.id)]['times'].append([1])
                events_dict2[str(query_ev.id)]['votes'].append(1)
                events_dict2[str(query_ev.id)]['whens'].append([[direct_obs[i]['when']]])
                events_dict2[str(query_ev.id)]['rels'].append([[reliability[i]]])


                # Here I have to compute the reputation
                # cons = 'majority'
                if events_dict2[str(query_ev.id)]['votes'][-1] == max(events_dict2[str(query_ev.id)]['votes']):

                    agents_dict2[str(direct_obs[i]['who'])]['positive'] += 1
                    agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                else:

                    agents_dict2[str(direct_obs[i]['who'])]['negative'] += 1
                    agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                    cons = 'min'


                reputation2[i] = agents_dict2[str(direct_obs[i]['who'])]['positive'] /\
                                (agents_dict2[str(direct_obs[i]['who'])]['positive'] + agents_dict2[str(direct_obs[i]['who'])]['negative'])

                events_dict2[str(query_ev.id)]['reps'].append([reputation2[i]])
                events_dict2[str(query_ev.id)]['reps1'].append([reputation[i]])

                # if not any(query_ev.id==dictionary['ev'] for dictionary in agents_perf[str(direct_obs[i]['who'])]):
                #         agents_perf[str(direct_obs[i]['who'])].append({
                #             'when': direct_obs[i]['when'],
                #             'cons': cons,
                #             'ev':   query_ev.id
                #         })

                agVotes = agentsVotesTab(   agents_id   = direct_obs[i]['who'],
                                            when        = direct_obs[i]['when'],
                                            where       = direct_obs[i]['where'],
                                            t_f         = tf,
                                            cons        = cons)

                db.session.add(agVotes)


            else:
                index = events_dict2[str(query_ev.id)]['obs'].index({'situation': direct_obs[i]['situation'], 'object': direct_obs[i]['obj']})

                token = 1

                # if the direct observer has already reported this direct observation
                if direct_obs[i]['who'] in events_dict2[str(query_ev.id)]['whos'][index] and\
                     not any(direct_obs[i]['when'] in nest for nest in events_dict2[str(query_ev.id)]['whens'][index]):

                    token = 2
                    index2 = events_dict2[str(query_ev.id)]['whos'][index].index(direct_obs[i]['who'])
                    events_dict2[str(query_ev.id)]['times'][index][index2] += 1

                    events_dict2[str(query_ev.id)]['whens'][index][index2].append(direct_obs[i]['when'])
                    events_dict2[str(query_ev.id)]['rels'][index][index2].append(reliability[i])
                    events_dict2[str(query_ev.id)]['votes'][index] += 1

                    # cons = 'majority'
                    if events_dict2[str(query_ev.id)]['votes'][index] == max(events_dict2[str(query_ev.id)]['votes']):
                        agents_dict2[str(direct_obs[i]['who'])]['positive'] += 1
                        agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                    else:
                        agents_dict2[str(direct_obs[i]['who'])]['negative'] += 1
                        agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                        cons = 'min'

                    # if not any(query_ev.id==dictionary['ev'] for dictionary in agents_perf[str(direct_obs[i]['who'])]):
                    #     agents_perf[str(direct_obs[i]['who'])].append({
                    #         'when': direct_obs[i]['when'],
                    #         'cons': cons,
                    #         'ev':   query_ev.id
                    #     })


                    agVotes = agentsVotesTab(   agents_id   = direct_obs[i]['who'],
                                                when        = direct_obs[i]['when'],
                                                where       = direct_obs[i]['where'],
                                                t_f         = tf,
                                                cons        = cons)

                    db.session.add(agVotes)

                # if this agent has not reported this observation before
                elif direct_obs[i]['who'] not in events_dict2[str(query_ev.id)]['whos'][index]:

                    events_dict2[str(query_ev.id)]['whos'][index].append(direct_obs[i]['who'])
                    events_dict2[str(query_ev.id)]['whens'][index].append([direct_obs[i]['when']])
                    events_dict2[str(query_ev.id)]['votes'][index] += 1

                    index2 = events_dict2[str(query_ev.id)]['whos'][index].index(direct_obs[i]['who'])
                    events_dict2[str(query_ev.id)]['times'][index].append(1)

                    events_dict2[str(query_ev.id)]['rels'][index].append([reliability[i]])


                    # cons = 'majority'
                    if events_dict2[str(query_ev.id)]['votes'][index] == max(events_dict2[str(query_ev.id)]['votes']):
                        agents_dict2[str(direct_obs[i]['who'])]['positive'] += 1
                        agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                    else:
                        agents_dict2[str(direct_obs[i]['who'])]['negative'] += 1
                        agents_dict2[str(direct_obs[i]['who'])]['times']    += 1

                        cons = 'min'

                    
                    # if not any(query_ev.id==dictionary['ev'] for dictionary in agents_perf[str(direct_obs[i]['who'])]):
                    #     agents_perf[str(direct_obs[i]['who'])].append({
                    #         'when': direct_obs[i]['when'],
                    #         'cons': cons,
                    #         'ev':   query_ev.id
                    #     })

                    agVotes = agentsVotesTab(   agents_id   = direct_obs[i]['who'],
                                                when        = direct_obs[i]['when'],
                                                where       = direct_obs[i]['where'],
                                                t_f         = tf,
                                                cons        = cons)

                    db.session.add(agVotes)


                else:
                    token=3


                reputation2[i] = agents_dict2[str(direct_obs[i]['who'])]['positive'] /\
                                (agents_dict2[str(direct_obs[i]['who'])]['positive'] + agents_dict2[str(direct_obs[i]['who'])]['negative'])

                if token==2:
                    events_dict2[str(query_ev.id)]['reps'][index][index2] = reputation2[i]
                    events_dict2[str(query_ev.id)]['reps1'][index][index2] = reputation[i]
                    events_dict2[str(query_ev.id)]['votes'][index] += 1
                elif token==1:
                    events_dict2[str(query_ev.id)]['reps'][index].append(reputation2[i])
                    events_dict2[str(query_ev.id)]['reps1'][index].append(reputation[i])
                    events_dict2[str(query_ev.id)]['votes'][index] += 1

                
            # if token==1 or token==2:
            #         agents_perf[str(direct_obs[i]['who'])].append({
            #             'when': direct_obs[i]['when'],
            #             'cons': cons,
            #             'ev':   query_ev.id
            #         })

            # agVotes = agentsVotesTab(   agents_id   = direct_obs[i]['who'],
            #                             when        = direct_obs[i]['when'],
            #                             where       = direct_obs[i]['where'],
            #                             t_f         = tf,
            #                             cons        = cons)

            # db.session.add(agVotes)

            reputations2.append({
                        'id':       direct_obs[i]['who'],
                        'rep':      1-reputation2[i],
                        'times':    agents_dict2[str(direct_obs[i]['who'])]['times'],
                        'when':     direct_obs[i]['when'],
                        'rel':      reliability[i]
                        })

        except Exception as error:

            raise error



        print("a")
        # first time
        if len(query_ev.observations)==0:

            ev = observedEventsTab( obs_situation   = direct_obs[i]['situation'],
                                    obs_object      = direct_obs[i]['obj'],
                                    confidence      = 1.)
            db.session.add(ev)
            query_ev.observations.append(ev)
            query_ev.observations[-1].event_id = query_ev.id
            print("b")

        elif len(query_ev.observations) > 0:
            for k in range(len(query_ev.observations)):
                if query_ev.observations[k] not in events_types:

                    events_types.append({'observation': query_ev.observations[k], 'times': 1})

                    for h in range(k, len(query_ev.observations)):
                        if query_ev.observations[h] == events_types[-1]['observation']:

                            events_types[-1]['times'] += 1

            # sits_db = [obs['observation'].obs_situation for obs in events_types]
            # objs_db = [obs['observation'].obs_object for obs in events_types]

            zipped_obs_db   = list(zip( [obs['observation'].obs_situation for obs in events_types],\
                                         [obs['observation'].obs_object for obs in events_types] ))
            ob              = (direct_obs[i]['situation'], direct_obs[i]['obj'])

            print("c")
            # if this observation has been already reported, update the confidence for all the observations
            if ob in zipped_obs_db:
                
                index = zipped_obs_db.index(ob)
                events_types[index]['times'] += 1

                total_cases = sum(obs['times'] for obs in events_types)

                # percs   = [events_types[m]['times']*100 / total_cases for m in range(len(query_ev.observations))]
                # conf    = sum(perc*w for perc,w in zip( percs, agents_dict[str(query_ev.id)] )) \
                #             / sum(w for w in agents_dict[str(query_ev.id)])

                for m in range(len(query_ev.observations)):
                    
                    # query_ev.observations[m].confidence = round(events_types[m]['times']*100 / total_cases, 2)
                    query_ev.observations[m].confidence = round(sum(el for el in events_dict[str(query_ev.id)]['reps'][m])\
                                                                    / sum(el[i] for el in events_dict[str(query_ev.id)]['reps'] for i in range(len(el))), 3)
                print("d")
            
            # if its the first time this observation has been reported
            elif ob not in zipped_obs_db:

                total_cases = sum(obs['times'] for obs in events_types) + 1

                ev = observedEventsTab( obs_situation   = direct_obs[i]['situation'],
                                        obs_object      = direct_obs[i]['obj'],
                                        confidence      = round(1 / total_cases, 3))

                db.session.add(ev)
                query_ev.observations.append(ev)
                query_ev.observations[-1].event_id = query_ev.id
                events_types.append({'observation': ev, 'times': 1})

                # percs   = [events_types[m]['times']*100 / total_cases for m in range(len(events_types))]
                # conf    = sum(perc*w for perc,w in zip( percs, agents_dict[str(query_ev.id)] )) \
                #             / sum(w for w in agents_dict[str(query_ev.id)])

                for n in range(len(query_ev.observations)):

                    # query_ev.observations[n].confidence = round(events_types[n]['times']*100 / total_cases, 2)
                    query_ev.observations[n].confidence = round(sum(el for el in events_dict[str(query_ev.id)]['reps'][n])\
                                                                    / sum(el[i] for el in events_dict[str(query_ev.id)]['reps'] for i in range(len(el)) ), 3)

                print("e")
            
            if abs(1 - sum(query_ev.observations[counter].confidence for counter in range(len(query_ev.observations)) )) >= 0.1:
                print("************************************")
                for el in query_ev.observations:
                    print("obs_sit: ", el.obs_situation, "obs_object: ", el.obs_object, "conf: ", el.confidence, "event_id: ", el.event_id)
                input("ouch")
        

        # First 2 tabs in the db
        query_do = dirObsTab.query.filter_by(   situation   = direct_obs[i]['situation'],
                                                obj         = direct_obs[i]['obj'],
                                                when        = direct_obs[i]['when'],
                                                where       = direct_obs[i]['where'],
                                                who         = direct_obs[i]['who']).first()



        # if the direct observation is not in the db
        if not query_do:
            return_flag = True
            result_ih = []

            # if info_history[i][0]['sender'] < 70:
            # latency.append(info_history[i][0]['sent_at_loop'] - direct_obs[i]['when'])
            # else:
            #     print(info_history[i])
            #     input("somethings wrong")

            # logging.info(do_schema.dump(direct_obs[i]))
            # logging.info(latency[-1])

            # lt  = latencyTab(   situation       = direct_obs[i]['situation'],
            #                     obj             = direct_obs[i]['obj'],
            #                     where           = direct_obs[i]["where"],
            #                     when            = direct_obs[i]["when"],
            #                     who             = direct_obs[i]["who"],
            #                     lat             = latency[-1])
            # db.session.add(lt)
            
            # if info_history[i][0]['sender'] < 70:
            #     with open('latency_tab_80%.csv', 'a') as csv_file:
            #         csv_w = csv.DictWriter(csv_file, fieldnames=fields)

            #         info = {
            #             'sender':       info_history[i][0]['sender'],
            #             'situation':    direct_obs[i]['situation'],
            #             'obj':          direct_obs[i]['obj'],
            #             'where':        direct_obs[i]['where'],
            #             'when':         direct_obs[i]['when'],
            #             'who':          direct_obs[i]['who'],
            #             'lat':          latency[-1]
            #         }

            #         csv_w.writerow(info)

            do  = dirObsTab(    situation       = direct_obs[i]['situation'],
                                obj             = direct_obs[i]['obj'],
                                where           = direct_obs[i]["where"],
                                when            = direct_obs[i]["when"],
                                who             = direct_obs[i]["who"])


            # ackowledging we are adding a new direct observation to the db
            elem = {'situation': do.situation, 'object': do.obj, 'where': do.where, 'who': do.who}
            for n, el in enumerate(events):
                # if the observation corresponds to the actual situation
                if el['situation'] == elem['situation'] and el['object'] == elem['object'] and el['where']==elem['where']:
                    try:
                        # index = events.index(el)
                        # del events[index]
                        if events[n]['correct']==0:

                            latency.append(info_history[i][0]['sent_at_loop'] - direct_obs[i]['when'])
                            latency2.append({
                                'sender':       info_history[i][0]['sender'],
                                'sit':          direct_obs[i]['situation'],
                                'obj':          direct_obs[i]['obj'],
                                'when':         direct_obs[i]['when'],
                                'where':        direct_obs[i]['where'],
                                'who':          direct_obs[i]['who'],
                                'sent_at_loop': info_history[i][0]['sent_at_loop'],
                                'lat':          latency[-1]
                            })
                            events[n]['first_time'] = 1

                            
                        events[n]['correct'] += 1
                    except Exception as err:
                        raise err

                # if the element is a "distorted" observation instead
                elif (el['situation'] != elem['situation'] or el['object'] != elem['object']) and el['where'] == elem['where']:
                    # index = events.index(el)
                    events[n]['mistaken']['times'] += 1
                    events[n]['mistaken']['difference'].append(elem)

        
        
            if not flag:
                for j in range(len(info_history[i])):
                    ih = infoHistoryTab(    observer        = info_history[i][j]['observer'],
                                            a1              = info_history[i][j]['a1'],
                                            a2              = info_history[i][j]['a2'],
                                            sender          = info_history[i][j]['sender'],
                                            where           = info_history[i][j]['where'],
                                            when            = info_history[i][j]['when'],
                                            sent_at_loop    = info_history[i][j]['sent_at_loop'],
                                            sent_where      = info_history[i][j]['sent_where'])
                    # print(do_schema.dump(do))
                    # print(ih_schema.dump(ih))
                    # input("checking first event")
                    db.session.add(ih)
                    # result_ih.append(ih_schema.dump(infoHistoryTab.query.get(ih.id)))
                    do.info_histories.append(ih)
                    # ih.dir_obs_tab = do.id
                    # do.info_histories[-1].dir_obs_id = do.id
                    do.info_histories[do.info_histories.index(ih)].dir_obs_id = do.id
                    result_ih.append(ih_schema.dump(ih))
                result_do.append(result_ih)
            print("10")
        # if the direct observation is already in the db
        else:#elif query_do:
            # print("###################################################")
            repetition_flag = True
            # print("request:     ", direct_obs[i]['situation'],",", direct_obs[i]['obj'],",", direct_obs[i]['when'],\
            #                         ",", direct_obs[i]['where'], ",", direct_obs[i]['who'])
            # print("query_do:    ", do_schema.dump(query_do)['situation'],",", do_schema.dump(query_do)['obj'],\
            #                     ",", do_schema.dump(query_do)['when'], ",", do_schema.dump(query_do)['where'],\
            #                         ",", do_schema.dump(query_do)['who'])
            # print(bool(query_do))
            # input()
            # if all the events have been seen
            if len(events) == 0:
                all_events_db = True
            result_ih = []
            if not flag:
                for j in range(len(info_history[i])):
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


    # keep track if event has been uploaded on the db for the first time
    if return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, "events": events, 'latency2': latency2, 'reputation': reputations, 'reputation2': reputations2}
    elif not return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, 'reputation': reputations, 'reputation2': reputations2}



@app.route("/IE/<int:DO_id>", methods=["DELETE"])
def delete_(DO_id):

    query           = dirObsTab.query.options(joinedload(dirObsTab.info_histories))
    query_events    = eventsTab.query.options(joinedload(eventsTab.observations))
    ag_votes        = agentsVotesTab.query.all()
    lat_tab         = latencyTab.query.all()

    for v in ag_votes:
        db.session.delete(v)
    
    for l in lat_tab:
        db.session.delete(l)

    check = []
    # latency = []
    # latency2 = []
    counter1 = 0
    counter2 = 0


    # fieldnames = ["sit", "obj", "when", "where", "who", "lat", "sent_at_loop"]

    # with open('80%.csv', 'w') as f:
    #     csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     csv_writer.writeheader()

    for Obs in query:

        # if 60 <= Obs.info_histories[0].sender <= 70:
        #     check.append(Obs.info_histories[0].sent_at_loop - Obs.when)
        # else:
        #     latency2.append(Obs.info_histories[0].sent_at_loop - Obs.when)
        # first time an observation has been sent to the db

        # minimum = min(x.when for x in Obs.info_histories)
        # ind     = [i for i, j in enumerate(Obs.info_histories) if j.when==minimum]

        # latency.append(Obs.info_histories[ind[0]].sent_at_loop - Obs.when)

        # minimum = min(x.sent_at_loop for x in Obs.info_histories)
        # ind     = [i for i, j in enumerate(Obs.info_histories) if j.sent_at_loop==minimum]

        # print("id:", Obs.info_histories[ind[0]].dir_obs_id)
        # print(ind)
        # print(len(Obs.info_histories))
        # # print("id:", Obs.info_histories[ind[0]].dir_obs_id)
        # if ind[0] >= len(Obs.info_histories):
        #     # print("id:", Obs.info_histories[ind[0]].dir_obs_id)
        #     input("ouch")

        # if not( 70 <= Obs.info_histories[ind[0]].sender <= 80):

        #     latency.append(minimum - Obs.when)
        # print(do_schema.dump(Obs))
        # pprint(ih_schemas.dump(Obs.info_histories))
        # print(len(Obs.info_histories))
        # print(ih_schema.dump(Obs.info_histories[0]))
        # print(Obs.info_histories[ind[0]].sent_at_loop)
        # print(Obs.when)
        # print(latency[-1])
        # print(ind)
        # input("checki")
        # with open('80%.csv', 'a') as f:
        #     csv_writer = csv.DictWriter(f, fieldnames=fieldnames)

        #     info = {
        #         'sit':          Obs.situation,
        #         'obj':          Obs.obj,
        #         'when':         Obs.when,
        #         'where':        Obs.where,
        #         'who':          Obs.who,
        #         'lat':          Obs.info_histories[0].sent_at_loop - Obs.when,
        #         'sent_at_loop': Obs.info_histories[0].sent_at_loop
        #     }
        #     csv_writer.writerow(info)

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
    events_dict.clear()

    # latency2.sort(key=lambda a: a['sender'])

    # with open('latency_tab_40%.csv', 'a') as f:
    #     csv_writer = csv.DictWriter(f, fieldnames=fields)

    #     for el in latency2:

    #         info = el

    #         csv_writer.writerow(info)




    return {"message": "tabs are cleared", "size_tab1": counter1, "size_tab2": counter2, "latency": statistics.mean(latency), "events_dict2": events_dict2, "agents_perf": agents_perf,
            'lat_length': len(latency)}


if __name__=="__main__":
    app.run(debug=True)