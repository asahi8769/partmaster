import torch
import torch.nn as nn
import torch.nn.functional as F
import os


class CNNModel(nn.Module):
    def __init__(self, n_vocab, n_embedding, n_outputs, seed=0):
        super(CNNModel, self).__init__()
        if seed is not None:
            torch.random.manual_seed(0)
        self.V_vocab = n_vocab
        self.D_input = n_embedding
        self.K_outputs = n_outputs
        self.embed = nn.Embedding(self.V_vocab, self.D_input)
        self.conv1 = nn.Conv1d(self.D_input, 32, 3, padding=1)
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(32, 64, 3, padding=1)
        self.pool2 = nn.MaxPool1d(2)
        self.conv3 = nn.Conv1d(64, 128, 3, padding=1)
        self.fc = nn.Linear(128, self.K_outputs)
        self.checkpoint = os.path.join(os.getcwd(),'files', 'models', self.__class__.__name__ + '_params.pt')
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, X):  # N T
        out = self.embed(X)  # N T D
        out = out.permute(0, 2, 1)  # N D T
        out = self.conv1(out)  # N M T
        out = F.relu(out)  # N M T
        out = self.pool1(out)  # N M T2
        out = self.conv2(out)  # N M2 T2
        out = self.pool2(out)  # N M2 T3
        out = self.conv3(out)  # N M3 T3
        out = out.permute(0, 2, 1)  # N T3 M3
        out, _ = torch.max(out, 1)  # N M3
        out = self.fc(out)
        return out  # N K

    def save_checkpoint(self):
        print('... saving params ...')
        torch.save(self.state_dict(), self.checkpoint)

    def load_checkpoint(self):
        print('... loading params ...')
        try:
            self.load_state_dict(torch.load(self.checkpoint))
        except FileNotFoundError as e:
            print(f'... No checkpoint found ...{e}')