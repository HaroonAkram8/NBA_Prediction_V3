import configparser

def get_from_private_data(private_data_path: str, section_key: str, value_key: str):
    config = configparser.ConfigParser()
    config.read(private_data_path)

    return config[section_key][value_key]