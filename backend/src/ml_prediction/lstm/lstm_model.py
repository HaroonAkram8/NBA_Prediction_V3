import torch
import torch.nn as nn

class LSTM_Model(nn.Module):
    def __init__(self, input_size: int=100, hidden_size: int=200, num_layers: int=1, num_classes: int=1):
        super(LSTM_Model, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        for name, param in self.lstm.named_parameters():
            if 'weight' in name:
                nn.init.kaiming_normal_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)

        self.fc = nn.Linear(hidden_size, num_classes)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device=x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device=x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = self.sigmoid(self.fc(out[:, -1, :]))

        return out