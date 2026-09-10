from marshmallow import Schema, fields


class InvoiceResponseSchema(Schema):
    id = fields.Int()
    onboard_account_id = fields.Int()
    total_amount = fields.Decimal(as_string=True)
    status = fields.Str()
    issued_at = fields.Raw()
