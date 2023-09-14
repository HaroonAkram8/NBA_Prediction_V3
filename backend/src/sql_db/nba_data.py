import pandas as pd
from nba_api.stats import endpoints
from src.globals import HEADERS, SEASON_TYPE, SEASON, GAMELOG_COLUMNS

def get_team_game_logs(team_id, season_type, season):
    team_game_logs = endpoints.teamgamelogs.TeamGameLogs(team_id_nullable=team_id, season_type_nullable=season_type, season_nullable=season, headers=HEADERS)
    df_team_game_logs = team_game_logs.get_data_frames()
    return df_team_game_logs[0]

def update_team_game_log():
    print()

def main():
    print(get_team_game_logs(1610612761, SEASON_TYPE, SEASON).columns)

if __name__ == "__main__":
    main()