from src.sql_db.sql_db_class import nba_psql
from src.sql_db.nba_data import get_all_team_game_logs, calculate_elo_rating

from src.global_utils import get_from_private_data, seasons_list
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

def elo_update(sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str, seasons: list, season_type: str):
    psql_conn = nba_psql()
    psql_conn.connect(sql_user=sql_user, sql_password=sql_password, sql_host=sql_host, sql_port=sql_port, sql_database=sql_database)
    
    query = "SELECT g1.season_year, g1.game_id AS game_id, g1.team_id AS h_team_id, g2.team_id AS a_team_id, g1.pts AS h_pts, g2.pts AS a_pts \
            FROM Gamelogs g1 JOIN Gamelogs g2 \
            ON g1.game_id = g2.game_id AND g1.at_home AND NOT g2.at_home AND g1.elo_rating IS NULL \
            ORDER BY g1.game_date;"
    success, games_needing_elo = psql_conn.run_select_query(query)
    if not success:
        print('ERROR: Failed to retrieve game logs...')
        return False
    print('SUCCESS: Retrieved game logs...')

    latest_elo_ratings = set_init_elo(psql_conn)
    games_with_elos = generate_elo_ratings(latest_elo_ratings=latest_elo_ratings, games_needing_elo=games_needing_elo)

    success = psql_conn.set_game_elos(elo_games=games_with_elos)
    if not success:
        print('ERROR: Failed to set game ELO ratings...')
        return False
    print('SUCCESS: Set all game ELO ratings...')

    return psql_conn.disconnect()

def generate_elo_ratings(latest_elo_ratings: dict, games_needing_elo: dict):
    games_with_elos = []
    curr_season_year = games_needing_elo['data'][0][0]
    for game in games_needing_elo['data']:
        season_year, game_id, h_team_id, a_team_id, h_pts, a_pts = game

        if curr_season_year != season_year:
            season_year = curr_season_year
            latest_elo_ratings = update_new_season_elos(last_season_elo_ratings=latest_elo_ratings)

        h_wins = h_pts >= a_pts
        mov_winner = abs(h_pts - a_pts)
        h_new_elo = calculate_elo_rating(team_elo=latest_elo_ratings[h_team_id], opp_elo=latest_elo_ratings[a_team_id], won=h_wins, MOV_winner=mov_winner)
        a_new_elo = calculate_elo_rating(team_elo=latest_elo_ratings[a_team_id], opp_elo=latest_elo_ratings[h_team_id], won=not h_wins, MOV_winner=mov_winner)

        latest_elo_ratings[h_team_id] = h_new_elo
        latest_elo_ratings[a_team_id] = a_new_elo

        games_with_elos.append([game_id, h_team_id, a_team_id, h_new_elo, a_new_elo])
    
    return games_with_elos

def set_init_elo(psql_conn: nba_psql, default_elo: float=1500.0):
    _, team_ids = psql_conn.select_team_info()

    default_elo_ratings = {}
    for team in team_ids['data']:
        team_id = team[0]
        default_elo_ratings[team_id] = default_elo

    return default_elo_ratings

def update_new_season_elos(last_season_elo_ratings: dict, base_elo: float=1505.0):
    new_season_elo_ratings = {}

    for team_id in last_season_elo_ratings.keys():
        new_season_elo_ratings[team_id] = last_season_elo_ratings[team_id] * 0.75 + base_elo * 0.25
    
    return new_season_elo_ratings

def format_team_ids(unformatted_ids: list):
    return [val for sublist in unformatted_ids for val in sublist]

def main():
    seasons = seasons_list(2012, 2022)
    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)
    update_sql_db(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT,
                  sql_database=LOCAL_SQL_DATABASE, seasons=seasons, season_type=SEASON_TYPE)
    elo_update(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT,
               sql_database=LOCAL_SQL_DATABASE, seasons=seasons, season_type=SEASON_TYPE)

if __name__ == "__main__":
    main()