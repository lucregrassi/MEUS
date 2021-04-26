import json
import statistics
from pprint import pprint
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


# -- MODEL --

class dirObsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    # dir_obs         = db.Column(db.JSON, nullable=False)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    when            = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    # Information element or direct observation
    who             = db.Column(db.Integer, nullable=False)
    info_histories  = db.relationship('infoHistoryTab', backref="dir_obs_tab", lazy=True)

    # def __repr__(self):
    #     return f"dirObsTab(id = {id}\n situation = {situation}\n \
    #             object = {obj}\n when = {when}\n where = {where}\n who = {who}\n"


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


class eventsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    situation       = db.Column(db.String(50), nullable=False)
    obj             = db.Column(db.String(50), nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    observations    = db.relationship('observedEventsTab', backref='events_tab', lazy=True)


class observedEventsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('events_tab.id'))
    obs_situation   = db.Column(db.String(50), nullable=False)
    obs_object      = db.Column(db.String(50), nullable=False)
    confidence      = db.Column(db.Float, nullable=False)
    # times           = db.Column(db.Integer, nullable=False)

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



# @app.route("/IE/events-status/<string:qsit>/<string:qobj>/<int:qwhen>/<int:qwhere>/<int:qwho>")
# def events_db_status(qsit, qobj, qwhen, qwhere, qwho):

#     dire_ob = {'situation': qsit, 'object': qobj}
#     try:
#         do = dirObsTab.query.filter_by(dir_obs=dire_ob, when=qwhen, where=qwhere, who=qwho).first()
#     except IntegrityError:
#         return{"message": "Direct Observation not found in the database"}, 400
    
#     print("Found the do: ", do)
#     input("events_db_status()")
#     return{"event found": do}ù

events  = []
weights = []
values  = []
global weight_counter
weight_counter = 0
global tab1
tab1 = 0

# global obs_ev_rowsblock
obs_ev_rowsblock = []

@app.route("/IE/events", methods=["PUT"])
def receiving_events_list():

    json_data = json.loads(request.data)
    events.extend(json_data)

    # filling up the first event tab in the db
    for event in events:
        ev = eventsTab( situation   = event['situation'],
                        obj         = event['object'],
                        where       = event['where'])
        db.session.add(ev)
    db.session.commit()

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

    # no_dupl = {}
    # no_dupl['already_j'] = []
    # no_dupl['already_k'] = []

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

    global tab1
    global weight_counter
    # events_types = []

    # print("#################################################")
    json_data = json.loads(request.data)
    # print(json_data)
    # input("put() first check")
    data_do, data_ih, reputation = NewpreProcessing(json_data)

    weights.append(reputation)

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
    result_do = []
    # values.append([])
    for i in range(len(direct_obs)):
        events_types = []

        print(direct_obs[i])
        query_ev    = eventsTab.query.filter_by(where=direct_obs[i]['where']).first()

        # first time
        if len(query_ev.observations)==0:

            ev = observedEventsTab( obs_situation   = direct_obs[i]['situation'],
                                    obs_object      = direct_obs[i]['obj'],
                                    confidence      = 100.)
            db.session.add(ev)
            query_ev.observations.append(ev)
            query_ev.observations[-1].event_id = query_ev.id
        

        elif len(query_ev.observations) > 0:
            for k in range(len(query_ev.observations)):
                if query_ev.observations[k] not in events_types:

                    events_types.append({'observation': query_ev.observations[k], 'times': 1})

                    for h in range(k, len(query_ev.observations)):
                        if query_ev.observations[h] == events_types[-1]['observation']:

                            events_types[-1]['times'] += 1

            # if not repetition:
            sits_db = [obs['observation'].obs_situation for obs in events_types]
            objs_db = [obs['observation'].obs_object for obs in events_types]

            zipped_obs_db   = list(zip(sits_db, objs_db))
            ob              = (direct_obs[i]['situation'], direct_obs[i]['obj'])

            # if this observation has been already reported, update the confidence for all the observations
            if ob in zipped_obs_db:
                
                index = zipped_obs_db.index(ob)
                events_types[index]['times'] += 1

                total_cases = sum(obs['times'] for obs in events_types)

                for m in range(len(query_ev.observations)):
                    
                    # events_types[i]['confidence'] = events_types[i]['times']*100 / total_cases
                    query_ev.observations[m].confidence = round(events_types[m]['times']*100 / total_cases, 2)
            
            # if its the first time this observation has been reported
            elif ob not in zipped_obs_db:

                total_cases = sum(obs['times'] for obs in events_types) + 1

                ev = observedEventsTab( obs_situation   = direct_obs[i]['situation'],
                                        obs_object      = direct_obs[i]['obj'],
                                        confidence      = round(1*100 / total_cases, 2))

                events_types.append({'observation': ev, 'times': 1})

                for n in range(len(query_ev.observations)):

                    query_ev.observations[n].confidence = round(events_types[n]['times']*100 / total_cases, 2)

                db.session.add(ev)
                query_ev.observations.append(ev)
                query_ev.observations[-1].event_id = query_ev.id
            
            if 100 - sum(query_ev.observations[counter].confidence for counter in range(len(query_ev.observations)) ) >= 0.1:
                print("************************************")
                for el in query_ev.observations:
                    print("obs_sit: ", el.obs_situation, "obs_object: ", el.obs_object, "conf: ", el.confidence, "event_id: ", el.event_id)
                input("ouch")
        

        query_do = dirObsTab.query.filter_by(   situation   = direct_obs[i]['situation'],
                                                obj         = direct_obs[i]['obj'],
                                                when        = direct_obs[i]['when'],
                                                where       = direct_obs[i]['where'],
                                                who         = direct_obs[i]['who']).first()
        # if the direct observation is not in the db
        if not query_do:
            return_flag = True
            result_ih = []
            do  = dirObsTab(    situation       = direct_obs[i]['situation'],
                                obj             = direct_obs[i]['obj'],
                                where           = direct_obs[i]["where"],
                                when            = direct_obs[i]["when"],
                                who             = direct_obs[i]["who"])

            # ackowledging we are adding a new direct observation to the db
            elem = {'situation': do.situation, 'object': do.obj, 'where': do.where, 'who': do.who}
            for el in events:
                # if the observation corresponds to the actual situation
                if el['situation'] == elem['situation'] and el['object'] == elem['object'] and el['where']==elem['where']:
                    try:
                        index = events.index(el)
                        # del events[index]
                        events[index]['correct'] += 1
                    except:
                        print("remove operation failed.")
                        pprint(events)
                        print("elem:    ", elem)
                        print(bool(elem in events))
                        input()
                # if the element is a "distorted" observation instead
                elif (el['situation'] != elem['situation'] or el['object'] != elem['object']) and el['where'] == elem['where']:
                    index = events.index(el)
                    events[index]['mistaken']['times'] += 1
                    events[index]['mistaken']['difference'].append(elem)
            # print(return_flag)
            # input("return_flag")
            db.session.add(do)
            result_do.append(do_schema.dump(do))
            

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
                    db.session.add(ih)
                    # result_ih.append(ih_schema.dump(infoHistoryTab.query.get(ih.id)))
                    do.info_histories.append(ih)
                    # ih.dir_obs_tab = do.id
                    do.info_histories[j].dir_obs_id = do.id
                    result_ih.append(ih_schema.dump(ih))
                result_do.append(result_ih)
            print("10")
        # if the direct observation is already in the db
        else:
            # print("###################################################")
            repetition_flag = True
            tab1 += 1
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
                        # print("ih: ", ih_schema.dump(ih(only('observer', 'a1', 'a2', 'where', 'when'))))
                        # for jump in query_do.info_histories:
                        #     print("jump_db: ", ih_schema.dump(jump))
                        # if ih not in query_do.info_histories:
                        # print("I have to add that jump!")
                        db.session.add(ih)
                        # result_ih.append(ih_schema.dump(infoHistoryTab.query.get(ih.id)))
                        query_do.info_histories.append(ih)
                        # ih.dir_obs_tab = do.id
                        query_do.info_histories[j].dir_obs_id = query_do.id
                        result_ih.append(ih_schema.dump(ih))
                result_do.append(result_ih)
                # query_ih = infoHistoryTab.query.filter_by(id=iden).all()
                # pprint(ih_schemas.dump(query_ih))
                # input()
            print("11")

    print("12")

    db.session.commit()
    # if repetition_flag:
    #     query = dirObsTab.query.filter_by(id=iden).first()
    #     pprint(ih_schemas.dump(query.info_histories))
    #     input()
    # input("after commit")
    # result_do = do_schema.dump(dirObsTab.query.get(do.id))

    # keep track if event has been uploaded on the db for the first time
    if return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do, "events": events}
    # keep track if all the events have been uploaded on the db
    # elif all_events_db:
    #     return {"message": "Created a new DO and IH.",  "DO": result_do, "all_events_db": events}
    # if an element which was already in the db was being uploaded
    elif not return_flag:
        return {"message": "Created a new DO and IH.",  "DO": result_do}



@app.route("/IE/<int:DO_id>", methods=["DELETE"])
def delete_(DO_id):

    query           = dirObsTab.query.options(joinedload(dirObsTab.info_histories))
    query_events    = eventsTab.query.options(joinedload(eventsTab.observations))

    latency = []
    counter1 = 0
    counter2 = 0
    for Obs in query:
        latency.append(Obs.info_histories[0].sent_at_loop - Obs.when)
        # s += Obs.info_histories[0].sent_at_loop - Obs.when
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
    weights.clear()



    return {"message": "tabs are cleared", "size_tab1": counter1, "size_tab2": counter2, "latency": statistics.mean(latency)}


if __name__=="__main__":
    app.run(debug=True)