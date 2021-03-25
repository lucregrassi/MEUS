import json
from utils import NewpreProcessing
from flask import Flask, request
from collections import defaultdict
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, inputs
from marshmallow import Schema, fields as mafields, ValidationError, INCLUDE, EXCLUDE, pre_load

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databaseMEUS.db'
db = SQLAlchemy(app)
# ma = Marshmallow(app)


### MODEL ###

class dirObsTab(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    dir_obs         = db.Column(db.JSON, nullable=False) 
    when            = db.Column(db.Integer, nullable=False)
    where           = db.Column(db.Integer, nullable=False)
    # Information element or direct observation
    who             = db.Column(db.Integer, nullable=False)
    info_histories  = db.relationship('infoHistoryTab', backref="dir_obs_tab", lazy=True)

    # def __repr__(self):
    #     return f"dirObsTab(id = {id}\n dir_obs = {dir_obs}\n when = {when}\n where = {where}\n who = {who}\n"


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

# db.create_all()


##### SCHEMAS #####


class dirObsSchema(Schema):
    # class Meta:
    #     unknown=INCLUDE
    id                  = mafields.Integer(dump_only=True)
    dir_obs             = mafields.Dict(keys=mafields.Str(), values=mafields.Str())
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
#     return{"event found": do}

    


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

    print("#################################################")
    json_data = json.loads(request.data)
    print(json_data)
    # input("put() first check")
    data_do, data_ih = NewpreProcessing(json_data)

    print ("processed_data: " +str(data_do) + "\n" + str(data_ih))
    print("and here as well")
    # input("put() second check")

    flag = False
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
        print ("direct_obs: " +str(direct_obs))
        print ("info_history: " +str(info_history))
    except ValidationError as err:
        print("7")
        return err.messages, 422

    print("9")
    result_do = []
    for i in range(len(direct_obs)):
        query_do = dirObsTab.query.filter_by(   dir_obs = direct_obs[i]['dir_obs'],
                                                when    = direct_obs[i]['when'],
                                                where   = direct_obs[i]['where'],
                                                who     = direct_obs[i]['who']).first()
        # if the direct observation is not in the db
        if not query_do:
            result_ih = []
            do  = dirObsTab(    #id              = DO_id,
                                dir_obs         = direct_obs[i]["dir_obs"],
                                where           = direct_obs[i]["where"],
                                when            = direct_obs[i]["when"],
                                who             = direct_obs[i]["who"])
            db.session.add(do)
            result_do.append(do_schema.dump(do))

            if not flag:
                for j in range(len(info_history[i])):
                    ih = infoHistoryTab(    observer    = info_history[i][j]['observer'],    
                                            a1          = info_history[i][j]['a1'],
                                            a2          = info_history[i][j]['a2'],
                                            sender      = info_history[i][j]['sender'],
                                            where       = info_history[i][j]['where'],
                                            when        = info_history[i][j]['when'],
                                            sent_at_loop    =info_history[i][j]['sent_at_loop'])
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
            result_ih = []
            if not flag:
                for j in range(len(info_history[i])):
                    ih = infoHistoryTab(    observer    = info_history[i][j]['observer'],    
                                            a1          = info_history[i][j]['a1'],
                                            a2          = info_history[i][j]['a2'],
                                            sender      = info_history[i][j]['sender'],
                                            where       = info_history[i][j]['where'],
                                            when        = info_history[i][j]['when'],
                                            sent_at_loop    =info_history[i][j]['sent_at_loop'])
                    db.session.add(ih)
                    # result_ih.append(ih_schema.dump(infoHistoryTab.query.get(ih.id)))
                    query_do.info_histories.append(ih)
                    # ih.dir_obs_tab = do.id
                    query_do.info_histories[j].dir_obs_id = query_do.id
                    result_ih.append(ih_schema.dump(ih))
                result_do.append(result_ih)
            print("10")

    print("11")

    db.session.commit()
    # result_do = do_schema.dump(dirObsTab.query.get(do.id))
    return {"message": "Created a new DO and IH.",  "DO": result_do}



@app.route("/IE/<int:DO_id>", methods=["DELETE"])
def delete_(DO_id):

    do = dirObsTab.query.all()
    ih = infoHistoryTab.query.all()
    for i in range(len(do)):
        db.session.delete(do[i])
    for j in range(len(ih)):
        db.session.delete(ih[j])
    db.session.commit()
    # do = dirObsTab.query.filter_by(id=DO_id).first()
    # ih = infoHistoryTab.query.filter_by(id=DO_id).first()

    # if not do: # or not ih:
    #     abort(404, message="This DO associated with this ID is not in the database")

    # result_do = []
    # result_ih = []

    # for res in do:
    #     result_do.append(do_schema.dump(dirObsTab.query.get(res.id)))
    #     for elem in res.info_histories:
    #         ih  = infoHistoryTab.query.get(elem.id)
    #         result_ih.append(ih_schema.dump(ih))
    #         db.session.delete(ih)
    #     db.session.delete(res)
    # db.session.commit()
    # return {"I have deleted do": result_do,
    #         "I have deleted ih": result_ih,
    #         "return code": 204}
    return {"message": "tabs are cleared"}


if __name__=="__main__":
    app.run(debug=True)