from marshmallow import Schema, fields

class TourProviderRequestSchema(Schema):
    name = fields.Str(required=True)
    contact_phone = fields.Str(required=False)
    contact_email = fields.Str(required=False)
    address = fields.Str(required=False)

class TourProviderResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    contact_phone = fields.Str(allow_none=True)
    contact_email = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    status = fields.Str()