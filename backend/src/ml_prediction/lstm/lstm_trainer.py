import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from src.ml_prediction.lstm.lstm_model import LSTM_Model
from src.ml_prediction.lstm.lstm_loader import LSTM_Dataloader
from src.globals import MODEL_SAVE_PATH

class Model_Trainer:
    def __init__(self, model: LSTM_Model, data_loader: LSTM_Dataloader, criterion=nn.BCEWithLogitsLoss(), learning_rate: float=0.001):
        self.model = model

        self.train_loader, self.val_loader, self.test_loader = data_loader.get_loaders()

        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = criterion
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.wandb_run = None

    def train(self, num_epochs: int=100, save_every_n: int=10):
        train_accuracy = []
        train_loss = []
        val_accuracy = []
        val_loss = []

        for epoch in range(num_epochs):
            total_train_loss = 0.0
            total_train_acc = 0.0
            total_epoch = 0

            for i, (inputs, labels) in enumerate(self.train_loader):
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)

                self.model.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels.unsqueeze(1))
                loss.backward()
                self.optimizer.step()

                total_train_acc += float(torch.sum(torch.eq(torch.round(outputs), labels.unsqueeze(1))))
                total_train_loss += loss.item()
                total_epoch += len(labels)
            
            train_accuracy.append(float(total_train_acc) / total_epoch)
            train_loss.append(float(total_train_loss) / (i+1))
            
            val_acc, val_ls = self.__evaluate__(self.val_loader)
            val_accuracy.append(val_acc)
            val_loss.append(val_ls)

            print(("Epoch {}: Train accuracy: {} Train loss: {} | " + "Validation accuracy: {} Validation loss: {}").format(epoch,
                                                                                                                            train_accuracy[epoch],
                                                                                                                            train_loss[epoch],
                                                                                                                            val_accuracy[epoch],
                                                                                                                            val_loss[epoch]))

            if epoch + 1 % save_every_n == 0 and epoch + 1 != num_epochs:
                model_name = 'lstm_model_epoch_' + str(epoch) + '.pt'
                torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)
                
        model_name = 'lstm_model_epoch_' + str(num_epochs-1) + '.pt'
        torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)
    
    def __evaluate__(self, loader):
        total_loss = 0.0
        total_err = 0.0
        total_epoch = 0
        i = 0

        for _, (inputs, labels) in enumerate(loader):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            outputs = self.model(inputs)
            loss = self.criterion(outputs, labels.unsqueeze(1))

            total_err += float(torch.sum(torch.eq(torch.round(outputs), labels.unsqueeze(1))))
            total_loss += loss.item()
            total_epoch += len(labels)

            i += 1

        err = float(total_err) / total_epoch
        loss = float(total_loss) / (i + 1)
        return err, loss

def main():
    from src.globals import COLUMNS_TO_REMOVE

    loader = LSTM_Dataloader()
    loader.load(columns_to_remove=COLUMNS_TO_REMOVE)

    model = LSTM_Model(input_size=46)

    model_trainer = Model_Trainer(model=model, data_loader=loader)
    model_trainer.train(num_epochs=3)

if __name__ == "__main__":
    main()