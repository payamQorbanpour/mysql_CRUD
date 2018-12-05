from marshmallow import fields, Schema
from app import price_limitaion


class Data(Schema):
    body = fields.Str()
    title = fields.String()
    price = fields.Integer(validate=price_limitaion)
    email = fields.Email()
