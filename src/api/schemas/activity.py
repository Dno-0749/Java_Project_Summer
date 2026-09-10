from marshmallow import Schema, fields


class ActivityRequestSchema(Schema):
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    description = fields.Str(load_default="")
    status = fields.Str(load_default="Sắp diễn ra")
    capacity = fields.Int(load_default=0)
    registered = fields.Int(load_default=0)
    price = fields.Int(load_default=0)
    activity_type = fields.Str(load_default="Miễn phí")


class ActivityResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    location = fields.Str()
    description = fields.Str()
    status = fields.Str()
    capacity = fields.Int()
    registered = fields.Int()
    price = fields.Int()
    activity_type = fields.Str()
    rating = fields.Float()
    feedback_count = fields.Int()
    created_at = fields.Raw()
    updated_at = fields.Raw()