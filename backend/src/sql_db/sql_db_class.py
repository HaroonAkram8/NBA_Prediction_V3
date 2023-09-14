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