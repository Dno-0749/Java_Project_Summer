from marshmallow import Schema, fields


class ActivityRequestSchema(Schema):
    cruise_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    location = fields.Str(required=False)
    start_time = fields.DateTime(required=False, allow_none=True)
    end_time = fields.DateTime(required=False, allow_none=True)
    capacity = fields.Int(required=False, allow_none=True)
    fee = fields.Decimal(required=False, load_default=0)
    is_included_in_package = fields.Bool(required=False, load_default=False)


class ActivityResponseSchema(Schema):
    id = fields.Int()
    cruise_id = fields.Int()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    start_time = fields.DateTime(allow_none=True)
    end_time = fields.DateTime(allow_none=True)
    capacity = fields.Int(allow_none=True)
    fee = fields.Decimal(as_string=True)
    is_included_in_package = fields.Bool()


class ExcursionRequestSchema(Schema):
    cruise_day_id = fields.Int(required=True)
    name = fields.Str(required=True)
    provider_name = fields.Str(required=False)
    gathering_time = fields.DateTime(required=False, allow_none=True)
    return_time = fields.DateTime(required=False, allow_none=True)
    capacity = fields.Int(required=False, allow_none=True)
    price = fields.Decimal(required=False, load_default=0)


class ExcursionResponseSchema(Schema):
    id = fields.Int()
    cruise_day_id = fields.Int()
    name = fields.Str()
    provider_name = fields.Str(allow_none=True)
    gathering_time = fields.DateTime(allow_none=True)
    return_time = fields.DateTime(allow_none=True)
    capacity = fields.Int(allow_none=True)
    price = fields.Decimal(as_string=True)
    status = fields.Str()


class RegistrationRequestSchema(Schema):
    passenger_id = fields.Int(required=True)
    activity_id = fields.Int(required=False, allow_none=True)
    excursion_id = fields.Int(required=False, allow_none=True)


class RegistrationResponseSchema(Schema):
    id = fields.Int()
    passenger_id = fields.Int()
    activity_id = fields.Int(allow_none=True)
    excursion_id = fields.Int(allow_none=True)
    status = fields.Str()
    registered_at = fields.Raw()
