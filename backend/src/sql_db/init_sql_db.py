from src.sql_db.sql_db_class import nba_psql
from src.globals import (
    LOCAL_SQL_DATABASE,
    LOCAL_SQL_USERNAME,
    LOCAL_SQL_PORT,
    LOCAL_SQL_HOST,
    PRIVATE_DATA,
    SQL_LOCAL_INFO,
    SQL_LOCAL_PASSWORD
)

def init_sql_db(sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str, schema_path: str, team_info_path: str):
    if not create_db(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database):
        print('ERROR: Failed to create database in Postgresql...')
        return False
    print('SUCCESS: Created database in Postgresql...')

    if not upload_file_to_db(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database, file_path=schema_path):
        print('ERROR: Failed to upload schema to Postgresql...')
        return False
    print('SUCCESS: Uploaded schema to Postgresql...')

    if not upload_file_to_db(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database, file_path=team_info_path):
        print('ERROR: Failed to upload teams to Postgresql...')
        return False
    print('SUCCESS: Uploaded teams to Postgresql...')

    return True

def create_db(sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str):
    psql_conn = nba_psql()

    if psql_conn.connect(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database='postgres'):
        if psql_conn.create_database(dbname=sql_database):
            return psql_conn.disconnect()
    
    return False

def upload_file_to_db(sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str, file_path: str):
    psql_conn = nba_psql()

    if psql_conn.connect(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database):
        if psql_conn.upload_file(file_path=file_path):
            return psql_conn.disconnect()
    
    return False

def main():
    from src.global_utils import get_from_private_data
    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)

    general_path = './backend/src/sql_db/sql_schema_and_queries/'
    schema_path = general_path + 'schema.ddl'
    team_info_path = general_path + 'populate_team_info.ddl'

    init_sql_db(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT,
                sql_database=LOCAL_SQL_DATABASE, schema_path=schema_path, team_info_path=team_info_path)

if __name__ == "__main__":
    main()