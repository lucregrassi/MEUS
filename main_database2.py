from flask import Flask, request
from sqlalchemy.exc import IntegrityError
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, inputs
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields as mafields, ValidationError, INCLUDE, EXCLUDE, pre_load
from flask_marshmallow import Marshmallow
import json
from utils import preProcessing

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

    def __repr__(self):
        return f"dirObsTab(id = {id}\n dir_obs = {dir_obs}\n when = {when}\n where = {where}\n who = {who}\n"


class infoHistoryTab(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    dir_obs_id  = db.Column(db.Integer, db.ForeignKey("dir_obs_tab.id"))
    a1          = db.Column(db.Integer, nullable=False)
    a2          = db.Column(db.Integer, nullable=False)
    where       = db.Column(db.Integer, nullable=False)
    # w1          = db.Column(db.Integer)
    # w2          = db.Column(db.Integer)
    when        = db.Column(db.Integer, nullable=False)

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
    id          = mafields.Integer(dump_only=True)
    a1          = mafields.Integer()
    a2          = mafields.Integer()
    where       = mafields.Integer()
    # w1        = mafields.Integer()
    # w2        = mafields.Integer()
    when        = mafields.Integer()


do_schema   = dirObsSchema()
do_schemas  = dirObsSchema(many=True)
ih_schema   = infoHistorySchema()
ih_schemas  = infoHistorySchema(many=True)


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

    return {"DO": DO_res, "infos": infos}




@app.route("/IE/<int:DO_id>", methods=["PUT"])
def put(DO_id):

    print("#################################################")
    json_data = json.loads(request.data)
    data_do, data_ih = preProcessing(json_data)
    # It's me! Mariooo!
    print ("processed_data: " +str(data_do) + "\n" + str(data_ih))
    print("and here as well")

    flag = False
    if not data_do:
        print("2")
        return {"message": "No input data provided"}, 400
        print("3")
    # Validate and deserialize input
    elif not data_ih:
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
    # Querying database
    print("8")
    try:
        res = dirObsTab.query.filter_by(id=DO_id).first()
        # print("9")
    except IntegrityError:
        # abort(409, message="IE_id already taken")
        return {"message": "DO_id already taken"}

    print("9")
    result_do = []
    for i in range(len(direct_obs)):
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
                ih = infoHistoryTab(    a1      = info_history[i][j]['a1'],
                                        a2      = info_history[i][j]['a2'],
                                        where   = info_history[i][j]['where'],
                                        when    = info_history[i][j]['when'])
                db.session.add(ih)
                # result_ih.append(ih_schema.dump(infoHistoryTab.query.get(ih.id)))
                do.info_histories.append(ih)
                # ih.dir_obs_tab = do.id
                do.info_histories[j].dir_obs_id = do.id
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
    # do = dirObsTab.query.filter_by(id=DO_id).first()
    # ih = infoHistoryTab.query.filter_by(id=DO_id).first()

    if not do: #or not ih:
        abort(404, message="This DO associated with this ID is not in the database")

    result_do = []
    result_ih = []

    for res in do:
        result_do.append(do_schema.dump(dirObsTab.query.get(res.id)))
        for elem in res.info_histories:
            ih  = infoHistoryTab.query.get(elem.id)
            result_ih.append(ih_schema.dump(ih))
            db.session.delete(ih)
        db.session.delete(res)
    db.session.commit()
    return {"I have deleted do": result_do,
            "I have deleted ih": result_ih,
            "return code": 204}


if __name__=="__main__":
    app.run(debug=True)