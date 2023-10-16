import pandas as pd

from src.global_utils import get_from_private_data
from src.sql_db.sql_db_class import nba_psql
from src.globals import (
    LOCAL_SQL_DATABASE, LOCAL_SQL_USERNAME, LOCAL_SQL_PORT, LOCAL_SQL_HOST,
    PRIVATE_DATA, SQL_LOCAL_INFO, SQL_LOCAL_PASSWORD
)

class Baseline_Model:
    def __init__(self):
        self.gamelogs = None

        self.train_set = None
        self.val_set = None
        self.test_set = None
    
    def load(self, train_val_test_split: list = [0.7, 0.15]):
        self.gamelogs = self.__get_gamelogs__()

        data_df = pd.DataFrame(data=self.gamelogs['data'])
        data_df.columns = self.gamelogs['columns']

        data = data_df.values.tolist()

        val_start_index = int(len(data) * train_val_test_split[0])
        test_start_index = val_start_index + int(len(data) * train_val_test_split[1])

        self.train_set = data[:val_start_index]
        self.val_set = data[val_start_index:test_start_index]
        self.test_set = data[test_start_index:]
        
    def __get_gamelogs__(self):
        password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)

        psql_conn = nba_psql()
        psql_conn.connect(sql_user=LOCAL_SQL_USERNAME, sql_password=password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT, sql_database=LOCAL_SQL_DATABASE)

        _, gamelogs = psql_conn.select_paired_gamelogs()

        psql_conn.disconnect()

        return gamelogs
    
    def elo_winner(self):
        elo_rating_idx = self.gamelogs['columns'].index('elo_rating')
        opp_elo_rating_idx = self.gamelogs['columns'].index('opp_elo_rating')
        wl_idx = self.gamelogs['columns'].index('wl')

        results_dict = {
            'train_results': self.__calculate_num_correct__(self.train_set, elo_rating_idx, opp_elo_rating_idx, wl_idx),
            'val_results': self.__calculate_num_correct__(self.val_set, elo_rating_idx, opp_elo_rating_idx, wl_idx),
            'test_results': self.__calculate_num_correct__(self.test_set, elo_rating_idx, opp_elo_rating_idx, wl_idx)
        }

        return results_dict

    def __calculate_num_correct__(self, dataset, elo_rating_idx, opp_elo_rating_idx, wl_idx):
        num_won = 0
        num_total = len(dataset)

        for i in range(1, num_total):
            game = dataset[i]
            prev_game = dataset[i - 1]

            elo_rating = prev_game[elo_rating_idx]
            opp_elo_rating = prev_game[opp_elo_rating_idx]
            wl = game[wl_idx]

            if wl and elo_rating >= opp_elo_rating or not wl and elo_rating <= opp_elo_rating:
                num_won += 1
        
        return [num_won, num_total, float(num_won / num_total)]


def main():
    base_model = Baseline_Model()

    base_model.load()
    print(base_model.elo_winner())

if __name__ == "__main__":
    main()