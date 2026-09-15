

from infrastructure.databases.abstract_database import AbstractDatabase
from infrastructure.databases.database_mssql import DatabaseMSSQL
from infrastructure.databases.database_postgres import DatabasePostgres


class FactoryDatabase:
    # Cache instance theo database_type - đảm bảo create_engine() (và pool
    # kết nối bên trong) CHỈ được tạo 1 LẦN DUY NHẤT cho cả vòng đời app,
    # thay vì mỗi lần gọi get_database() lại tạo 1 engine/pool mới (đây
    # chính là nguyên nhân gây tràn giới hạn connection pool của Supabase).
    _instances = {}

    @staticmethod
    def get_database(database_type) -> AbstractDatabase:
        if database_type in FactoryDatabase._instances:
            return FactoryDatabase._instances[database_type]

        if database_type == 'MSSQL':
            instance = DatabaseMSSQL()
        elif database_type == 'POSTGREE':
            instance = DatabasePostgres()
        else:
            raise ValueError(f"Unsupported database type: {database_type}")

        FactoryDatabase._instances[database_type] = instance
        return instance 