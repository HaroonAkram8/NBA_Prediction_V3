import json

from src.utils.encryption_keys import load_key


def get_from_private_data(private_data_path: str, section_key: str, value_key: str):
    with open(private_data_path, 'rb') as file:
        token = file.read()

    fernet = load_key()
    data_str = fernet.decrypt(token).decode()
    data_dict = json.loads(data_str)

    return data_dict[section_key][value_key]


def seasons_list(start_season_year: int, end_season_year: int):
    seasons = []
    for year in range(start_season_year, end_season_year+1):
        seasons.append(str(year) + "-" + str(int(str(year)[2:]) + 1))

    return seasons


def main():
    print(seasons_list(2012, 2022))


if __name__ == "__main__":
    main()
