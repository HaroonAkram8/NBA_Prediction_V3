import pandas as pd

from src.globals import (
    LOCAL_SQL_DATABASE, LOCAL_SQL_USERNAME, LOCAL_SQL_PORT, LOCAL_SQL_HOST,
    PRIVATE_DATA, SQL_LOCAL_INFO, SQL_LOCAL_PASSWORD
)
from src.global_utils import get_from_private_data
from src.sql_db.sql_db_class import nba_psql

def load_dataset(columns_to_keep: list, train_val_test_split: list = [0.7, 0.15]):
    gamelogs = retrieve_sql_data()
    data = transform_data(columns_to_keep=columns_to_keep, gamelogs=gamelogs)

    val_start_index = int(len(data) * train_val_test_split[0])
    test_start_index = val_start_index + int(len(data) * train_val_test_split[1])

    train_set = data[:val_start_index]
    val_set = data[val_start_index:test_start_index]
    test_set = data[test_start_index:]

    return train_set, val_set, test_set

def retrieve_sql_data():
    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)

    psql_conn = nba_psql()
    psql_conn.connect(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT, sql_database=LOCAL_SQL_DATABASE)

    _, gamelogs = psql_conn.select_gamelogs()

    psql_conn.disconnect()

    return gamelogs

def transform_data(columns_to_keep: list, gamelogs: dict):
    data_df = pd.DataFrame(data=gamelogs['data'])
    data_df.columns = gamelogs['columns']
    data_df = data_df[columns_to_keep]

    data = data_df.values.tolist()
    return data

def main():
    train_set, val_set, test_set = load_dataset()
    print(len(train_set))
    print(len(val_set))
    print(len(test_set))

if __name__ == "__main__":
    main()