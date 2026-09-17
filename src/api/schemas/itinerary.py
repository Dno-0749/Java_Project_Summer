from marshmallow import Schema, fields


BOOKING_STATUSES = ("pending", "confirmed", "completed", "cancelled")


class BookingRequestSchema(Schema):
    ship_name = fields.Str(required=True)
    customer_name = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    status = fields.Str(required=False, load_default="pending")


class BookingResponseSchema(Schema):
    id = fields.Int()
    ship_name = fields.Str(allow_none=True)
    customer_name = fields.Str(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    status = fields.Str()
    created_at = fields.Raw()
    updated_at = fields.Raw()


class CruiseRequestSchema(Schema):
    name = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    status = fields.Str(required=False, load_default="planned")


class CruiseResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.Str()
    created_at = fields.Raw()
    updated_at = fields.Raw()


class PortRequestSchema(Schema):
    name = fields.Str(required=True)
    country = fields.Str(required=False)
    description = fields.Str(required=False)


class PortResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    country = fields.Str()
    description = fields.Str()


class CruiseDayRequestSchema(Schema):
    cruise_id = fields.Int(required=True)
    day_number = fields.Int(required=True)
    date = fields.Date(required=True)
    port_id = fields.Int(required=False, allow_none=True)
    arrival_time = fields.Time(required=False, allow_none=True)
    departure_time = fields.Time(required=False, allow_none=True)


class CruiseDayResponseSchema(Schema):
    id = fields.Int()
    cruise_id = fields.Int()
    day_number = fields.Int()
    date = fields.Date()
    port_id = fields.Int(allow_none=True)
    arrival_time = fields.Time(allow_none=True)
    departure_time = fields.Time(allow_none=True)


class CabinRequestSchema(Schema):
    cruise_id = fields.Int(required=True)
    cabin_number = fields.Str(required=True)


class CabinResponseSchema(Schema):
    id = fields.Int()
    cruise_id = fields.Int()
    cabin_number = fields.Str()
