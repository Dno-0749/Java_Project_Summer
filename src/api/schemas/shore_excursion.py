from marshmallow import Schema, fields

class ShoreExcursionRequestSchema(Schema):
    provider_id = fields.Int(required=True)
    name = fields.Str(required=True)
    port_name = fields.Str(required=False)
    description = fields.Str(required=False)
    duration_hours = fields.Float(required=False)
    capacity = fields.Int(required=True)
    fee = fields.Float(required=False)

class ShoreExcursionStatusSchema(Schema):
    status = fields.Str(required=True)

class ShoreExcursionResponseSchema(Schema):
    id = fields.Int()
    provider_id = fields.Int()
    name = fields.Str()
    port_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    duration_hours = fields.Float(allow_none=True)
    capacity = fields.Int()
    fee = fields.Float()
    status = fields.Str()