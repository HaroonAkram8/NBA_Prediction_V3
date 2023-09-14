import pandas as pd
from nba_api.stats import endpoints
from src.globals import HEADERS, GAMELOG_COLUMNS

def get_all_team_game_logs(team_ids: list, seasons: list, season_type: str):
    #df1.append(df2)
    df_all_game_logs = pd.DataFrame(columns=GAMELOG_COLUMNS)
    
    for team_id in team_ids:
        for season in seasons:
            df_team_game_logs = get_team_game_logs(team_id=team_id, season_type=season_type, season=season)
            df_all_game_logs = pd.concat([df_all_game_logs, df_team_game_logs], ignore_index=True)

    return df_all_game_logs

def get_team_game_logs(team_id: int, season_type: str, season: str):
    team_game_logs = endpoints.teamgamelogs.TeamGameLogs(team_id_nullable=team_id, season_type_nullable=season_type, season_nullable=season, headers=HEADERS)
    df_team_game_logs = team_game_logs.get_data_frames()
    return df_team_game_logs[0][GAMELOG_COLUMNS]

def main():
    from src.globals import SEASON_TYPE, SEASON
    #print(get_team_game_logs(1610612761, SEASON_TYPE, SEASON)[0:5])
    print(get_all_team_game_logs([1610612761, 1610612743], ['2021-22', '2022-23'], SEASON_TYPE))

if __name__ == "__main__":
    main()