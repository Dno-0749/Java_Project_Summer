from infrastructure.databases.factory_database import FactoryDatabase
from infrastructure.databases.base import Base
# from infrastructure.databases.mssql import init_mssql
# from infrastructure.databases.postgres import init_postgres
from infrastructure.models import course_register_model, todo_model, user_model, course_model, consultant_model, appointment_model, program_model, feedback_model,survey_model
from infrastructure.models.auth import auth_user_model, auth_role_model,auth_funtion_model
from infrastructure.models.sell import sell_customer_model, sell_product_model, sell_invoice_model
from infrastructure.models.pay import pay_tran_model

# Cruise Activity and Service Management models
from infrastructure.models.cruise import (
    port_model,
    cruise_model,
    cruise_day_model,
    cabin_model,
    passenger_model,
    activity_model,
    shore_excursion_model,
    registration_model,
    checkin_model,
    onboard_account_model,
    transaction_model,
    invoice_model,
    feedback_model,
    notification_model,
)

def init_db(app):
    # init_mssql(app)
    FactoryDatabase.get_database('POSTGREE').init_database(app)
    # init_postgres(app)

# Base ở đây được import từ infrastructure.databases.base, dùng chung
# cho MỌI model (kể cả các model cruise mới) để Base.metadata.create_all()
# trong DatabasePostgres.init_database() có thể tạo đủ bảng trên Supabase.