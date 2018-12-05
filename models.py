from marshmallow import fields, Schema, ValidationError
from app import price_limitaion


class Input(Schema):
    body = fields.Str()
    title = fields.String()
    price = fields.Integer(validate=price_limitaion)
    email = fields.Email()
