# General constants
SEASON_START_YEAR = '2022'
SEASON = SEASON_START_YEAR + "-" + str(int(SEASON_START_YEAR[2:]) + 1)
SEASON_TYPE = "Regular Season"
MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
SCHEDULE_URL = f'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{SEASON_START_YEAR}/league/00_full_schedule.json'

# Game Columns
GAME_COLUMNS = ["SEASON_YEAR", "GAME_ID", "GAME_DATE", "H_TEAM_ID", "H_TEAM_NAME", "A_TEAM_ID", "A_TEAM_NAME", "H_PTS", "A_PTS", "MIN"]
GAME_STATS_COLUMNS = ["FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB","REB","AST","TOV","STL","BLK","BLKA","PF","PFD","PLUS_MINUS","GP_RANK","W_RANK","L_RANK","W_PCT_RANK","MIN_RANK","FGM_RANK","FGA_RANK","FG_PCT_RANK","FG3M_RANK","FG3A_RANK","FG3_PCT_RANK","FTM_RANK","FTA_RANK","FT_PCT_RANK","OREB_RANK","DREB_RANK","REB_RANK","AST_RANK","TOV_RANK","STL_RANK","BLK_RANK","BLKA_RANK","PF_RANK","PFD_RANK","PTS_RANK","PLUS_MINUS_RANK"]

# ELO stats constants
START_ELO_RATING = 1500.0

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