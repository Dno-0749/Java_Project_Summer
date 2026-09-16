from marshmallow import Schema, fields


class FeedbackRequestSchema(Schema):
    passenger_id = fields.Int(required=True)
    target_type = fields.Str(required=True)
    target_id = fields.Int(required=False, allow_none=True)
    target_name = fields.Str(required=False, allow_none=True)
    rating = fields.Int(required=True)
    comment = fields.Str(required=False, allow_none=True)


class FeedbackResponseSchema(Schema):
    id = fields.Int()
    passenger_id = fields.Int()
    target_type = fields.Str()
    target_id = fields.Int(allow_none=True)
    target_name = fields.Str(allow_none=True)
    rating = fields.Int()
    comment = fields.Str(allow_none=True)
    created_at = fields.Raw()
