import torch
from torch.utils.data import TensorDataset, DataLoader

from src.ml_prediction.load_dataset import load_clustered_dataset

class Autoencoder_Dataloader:
    def __init__(self, batch_size: int = 32, shuffle: bool = True):
        self.batch_size = batch_size
        self.shuffle = shuffle

        self.train_dataloader, self.val_dataloader, self.test_dataloader, self.gamelogs = None, None, None, None
    
    def load(self, train_val_test_split: list = [0.7, 0.15], paired: bool=True, num_rows_per_cluster: int=10, columns_to_remove: list=[]):
        train_set, val_set, test_set, self.gamelogs = load_clustered_dataset(train_val_test_split=train_val_test_split,
                                                                             paired=paired,
                                                                             columns_to_remove=columns_to_remove,
                                                                             num_rows_per_cluster=num_rows_per_cluster)

        self.train_dataloader = self.__dataset_to_dataloader__(train_set)
        self.val_dataloader = self.__dataset_to_dataloader__(val_set)
        self.test_dataloader = self.__dataset_to_dataloader__(test_set)

        num_cols = len(self.gamelogs['columns']) - len(columns_to_remove)

        return num_cols
    
    def get_loaders(self):
        return self.test_dataloader, self.val_dataloader, self.test_dataloader
    
    def __dataset_to_dataloader__(self, dataset: list=[]):
        data = [item[0] for item in dataset]
        labels = [float(item[1]) for item in dataset]

        data_tensor = torch.tensor(data)
        labels_tensor = torch.tensor(labels)

        dataset_tensor = TensorDataset(data_tensor, labels_tensor)
        dataloader = DataLoader(dataset_tensor, batch_size=self.batch_size, shuffle=self.shuffle)

        return dataloader