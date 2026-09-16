from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from api.schemas.auth import LoginUserRequestSchema, LoginUserResponseSchema, RigisterUserRequestSchema, RigisterUserResponseSchema
from api.schemas.todo import TodoRequestSchema, TodoResponseSchema
from api.schemas.itinerary import (
    CruiseRequestSchema, CruiseResponseSchema,
    PortRequestSchema, PortResponseSchema,
    CruiseDayRequestSchema, CruiseDayResponseSchema,
    CabinRequestSchema, CabinResponseSchema,
)
from api.schemas.activity import (
    ActivityRequestSchema, ActivityResponseSchema,
    ExcursionRequestSchema, ExcursionResponseSchema,
    RegistrationRequestSchema, RegistrationResponseSchema,
)
from api.schemas.report import InvoiceResponseSchema
from api.schemas.feedback import FeedbackRequestSchema, FeedbackResponseSchema
from api.schemas.passenger import PassengerRequestSchema, PassengerResponseSchema

spec = APISpec(
    title="Todo API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Đăng ký schema để tự động sinh model
spec.components.schema("TodoRequest", schema=TodoRequestSchema)
spec.components.schema("TodoResponse", schema=TodoResponseSchema)
spec.components.schema("LoginUserRequest", schema= LoginUserRequestSchema)
spec.components.schema("LoginUserResponse", schema= LoginUserResponseSchema)
spec.components.schema("RigisterUserRequest", schema= RigisterUserRequestSchema)
spec.components.schema("RigisterUserResponse", schema= RigisterUserResponseSchema)

# Nhóm Itinerary (Cruise Activity and Service Management System)
spec.components.schema("CruiseRequest", schema=CruiseRequestSchema)
spec.components.schema("CruiseResponse", schema=CruiseResponseSchema)
spec.components.schema("PortRequest", schema=PortRequestSchema)
spec.components.schema("PortResponse", schema=PortResponseSchema)
spec.components.schema("CruiseDayRequest", schema=CruiseDayRequestSchema)
spec.components.schema("CruiseDayResponse", schema=CruiseDayResponseSchema)
spec.components.schema("CabinRequest", schema=CabinRequestSchema)
spec.components.schema("CabinResponse", schema=CabinResponseSchema)

# Nhóm Activity / Excursion / Registration
spec.components.schema("ActivityRequest", schema=ActivityRequestSchema)
spec.components.schema("ActivityResponse", schema=ActivityResponseSchema)
spec.components.schema("ExcursionRequest", schema=ExcursionRequestSchema)
spec.components.schema("ExcursionResponse", schema=ExcursionResponseSchema)
spec.components.schema("RegistrationRequest", schema=RegistrationRequestSchema)
spec.components.schema("RegistrationResponse", schema=RegistrationResponseSchema)

# Nhóm Report / Reconciliation
spec.components.schema("InvoiceResponse", schema=InvoiceResponseSchema)

# Nhóm Feedback
spec.components.schema("FeedbackRequest", schema=FeedbackRequestSchema)
spec.components.schema("FeedbackResponse", schema=FeedbackResponseSchema)

# Nhóm Passenger
spec.components.schema("PassengerRequest", schema=PassengerRequestSchema)
spec.components.schema("PassengerResponse", schema=PassengerResponseSchema)