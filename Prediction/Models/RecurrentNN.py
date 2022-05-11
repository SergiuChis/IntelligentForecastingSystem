import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image


class RecurrentNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, device="cuda"):
        super(RecurrentNN, self).__init__()
        self.device = device
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.rnn = nn.RNN(input_size, hidden_size, num_layers)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(1, self.hidden_size).to(self.device)
        out, _ = self.rnn(x, h0)
        out = out[-1, :]
        out = self.fc(out)
        return out

    def initial_hidden(self):
        return torch.zeros(self.hidden_size).to(self.device)
