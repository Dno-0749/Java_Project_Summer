from marshmallow import Schema, fields

class ActivityScheduleRequestSchema(Schema):
    activity_id = fields.Int(required=True)
    location = fields.Str(required=False)
    start_at = fields.Raw(required=False)
    end_at = fields.Raw(required=False)
    capacity = fields.Int(required=True)

class ActivityScheduleResponseSchema(Schema):
    id = fields.Int()
    activity_id = fields.Int()
    location = fields.Str(allow_none=True)
    start_at = fields.Raw(allow_none=True)
    end_at = fields.Raw(allow_none=True)
    capacity = fields.Int()
    status = fields.Str()