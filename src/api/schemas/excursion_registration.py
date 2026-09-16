from marshmallow import Schema, fields


class ExcursionRegistrationCreateSchema(Schema):
    passenger_id = fields.Integer(
        required=False,
        allow_none=True
    )

    excursion_id = fields.Integer(
        required=True
    )

    booking_id = fields.Integer(
        required=False,
        allow_none=True
    )

    guest_code = fields.String(
        required=False,
        allow_none=True
    )

    passenger_name = fields.String(
        required=False,
        allow_none=True
    )

    room = fields.String(
        required=False,
        allow_none=True
    )

    status = fields.String(
        required=False,
        load_default="REGISTERED"
    )

    notes = fields.String(
        required=False,
        allow_none=True
    )


class ExcursionRegistrationUpdateStatusSchema(Schema):
    status = fields.String(required=True)


class ExcursionRegistrationResponseSchema(Schema):
    id = fields.Integer()
    passenger_id = fields.Integer(allow_none=True)
    excursion_id = fields.Integer()
    booking_id = fields.Integer(allow_none=True)

    guest_code = fields.String(allow_none=True)
    passenger_name = fields.String(allow_none=True)
    room = fields.String(allow_none=True)

    status = fields.String()
    notes = fields.String(allow_none=True)

    checked_in = fields.Boolean()

    checked_in_at = fields.DateTime(
        allow_none=True
    )

    registered_at = fields.DateTime()
