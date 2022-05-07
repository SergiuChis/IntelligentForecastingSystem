import torch
import torch.nn as nn
import torch.nn.functional as F


class RecurrentNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, device="cuda"):
        super(RecurrentNN, self).__init__()
        self.device = device
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        # super(RecurrentNN, self).__init__()
        # self.device = device
        # self.hidden_size = hidden_size
        # TODO convolutie
        # TODO testeaza si alte optimizers
        # TODO mecanism de early stopping
        # TODO prezic una din cele 4 valori
        # TODO mai multe imagini in secventa
        # TODO impartim sunny vallue in 4 clustere
        # pt paper: toate familiile de algoritmi de clustere
        # toate familiile de modele ai
        # self.input2hidden = nn.Linear(input_size + hidden_size, hidden_size, device=self.device)
        # self.input2output = nn.Linear(input_size + hidden_size, output_size, device=self.device)
        # self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device)
        out, _ = self.rnn(x, h0)
        out = out[:, -1, :]
        out = self.fc(out)
        return out
        # combined = torch.cat((input_tensor, hidden_tensor))
        #
        # hidden = self.input2hidden(combined)
        # output = self.input2output(combined)
        # output = self.softmax(output)

    def initial_hidden(self):
        return torch.zeros(self.hidden_size).to(self.device)
