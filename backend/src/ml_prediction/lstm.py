import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.ml_prediction.load_dataset import load_dataset
from src.globals import SQL_KEEP_COLUMNS


class LSTM_Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(LSTM_Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device=x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device=x.device)

        out, _ = self.lstm(x, (h0, c0))

        out = self.fc(out[:, -1, :])

        return out


class LSTM_Dataloader:
    def __init__(self, batch_size: int = 64, shuffle: bool = True):
        self.batch_size = batch_size
        self.shuffle = shuffle

        self.train_dataloader = None
        self.val_dataloader = None
        self.test_dataloader = None

    def load(self, train_val_test_split: list = [0.7, 0.15], sequence_len: int = 10):
        train_set, val_set, test_set = load_dataset(columns_to_keep=SQL_KEEP_COLUMNS, train_val_test_split=train_val_test_split)

        train_tensor_set = self.__generate_sequenced_dataset__(dataset=train_set, sequence_len=sequence_len)
        val_tensor_set = self.__generate_sequenced_dataset__(dataset=val_set, sequence_len=sequence_len)
        test_tensor_set = self.__generate_sequenced_dataset__(dataset=test_set, sequence_len=sequence_len)

        self.train_dataloader = DataLoader(train_tensor_set, batch_size=self.batch_size, shuffle=self.shuffle)
        self.val_dataloader = DataLoader(val_tensor_set, batch_size=self.batch_size, shuffle=self.shuffle)
        self.test_dataloader = DataLoader(test_tensor_set, batch_size=self.batch_size, shuffle=self.shuffle)

    def __generate_sequenced_dataset__(self, dataset: list, sequence_len: int):
        sequenced_set, labels = self.__generate_sequences__(dataset=dataset, sequence_len=sequence_len)

        data_tensor = torch.tensor(sequenced_set)
        labels_tensor = torch.tensor(labels)

        dataset_tensor = TensorDataset(data_tensor, labels_tensor)

        return dataset_tensor

    def __generate_sequences__(self, dataset: list, sequence_len: int):
        dataset_len = len(dataset)
        labels = []
        sequenced_set = []

        for i in range(dataset_len):
            if i + sequence_len + 1 > dataset_len:
                break

            sequence = dataset[i: i + sequence_len]
            sequenced_set.append(sequence)

            next_game_outcome = dataset[i + sequence_len][0]  # Win/loss of next game
            labels.append(next_game_outcome)

        return sequenced_set, labels


def main():
    loader = LSTM_Dataloader()
    loader.load()


if __name__ == "__main__":
    main()
