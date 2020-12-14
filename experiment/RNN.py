import torch
import torch.nn as nn
import os


class RNNModel(nn.Module):
    def __init__(self, n_vocab, n_input, n_hidden, n_rnnlayers, n_outputs):
        super(RNNModel, self).__init__()
        self.V_vocab = n_vocab
        self.D_input = n_input
        self.M_hidden = n_hidden
        self.L_rnnlayers = n_rnnlayers
        self.K_outputs = n_outputs
        self.embed = nn.Embedding(self.V_vocab, self.D_input)
        self.rnn = nn.LSTM(input_size=self.D_input, hidden_size=self.M_hidden, num_layers=self.L_rnnlayers,
                           batch_first=True)
        self.fc = nn.Linear(self.M_hidden, self.K_outputs)
        self.checkpoint = os.path.join(os.getcwd(), 'models', self.__class__.__name__ + '_params.pt')
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, X):
        h0 = torch.zeros(self.L_rnnlayers, X.size(0), self.M_hidden).to(self.device)
        c0 = torch.zeros(self.L_rnnlayers, X.size(0), self.M_hidden).to(self.device)
        out = self.embed(X)  # in : N*T, out: N*T*D
        out, _ = self.rnn(out, (h0, c0))  # in : N*T*D, out: N*T*M
        out, _ = torch.max(out, 1)  # in : N*T*M, out: N*M
        return self.fc(out)  # in : N*M, out: N*K

    def save_checkpoint(self):
        print('... saving params ...')
        torch.save(self.state_dict(), self.checkpoint)

    def load_checkpoint(self):
        print('... loading params ...')
        try:
            self.load_state_dict(torch.load(self.checkpoint))
        except FileNotFoundError as e:
            print(f'... No checkpoint found ...{e}')