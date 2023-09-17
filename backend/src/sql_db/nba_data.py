import pandas as pd
import numpy as np
from tqdm import tqdm

from nba_api.stats import endpoints
from src.globals import HEADERS, GAMELOG_COLUMNS, WIN, LOSS

def get_all_team_game_logs(team_ids: list, seasons: list, season_type: str):
    columns = GAMELOG_COLUMNS + ['MATCHUP']
    df_all_game_logs = pd.DataFrame(columns=columns)

    for season in seasons:
        for i in tqdm(range(0, len(team_ids)), desc=f"Retrieving game logs for each NBA team in the {season} season"):
            df_team_game_logs = get_team_game_logs(team_id=team_ids[i], season_type=season_type, season=season, columns=columns)
            df_all_game_logs = pd.concat([df_all_game_logs, df_team_game_logs], ignore_index=True)

    df_all_game_logs['GAME_DATE'] = df_all_game_logs['GAME_DATE'].apply(lambda x: x.replace('T00:00:00', ''))
    df_all_game_logs['WL'] = np.where(df_all_game_logs['WL'] == 'W', WIN, LOSS)
    df_all_game_logs['AT_HOME'] = df_all_game_logs['MATCHUP'].apply(lambda x: not '@' in x)
    df_all_game_logs = df_all_game_logs.drop('MATCHUP', axis=1)

    return df_all_game_logs

def get_team_game_logs(team_id: int, season_type: str, season: str, columns: list):
    team_game_logs = endpoints.teamgamelogs.TeamGameLogs(team_id_nullable=team_id, season_type_nullable=season_type, season_nullable=season, headers=HEADERS)
    df_team_game_logs = team_game_logs.get_data_frames()
    return df_team_game_logs[0][columns]

def calculate_elo_rating(team_elo: float, opp_elo: float, won: bool, MOV_winner: int):
    # R_i = k * (S_team - E_team + R_(i-1))
    E_ratio = (opp_elo - team_elo) / 400.0
    E_team = 1.0 / (1 + 10 ** E_ratio)

    S_team = 0
    elo_diff = opp_elo - team_elo
    if won:
        S_team = 1
        elo_diff = -1.0 * elo_diff
    
    k = 20.0 * ((MOV_winner + 3) ** 0.8) / (7.5 + 0.006 * elo_diff)

    return k * (S_team - E_team) + team_elo

def main():
    from src.globals import SEASON_TYPE, SEASON
    #print(get_team_game_logs(1610612761, SEASON_TYPE, SEASON, columns=[]).columns)
    df_game_logs = get_all_team_game_logs([1610612761], ['2022-23'], SEASON_TYPE)

    columns = df_game_logs.columns
    values_list = df_game_logs.values.tolist()
    print(len(values_list[0]))

if __name__ == "__main__":
    main()