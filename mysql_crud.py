from flask import Flask
from flask_restful import Resource, Api, abort
from marshmallow import fields, Schema, ValidationError
from sqlalchemy import create_engine, MetaData, select, Table


# Defining database
engine = create_engine("mysql+mysqldb://john:1234@localhost/TESTDB")
conn = engine.connect()
metadata = MetaData()
stuff = Table('stuff', metadata, autoload=True, autoload_with=engine)

app = Flask(__name__)
api = Api(app)


# def does_exist(stuff_id):
#     this_stuff = all_stuff.find_one({"data": stuff_id})
#     if not this_stuff:
#         abort(404, message="doesn't exist.")


def price_limitaion(price):
    if price < 0:
        raise ValidationError('Price couldn\'t be negative!')
    if price > 1000:
        abort(400, message="The price is too high!")


class Input(Schema):
    data = fields.Str()
    title = fields.String()
    price = fields.Float(validate=price_limitaion)
    email = fields.Email()

#
# class Stuff(Resource):
#     # READ individually
#     def get(self, stuff_id):
#         this_stuff = all_stuff.find_one({"data": stuff_id}, {"_id": 0})
#         does_exist(stuff_id)
#         return this_stuff
#
#     # CREATE
#     def post(self, stuff_id):
#         stuff = request.get_json()
#         schema = Input()
#         result = schema.load(stuff)
#         all_stuff.insert_one(stuff)
#         return result, 201
#
#     # UPDATE
#     def put(self, stuff_id):
#         stuff = request.get_json()
#         schema = Input()
#         result = schema.load(stuff)
#         all_stuff.update_one({"data": stuff_id}, {"$set": stuff})
#         return result, 201
#
#     # DELETE
#     def delete(self, stuff_id):
#         does_exist(stuff_id)
#         all_stuff.delete_one({"data": stuff_id})
#         return 'Data deleted!', 204


# READ totally
class AllStuff(Resource):
    def get(self):
        table = select([stuff])
        result = conn.execute(table).fetchall()
        stringish = str(result)
        return stringish


# api.add_resource(Stuff, '/<string:stuff_id>')
api.add_resource(AllStuff, '/')

if __name__ == '__main__':
    app.run(debug=True)
