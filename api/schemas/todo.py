from marshmallow import Schema, fields

class TodoRequestSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True)

class TodoResponseSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True)
    created_at = fields.Raw(required=True)
    updated_at = fields.Raw(required=True) 