import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from src.ml_prediction.autoencoder.autoencoder_model import Autoencoder_Model
from src.ml_prediction.autoencoder.autoencoder_loader import Autoencoder_Dataloader
from src.globals import MODEL_SAVE_PATH


class Autoencoder_Model_Trainer:
    def __init__(self, model: Autoencoder_Model, data_loader: Autoencoder_Dataloader, criterion=nn.MSELoss(), learning_rate: float=0.0001, weight_decay: float=0.00001):
        self.model = model

        self.train_loader, self.val_loader, self.test_loader = data_loader.get_loaders()

        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        self.criterion = criterion
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def train(self, num_epochs: int=100, save_every_n: int=10):
        train_loss_list = []
        val_loss_list = []

        for epoch in range(num_epochs):
            train_loss = self.__train_epoch__()
            val_loss = self.__evaluate__()

            train_loss_list.append(train_loss)
            val_loss_list.append(val_loss)

            print('Epoch ' + str(epoch) +f' | Train Loss: {train_loss} | Validation Loss: {val_loss}')

            if (epoch + 1) % save_every_n == 0 and epoch + 1 != num_epochs:
                model_name = 'autoencoder_model_epoch_' + str(epoch) + '.pt'
                torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)

        model_name = 'autoencoder_model_epoch_' + str(num_epochs-1) + '.pt'
        torch.save(self.model.state_dict(), MODEL_SAVE_PATH + model_name)

        return train_loss_list, val_loss_list

    def plot_latent(self, loader, num_batches: int=100):
        for i, (x, y) in enumerate(loader):
            z = self.model.encoder(x.to(self.device))
            z = z.to('cpu').detach().numpy()
            plt.scatter(z[:, 0], z[:, 1], c=y, cmap='tab10')
            if i > num_batches:
                plt.colorbar()
                break

        plt.show()

    def __train_epoch__(self):
        epoch_loss = 0.0

        self.model.train()

        for _, (inputs, _) in enumerate(self.train_loader):
            inputs = inputs.to(self.device)

            self.optimizer.zero_grad()
            inputs_hat = self.model(inputs)
            loss = self.criterion(inputs_hat, inputs)
            loss.backward()
            self.optimizer.step()

            epoch_loss += loss.item()

        return epoch_loss / len(self.train_loader)

    def __evaluate__(self):
        epoch_loss = 0.0

        self.model.eval()

        with torch.no_grad():
            for _, (inputs, _) in enumerate(self.val_loader):
                inputs = inputs.to(self.device)

                inputs_hat = self.model(inputs).squeeze()
                loss = self.criterion(inputs_hat, inputs)

                epoch_loss += loss.item()

        return epoch_loss / len(self.val_loader)


def main():
    from src.globals import COLUMNS_TO_REMOVE

    loader = Autoencoder_Dataloader()
    num_cols = loader.load(columns_to_remove=COLUMNS_TO_REMOVE, num_rows_per_cluster=10)

    model = Autoencoder_Model(latent_dims=2, num_games=10, num_cols=num_cols)

    model_trainer = Autoencoder_Model_Trainer(model=model, data_loader=loader, learning_rate=0.0001)
    _, _ = model_trainer.train(num_epochs=100, save_every_n=150)

    train_loader, val_loader, _ = loader.get_loaders()
    model_trainer.plot_latent(train_loader)
    model_trainer.plot_latent(val_loader)


if __name__ == "__main__":
    main()
