from flask import Flask, request
from flask_restful import Resource, Api, abort
from marshmallow import fields, Schema, ValidationError
from sqlalchemy import create_engine, MetaData, select, update, Table
from models import *

# Defining database
engine = create_engine("mysql+mysqldb://john:1234@localhost/TESTDB")
conn = engine.connect()
metadata = MetaData()
database_table = Table("stuff", metadata, autoload=True, autoload_with=engine)

app = Flask(__name__)
api = Api(app)


def does_exist(data_id):
    title = select([database_table]).where(database_table.c.title == data_id)
    table = conn.execute(title).fetchone()
    if not table:
        abort(404, message="doesn't exist.")


def price_limitaion(price):
    if price < 0:
        raise ValidationError('Price couldn\'t be negative!')
    if price > 1000:
        abort(400, message="The price is too high!")


class CRUD(Resource):
    # READ individually
    def get(self, data_id):
        does_exist(data_id)
        table = select([database_table]).where(database_table.c.title == data_id)
        result = conn.execute(table).fetchall()
        return [Input().dump(r) for r in result]


    # CREATE
    def post(self, data_id):
        schema = Input()
        things = request.get_json()
        result = schema.load(things)
        if not result.errors:
            ins = database_table.insert().values(result.data)
            conn.execute(ins)
            return result.data, 201
        else:
            return result.errors, 400

    # UPDATE
    def put(self, data_id):
        does_exist(data_id)
        schema = Input()
        things = request.get_json()
        result = schema.load(things)
        if not result.errors:
            ins = database_table.update().where(database_table.c.title == data_id).values(result.data)
            conn.execute(ins)
            return result.data, 201
        else:
            return result.errors, 400

    # DELETE
    def delete(self, data_id):
        does_exist(data_id)
        ins = database_table.delete().where(database_table.c.title == data_id)
        conn.execute(ins)
        return 'Data deleted!', 204


# READ totally
class AllDataRetrieve(Resource):
    def get(self):
        table = select([database_table])
        result = conn.execute(table).fetchall()
        return [dict(r) for r in result]


api.add_resource(CRUD, '/<string:data_id>')
api.add_resource(AllDataRetrieve, '/')

if __name__ == '__main__':
    app.run(debug=True)
