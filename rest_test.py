from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
from marshmallow import fields, Schema, ValidationError
from pymongo import MongoClient


app = Flask(__name__)
api = Api(app)

all_stuff = MongoClient().crud_db.stuff

def abort_if_stuff_doesnt_exist(stuff_id):
    if stuff_id not in all_stuff:
        abort(404, message="doesn't exist.")


def price_limitaion(price):
    if price < 0:
        raise ValidationError('Price couldn\'t be negative!')
    if price > 1000:
        abort(400, message="It is too high!")


class Input(Schema):
    data = fields.Str()
    title = fields.String()
    price = fields.Float(validate=price_limitaion)
    email = fields.Email()


class Stuff(Resource):
    # READ individually
    def get(self, stuff_id):
        abort_if_stuff_doesnt_exist(stuff_id)
        return all_stuff[stuff_id]

    # CREATE
    def post(self, stuff_id):
        stuff = request.get_json()
        schema = Input()
        result = schema.load(stuff)
        insert_res = all_stuff.insert_one(stuff)
        return result, 201

    # UPDATE
    def put(self, stuff_id):
        stuff = request.get_json()
        schema = Input()
        result = schema.load(stuff)
        insert_res = all_stuff.insert_one(stuff)
        return result, 201

    # DELETE
    def delete(self, stuff_id):
        abort_if_stuff_doesnt_exist(stuff_id)
        stuff = request.get_json()
        all_stuff.delete_one(stuff)
        return '', 204

# READ totally
class AllStuff(Resource):
    def get(self):
        bucket = []
        cursor = all_stuff.find({}, {"_id": 0})
        for result in cursor:
            bucket.append(result)
        return bucket

api.add_resource(Stuff, '/<string:stuff_id>')
api.add_resource(AllStuff, '/')

if __name__ == '__main__':
    app.run(debug=True)
