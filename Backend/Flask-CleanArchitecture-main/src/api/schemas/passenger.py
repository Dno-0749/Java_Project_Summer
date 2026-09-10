from marshmallow import Schema, fields


class PassengerRequestSchema(Schema):
    cruise_id = fields.Int(required=True)
    full_name = fields.Str(required=True)
    cabin_id = fields.Int(required=False, allow_none=True)


class PassengerResponseSchema(Schema):
    id = fields.Int()
    cruise_id = fields.Int()
    full_name = fields.Str()
    cabin_id = fields.Int(allow_none=True)
    qr_code = fields.Str(allow_none=True)
    rfid_code = fields.Str(allow_none=True)
