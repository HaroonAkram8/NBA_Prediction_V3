import psycopg2 as pg
from psycopg2 import sql

class nba_psql:
    def __init__(self):
        self.connection = None

    def connect(self, sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str):
        try:
            self.connection = pg.connect(user=sql_user, password=sql_password, host=sql_host, port=sql_port, database=sql_database)
            return True
        except pg.Error:
            return False
    
    def disconnect(self):
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
            return True
        except pg.Error:
            return False
    
    def create_database(self, dbname: str) -> bool:
        success = False

        with self.connection.cursor() as cursor:
            self.connection.autocommit = True

            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", [dbname])
            exists = cursor.fetchone()
            if not exists:
                query = ''' CREATE DATABASE {} ; '''
                cursor.execute(sql.SQL(query).format(sql.Identifier(dbname)))

            # For some reason, this needs to be run here and in the upload_schema() function as well
            cursor.execute("CREATE SCHEMA IF NOT EXISTS nba_db_schema;")
            cursor.execute("ALTER DATABASE nba_db SET SEARCH_PATH TO nba_db_schema;")

            success = True

        self.connection.autocommit = False
        return success
    
    def upload_file(self, file_path: str):
        success = False

        with self.connection.cursor() as cursor:
            self.connection.autocommit = True

            file = open(file_path, "r")
            cursor.execute(file.read())

            success = True
        
        self.connection.autocommit = False
        return success
    
    def run_select_query(self, query: str):
        success = False
        all_data = {}

        with self.connection.cursor() as cursor:
            view_query = "CREATE TEMP VIEW temp AS " + query
            cursor.execute(view_query)

            data_query = "SELECT * FROM temp;"
            cursor.execute(data_query)
            all_data['columns'] = [desc[0] for desc in cursor.description]
            all_data['data'] = cursor.fetchall()

        return success, all_data

def main():
    from src.globals import (
        LOCAL_SQL_DATABASE,
        LOCAL_SQL_USERNAME,
        LOCAL_SQL_PORT,
        LOCAL_SQL_HOST,
        PRIVATE_DATA,
        SQL_LOCAL_INFO,
        SQL_LOCAL_PASSWORD
    )
    from src.utils import get_from_private_data

    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)

    psql_conn = nba_psql()
    psql_conn.connect(sql_user=LOCAL_SQL_USERNAME,
                      sql_password=password,
                      sql_host=LOCAL_SQL_HOST,
                      sql_port=LOCAL_SQL_PORT,
                      sql_database=LOCAL_SQL_DATABASE)

    # =============== EDIT BELOW FOR TESTING ===============
    query = "SELECT abbr FROM TeamInfo WHERE id > 1610612754;"
    _, return_dict = psql_conn.run_select_query(query=query)
    print(return_dict)
    # ======================================================

    psql_conn.disconnect()

if __name__ == "__main__":
    main()