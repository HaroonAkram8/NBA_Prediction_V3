import configparser

def get_from_private_data(private_data_path: str, section_key: str, value_key: str):
    config = configparser.ConfigParser()
    config.read(private_data_path)

    return config[section_key][value_key]

def seasons_list(start_season_year: int, end_season_year: int):
    seasons = []
    for year in range(start_season_year, end_season_year+1):
        seasons.append(str(year) + "-" + str(int(str(year)[2:]) + 1))
    
    return seasons

def main():
    print(seasons_list(2012, 2022))

if __name__ == "__main__":
    main()