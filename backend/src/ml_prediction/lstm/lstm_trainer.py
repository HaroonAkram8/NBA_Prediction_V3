import torch
import torch.nn as nn
import torch.optim as optim

from src.ml_prediction.lstm.lstm_model import LSTM_Model
from src.ml_prediction.lstm.lstm_loader import LSTM_Dataloader
from src.globals import MODEL_SAVE_PATH

class LSTM_Model_Trainer:
    def __init__(self, model: LSTM_Model, data_loader: LSTM_Dataloader, criterion=nn.MSELoss(), learning_rate: float=0.0001, weight_decay: float=0.00001):
        self.model = model

        self.train_loader, self.val_loader, self.test_loader = data_loader.get_loaders()

        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        self.criterion = criterion
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    def train(self, num_epochs: int=100, save_every_n: int=10):
        train_acc_list = []
        train_loss_list = []
        val_acc_list = []
        val_loss_list = []

        for epoch in range(num_epochs):
            train_loss, train_acc = self.__train_epoch__()
            val_loss, val_acc = self.__evaluate__()

            train_loss_list.append(train_loss)
            train_acc_list.append(train_acc)
            val_loss_list.append(val_loss)
            val_acc_list.append(val_acc)
            
            print('Epoch ' + str(epoch) +f' | Train Acc: {train_acc} Train Loss: {train_loss} | Validation Acc: {val_acc} Validation Loss: {val_loss}')

            if (epoch + 1) % save_every_n == 0 and epoch + 1 != num_epochs:
                model_name = 'lstm_model_epoch_' + str(epoch) + '.pt'
                torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)
        
        model_name = 'lstm_model_epoch_' + str(num_epochs-1) + '.pt'
        torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)
        
        return train_acc_list, train_loss_list, val_acc_list, val_loss_list
    
    def __train_epoch__(self):
        epoch_loss = 0.0
        epoch_acc = 0.0
        
        self.model.train()
        
        for _, (inputs, labels) in enumerate(self.train_loader):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()
            predictions = self.model(inputs).squeeze()
            loss = self.criterion(predictions, labels)
            loss.backward()
            self.optimizer.step()
            
            acc = self.__binary_accuracy__(predictions, labels)
            
            epoch_loss += loss.item()
            epoch_acc += acc.item()

        return epoch_loss / len(self.train_loader), epoch_acc / len(self.train_loader)
    
    def __evaluate__(self):
        epoch_loss = 0.0
        epoch_acc = 0.0

        self.model.eval()

        with torch.no_grad():
            for _, (inputs, labels) in enumerate(self.val_loader):
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                
                predictions = self.model(inputs).squeeze()

                loss = self.criterion(predictions, labels)
                acc = self.__binary_accuracy__(predictions, labels)

                epoch_loss += loss.item()
                epoch_acc += acc.item()
        
        return epoch_loss / len(self.val_loader), epoch_acc / len(self.val_loader)

    def __binary_accuracy__(self, preds, y):
        rounded_preds = torch.round(preds)
        
        correct = (rounded_preds == y).float()
        acc = correct.sum() / len(correct)

        return acc

def main():
    from src.globals import COLUMNS_TO_REMOVE

    loader = LSTM_Dataloader()
    num_cols = loader.load(columns_to_remove=COLUMNS_TO_REMOVE, num_rows_per_cluster=10)

    model = LSTM_Model(input_size=num_cols, hidden_size=10, num_layers=1)

    model_trainer = LSTM_Model_Trainer(model=model, data_loader=loader, learning_rate=0.0001)
    _, _, _, _ = model_trainer.train(num_epochs=1000, save_every_n=1500)

if __name__ == "__main__":
    main()