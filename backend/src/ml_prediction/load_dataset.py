import pandas as pd

from src.globals import (
    LOCAL_SQL_DATABASE, LOCAL_SQL_USERNAME, LOCAL_SQL_PORT, LOCAL_SQL_HOST,
    PRIVATE_DATA, SQL_LOCAL_INFO, SQL_LOCAL_PASSWORD
)
from src.global_utils import get_from_private_data
from src.sql_db.sql_db_class import nba_psql


def load_clustered_dataset(train_val_test_split: list = [0.7, 0.15], paired: bool=False, columns_to_remove: list=[], num_rows_per_cluster: int=10):
    train_set, val_set, test_set, gamelogs, wl_idx = load_dataset(train_val_test_split=train_val_test_split, paired=paired, columns_to_remove=columns_to_remove)

    clustered_train_set = generate_clusters(dataset=train_set, num_rows_per_cluster=num_rows_per_cluster, wl_idx=wl_idx)
    clustered_val_set = generate_clusters(dataset=val_set, num_rows_per_cluster=num_rows_per_cluster, wl_idx=wl_idx)
    clustered_test_set = generate_clusters(dataset=test_set, num_rows_per_cluster=num_rows_per_cluster, wl_idx=wl_idx)

    return clustered_train_set, clustered_val_set, clustered_test_set, gamelogs


def load_dataset(train_val_test_split: list = [0.7, 0.15], paired: bool=False, columns_to_remove: list=[]):
    gamelogs = get_gamelogs(paired=paired)

    data_df = pd.DataFrame(data=gamelogs['data'])
    data_df.columns = gamelogs['columns']

    data, wl_idx = transform_data(columns_to_remove=columns_to_remove, gamelogs=gamelogs)

    val_start_index = int(len(data) * train_val_test_split[0])
    test_start_index = val_start_index + int(len(data) * train_val_test_split[1])

    train_set = data[:val_start_index]
    val_set = data[val_start_index:test_start_index]
    test_set = data[test_start_index:]

    return train_set, val_set, test_set, gamelogs, wl_idx


def generate_clusters(dataset: list=[], num_rows_per_cluster: int = 10, wl_idx: int = -1):
    clustered_dataset = []
    num_clusters = len(dataset) - num_rows_per_cluster - 1

    results_list = [item[wl_idx] for item in dataset]

    for i in range(num_clusters):
        cluster = dataset[i:i+num_rows_per_cluster]
        result = results_list[i + num_rows_per_cluster + 1]
        clustered_dataset.append((cluster, result))

    return clustered_dataset


def get_gamelogs(paired: bool = False):
    password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)

    psql_conn = nba_psql()
    psql_conn.connect(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT, sql_database=LOCAL_SQL_DATABASE)

    if paired:
        _, gamelogs = psql_conn.select_paired_gamelogs(home_away_only=False)
    else:
        _, gamelogs = psql_conn.select_gamelogs()

    psql_conn.disconnect()

    return gamelogs


def transform_data(columns_to_remove: list, gamelogs: dict):
    data_df = pd.DataFrame(data=gamelogs['data'])
    data_df.columns = gamelogs['columns']

    data_df = data_df.drop(columns=columns_to_remove)
    wl_idx = data_df.columns.get_loc('wl')

    data_df = data_df.astype(float)
    data_df = (data_df - data_df.min()) / (data_df.max() - data_df.min())

    data = data_df.values.tolist()
    return data, wl_idx


def main():
    train_set, val_set, test_set = load_dataset()
    print(len(train_set))
    print(len(val_set))
    print(len(test_set))


if __name__ == "__main__":
    main()
