from marshmallow import Schema, fields


class ShoreExcursionRequestSchema(Schema):
    provider_id = fields.Int(required=True)
    name = fields.Str(required=True)
    date = fields.Str(required=False, allow_none=True)
    time = fields.Str(required=False, allow_none=True)
    location = fields.Str(required=False, allow_none=True)
    port_name = fields.Str(required=False, allow_none=True)
    description = fields.Str(required=False, allow_none=True)
    duration_hours = fields.Float(required=False, allow_none=True)
    capacity = fields.Int(required=True)
    registered = fields.Int(required=False, allow_none=True)
    fee = fields.Float(required=False, allow_none=True)
    price = fields.Float(required=False, allow_none=True)
    status = fields.Str(required=False, allow_none=True)


class ShoreExcursionUpdateSchema(Schema):
    provider_id = fields.Int(required=False)
    name = fields.Str(required=False)
    date = fields.Str(required=False, allow_none=True)
    time = fields.Str(required=False, allow_none=True)
    location = fields.Str(required=False, allow_none=True)
    port_name = fields.Str(required=False, allow_none=True)
    description = fields.Str(required=False, allow_none=True)
    duration_hours = fields.Float(required=False, allow_none=True)
    capacity = fields.Int(required=False)
    registered = fields.Int(required=False)
    fee = fields.Float(required=False)
    price = fields.Float(required=False)


class ShoreExcursionStatusSchema(Schema):
    status = fields.Str(required=True)


class ShoreExcursionResponseSchema(Schema):
    id = fields.Int()
    provider_id = fields.Int()
    name = fields.Str()
    date = fields.Str(allow_none=True)
    time = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    port_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    duration_hours = fields.Float(allow_none=True)
    capacity = fields.Int()
    registered = fields.Int()
    fee = fields.Float()
    price = fields.Float()
    rating = fields.Float()
    feedback_count = fields.Int()
    status = fields.Str()

