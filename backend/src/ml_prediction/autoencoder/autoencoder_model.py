import torch
import torch.nn as nn
import torch.nn.functional as F


class Autoencoder_Model(nn.Module):
    def __init__(self, latent_dims, num_games: int=10, num_cols: int=47):
        super(Autoencoder_Model, self).__init__()

        self.dim_1 = num_games * num_cols
        self.dim_2 = int(self.dim_1 / 2)

        self.encoder = Encoder(latent_dims, self.dim_1, self.dim_2)
        self.decoder = Decoder(latent_dims, self.dim_1, self.dim_2, num_games, num_cols)

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)


class Encoder(nn.Module):
    def __init__(self, latent_dims, dim_1, dim_2):
        super(Encoder, self).__init__()
        self.linear1 = nn.Linear(dim_1, dim_2)
        self.linear2 = nn.Linear(dim_2, latent_dims)

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.linear1(x))

        return self.linear2(x)


class Decoder(nn.Module):
    def __init__(self, latent_dims, dim_1, dim_2, num_games, num_cols):
        super(Decoder, self).__init__()

        self.num_games = num_games
        self.num_cols = num_cols

        self.linear1 = nn.Linear(latent_dims, dim_2)
        self.linear2 = nn.Linear(dim_2, dim_1)

    def forward(self, z):
        z = F.relu(self.linear1(z))
        z = torch.sigmoid(self.linear2(z))

        return z.reshape((-1, self.num_games, self.num_cols))
