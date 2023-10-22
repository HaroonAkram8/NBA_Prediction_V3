import pandas as pd
import psycopg2 as pg
from psycopg2 import sql
from tqdm import tqdm

from src.globals import GAMELOG_COLUMNS, SQL_GAMELOG_COLUMNS

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

            self.connection.commit()
            success = True

        return success, all_data
    
    def insert_into_gamelogs(self, df_game_logs: pd.DataFrame):
        success = False
        df_game_logs = df_game_logs[GAMELOG_COLUMNS + ['AT_HOME']]
        tuples = [tuple(x) for x in df_game_logs.to_numpy()]

        with self.connection.cursor() as cursor:
            query = "INSERT INTO Gamelogs (GAME_ID, SEASON_YEAR, GAME_DATE, TEAM_ID, WL, PTS, MIN, FGM,FGA, FG_PCT, FG3M, FG3A, FG3_PCT, \
                    FTM, FTA, FT_PCT, OREB, DREB, REB, AST, TOV, STL, BLK, BLKA, PF, PFD, PLUS_MINUS, AT_HOME) \
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"
            
            for i in tqdm(range(0, len(tuples)), desc=f"Uploading gamelogs to the Gamelogs table"):
                cursor.execute(query, tuples[i])

            self.connection.commit()
            success = True

        return success

    def set_game_elos(self, elo_games):
        success = False

        with self.connection.cursor() as cursor:
            query = "UPDATE Gamelogs SET elo_rating = %s \
                    WHERE game_id = %s AND team_id = %s;"
            
            for i in tqdm(range(0, len(elo_games)), desc=f"Setting ELO rating for each game"):
                game_id, h_team_id, a_team_id, h_elo, a_elo = elo_games[i]
                cursor.execute(query, (h_elo, game_id, h_team_id))
                cursor.execute(query, (a_elo, game_id, a_team_id))

            self.connection.commit()
            success = True

        return success
    
    def select_team_info(self):
        success = False
        all_data = {}

        with self.connection.cursor() as cursor:
            query = "SELECT id, abbr, name FROM TeamInfo;"
            cursor.execute(query)

            all_data['columns'] = ['id', 'abbr', 'name']
            all_data['data'] = cursor.fetchall()

            self.connection.commit()
            success = True

        return success, all_data
    
    def select_gamelogs(self):
        success = False
        all_data = {}

        with self.connection.cursor() as cursor:
            query = "SELECT * FROM Gamelogs ORDER BY game_date ASC;"
            cursor.execute(query)

            all_data['columns'] = SQL_GAMELOG_COLUMNS
            all_data['data'] = cursor.fetchall()

            self.connection.commit()
            success = True

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