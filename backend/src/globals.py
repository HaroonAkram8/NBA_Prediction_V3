# SQL Info
LOCAL_SQL_DATABASE = 'nba_db'
LOCAL_SQL_USERNAME = 'postgres'
LOCAL_SQL_PORT = 5432
LOCAL_SQL_HOST = 'localhost'
SCHEMA_PATH = './backend/src/sql_db/sql_schema_and_queries/schema.ddl'
TEAM_INFO_PATH = './backend/src/sql_db/sql_schema_and_queries/populate_team_info.ddl'

# Private Data Paths
KEY_PATH = 'backend_key.key'
PRIVATE_DATA = 'private_data.txt'
SQL_LOCAL_INFO = 'SQL_LOCAL_INFO'
SQL_LOCAL_PASSWORD = 'password'

# WL
WIN = True
LOSS = False

# General constants
EARLIEST_START_YEAR = '2012'
EARLIEST_SEASON = '2012-13'
SEASON_START_YEAR = '2022'
SEASON = SEASON_START_YEAR + "-" + str(int(SEASON_START_YEAR[2:]) + 1)
SEASON_TYPE = "Regular Season"
MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
SCHEDULE_URL = f'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{SEASON_START_YEAR}/league/00_full_schedule.json'

# Game Columns
GAMELOG_COLUMNS = ['GAME_ID', 'SEASON_YEAR', 'GAME_DATE', 'TEAM_ID', 'WL', 'PTS', 'MIN', 'FGM','FGA','FG_PCT','FG3M','FG3A','FG3_PCT','FTM','FTA','FT_PCT','OREB','DREB','REB','AST','TOV','STL','BLK','BLKA','PF','PFD','PLUS_MINUS']
GAMELOG_TABLE_COLUMNS = ['ELO_RATING', 'AT_HOME'] + GAMELOG_COLUMNS
SQL_GAMELOG_COLUMNS = ['game_id', 'season_year', 'game_date', 'team_id', 'elo_rating', 'wl', 'at_home', 'pts', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'tov', 'stl', 'blk', 'blka', 'pf', 'pfd', 'plus_minus']
SQL_KEEP_COLUMNS = ['wl', 'at_home', 'pts', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'tov', 'stl', 'blk', 'blka', 'pf', 'pfd', 'plus_minus']

# ELO stats constants
START_ELO_RATING = 1300.0
H_ELO_BOOST = 100.0

# Connecting to NBA API
HEADERS = {'Accept': 'application/json, text/plain, */*',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9',
          'Connection': 'keep-alive',
          'Host': 'stats.nba.com',
          'Origin': 'https://www.nba.com',
          'Referer': 'https://www.nba.com/',
          'sec-ch-ua': '"Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87"',
          'sec-ch-ua-mobile': '?1',
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Site': 'same-site',
          'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
          'x-nba-stats-origin': 'stats',
          'x-nba-stats-token': 'true'}