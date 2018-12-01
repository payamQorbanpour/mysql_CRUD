from flask import Flask, request
from flask_restful import Resource, Api, abort
from marshmallow import fields, Schema, ValidationError
from sqlalchemy import create_engine, MetaData, select, Table

# Defining database
engine = create_engine("mysql+mysqldb://john:1234@localhost/TESTDB")
conn = engine.connect()
metadata = MetaData()
stuff = Table("stuff", metadata, autoload=True, autoload_with=engine)

app = Flask(__name__)
api = Api(app)


def does_exist(stuff_id):
    this_stuff = all_stuff.find_one({"data": stuff_id})
    if not this_stuff:
        abort(404, message="doesn't exist.")


def price_limitaion(price):
    if price < 0:
        raise ValidationError('Price couldn\'t be negative!')
    if price > 1000:
        abort(400, message="The price is too high!")


class Input(Schema):
    body = fields.Str()
    title = fields.String()
    price = fields.Integer(validate=price_limitaion)
    email = fields.Email()


class Stuff(Resource):
    # READ individually
    def get(self, stuff_id):
        does_exist(stuff_id)
        stuff_bucket = []
        ins = Input()
        table = select([stuff]).where(stuff.c.title == stuff_id)
        result = conn.execute(table).fetchall()
        for r in result:
            serialize = ins.dump(r)
            stuff_bucket.append(serialize)
        return stuff_bucket

    # CREATE
    def post(self, stuff_id):
        schema = Input()
        things = request.get_json()
        result = schema.load(things)
        if not result.errors:
            ins = stuff.insert().values(result.data)
            engine.execute(ins)
            return result.data, 201
        else:
            return result.errors, 400

    # UPDATE
    def put(self, stuff_id):
        does_exist(stuff_id)
        schema = Input()
        things = request.get_json()
        result = schema.load(things)
        if not result.errors:
            all_stuff.update_one({"title": stuff_id}, {"$set": stuff})
            return result.data, 201
        else:
            return result.errors, 400

    # DELETE
    def delete(self, stuff_id):
        does_exist(stuff_id)
        all_stuff.delete_one({"title": stuff_id})
        return 'Data deleted!', 204


# READ totally
class AllStuff(Resource):
    def get(self):
        stuff_bucket = []
        table = select([stuff])
        result = conn.execute(table).fetchall()
        for r in result:
            stuff_bucket.append(dict(r))
        return stuff_bucket


api.add_resource(Stuff, '/<string:stuff_id>')
api.add_resource(AllStuff, '/')

if __name__ == '__main__':
    app.run(debug=True)
