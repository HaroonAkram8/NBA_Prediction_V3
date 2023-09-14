from src.sql_db.sql_db_class import nba_psql
from src.sql_db.nba_data import get_all_team_game_logs

from src.utils import get_from_private_data, seasons_list
from src.globals import (
        LOCAL_SQL_DATABASE,
        LOCAL_SQL_USERNAME,
        LOCAL_SQL_PORT,
        LOCAL_SQL_HOST,
        PRIVATE_DATA,
        SQL_LOCAL_INFO,
        SQL_LOCAL_PASSWORD,
        SEASON_TYPE
    )

def update_sql_db(sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str, seasons: list, season_type: str):
    psql_conn = nba_psql()

    psql_conn.connect(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database)

    query = "SELECT id FROM TeamInfo;"
    success, return_dict = psql_conn.run_select_query(query=query)
    team_ids = format_team_ids(unformatted_ids=return_dict['data'])
    
    df_all_game_logs = get_all_team_game_logs(team_ids=team_ids, seasons=seasons, season_type=season_type)
    if not success:
        print('ERROR: Failed to retrieve game logs...')
        return False
    print('SUCCESS: Retrieved game logs...')
    
    success = psql_conn.insert_into_gamelogs(df_game_logs=df_all_game_logs)
    if not success:
        print('ERROR: Failed to upload gamelogs to Postgresql...')
        return False
    print('SUCCESS: Uploaded gamelogs to Postgresql...')
    
    return psql_conn.disconnect()

def format_team_ids(unformatted_ids: list):
    return [val for sublist in unformatted_ids for val in sublist]

def main():
    seasons = seasons_list(2012, 2022)
    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)
    update_sql_db(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT,
                  sql_database=LOCAL_SQL_DATABASE, seasons=seasons, season_type=SEASON_TYPE)

if __name__ == "__main__":
    main()