from src.ml_prediction.load_dataset import load_dataset

class Baseline_Model:
    def __init__(self):
        self.train_set, self.val_set, self.test_set, self.gamelogs = None, None, None, None
    
    def load(self, train_val_test_split: list = [0.7, 0.15]):
        self.train_set, self.val_set, self.test_set, self.gamelogs = load_dataset(train_val_test_split=train_val_test_split, paired=True)
    
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