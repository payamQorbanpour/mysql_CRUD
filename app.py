from flask import Flask, request
from flask_restful import Resource, Api, abort
from marshmallow import fields, Schema, ValidationError
from sqlalchemy import create_engine, MetaData, select, update, Table
from models import *

# Defining database
engine = create_engine("mysql+mysqldb://john:1234@localhost/TESTDB")
conn = engine.connect()
metadata = MetaData()
stuff = Table("stuff", metadata, autoload=True, autoload_with=engine)

app = Flask(__name__)
api = Api(app)


def does_exist(stuff_id):
    title = select([stuff]).where(stuff.c.title == stuff_id)
    this_stuff = conn.execute(title).fetchone()
    if not this_stuff:
        abort(404, message="doesn't exist.")


def price_limitaion(price):
    if price < 0:
        raise ValidationError('Price couldn\'t be negative!')
    if price > 1000:
        abort(400, message="The price is too high!")


class Stuff(Resource):
    # READ individually
    def get(self, stuff_id):
        does_exist(stuff_id)
        table = select([stuff]).where(stuff.c.title == stuff_id)
        result = conn.execute(table).fetchall()
        return [Input().dump(r) for r in result]


    # CREATE
    def post(self, stuff_id):
        schema = Input()
        things = request.get_json()
        result = schema.load(things)
        if not result.errors:
            ins = stuff.insert().values(result.data)
            conn.execute(ins)
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
            ins = stuff.update().where(stuff.c.title == stuff_id).values(result.data)
            conn.execute(ins)
            return result.data, 201
        else:
            return result.errors, 400

    # DELETE
    def delete(self, stuff_id):
        does_exist(stuff_id)
        ins = stuff.delete().where(stuff.c.title == stuff_id)
        conn.execute(ins)
        return 'Data deleted!', 204


# READ totally
class AllStuff(Resource):
    def get(self):
        table = select([stuff])
        result = conn.execute(table).fetchall()
        return [dict(r) for r in result]


api.add_resource(Stuff, '/<string:stuff_id>')
api.add_resource(AllStuff, '/')

if __name__ == '__main__':
    app.run(debug=True)
