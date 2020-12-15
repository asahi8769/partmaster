import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
import pickle, os
from datetime import datetime
import torch.nn.functional as F


class ModelTrainer:
    def __init__(self, model, train_iter, test_iter, lr=0.01, epochs=200):
        self.lr = lr
        self.model = model
        self.epochs = epochs
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(model.parameters(),lr=self.lr)
        self.train_iter, self.test_iter = train_iter, test_iter
        self.train_losses = np.zeros(self.epochs)
        self.test_losses = np.zeros(self.epochs)
        self.train_accs = np.zeros(self.epochs)
        self.test_accs = np.zeros(self.epochs)
        self.best_param_pkl = os.path.join(os.getcwd(), 'files', 'models', model.__class__.__name__ + '_loss.pkl')
        self.minloss_bestacc = None

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.update_minloss()

    def batch_learn(self):
        # for epoch in range(self.epochs):
        for epoch in range(self.epochs):
            self.model.train()
            t0 = datetime.now()
            train_loss = []
            p_train = []
            y_train = []
            for inputs, targets in self.train_iter:
                targets = targets.view(-1, 1).squeeze(1).long()
                self.optimizer.zero_grad()
                y_pred = self.model(inputs)
                y_pred = y_pred.float()
                p_train += list(torch.argmax(y_pred, dim=1).to(self.device).detach().numpy())
                y_train += list(targets.to(self.device).detach().numpy())
                loss = self.criterion(y_pred, targets)
                loss.backward()
                self.optimizer.step()
                train_loss.append(loss.item())
            p_train = np.array(p_train)
            y_train = np.array(y_train)
            self.train_losses[epoch] = np.mean(train_loss)
            self.train_accs[epoch] = np.mean(y_train == p_train)
            p_test, y_test = self.batch_test(epoch)
            self.batch_test(epoch)
            dt = datetime.now() - t0
            print(f'Epoch : {epoch + 1}/{self.epochs}, Train Loss : {self.train_losses[epoch]:.4f}, '
                  f'Train Acc : {self.train_accs[epoch]:.4f}, Test Loss : {self.test_losses[epoch]:.4f}, '
                  f'Test Acc : {self.test_accs[epoch]:.4f}, Duration : {dt}')
            if self.minloss_bestacc is None or self.minloss_bestacc[1] < self.test_accs[epoch]:
                self.save_minloss([self.test_losses[epoch], self.test_accs[epoch]])
        # return p_train, y_train, p_test, y_test

    @torch.no_grad()
    def batch_test(self, epoch):
        self.model.eval()
        test_loss = []
        p_test = []
        y_test = []
        for inputs, targets in self.test_iter:
            targets = targets.view(-1, 1).squeeze(1).long()
            y_pred = self.model(inputs)
            p_test += list(torch.argmax(y_pred, dim=1).to(self.device).detach().numpy())
            y_test += list(targets.to(self.device).numpy())
            loss = self.criterion(y_pred, targets)
            test_loss.append(loss.item())
        p_test = np.array(p_test)
        y_test = np.array(y_test)
        self.test_losses[epoch] = np.mean(test_loss)
        self.test_accs[epoch] = np.mean(y_test == p_test)
        return p_test, y_test

    def plot_result(self):
        plt.plot(self.train_losses, label='training loss')
        plt.plot(self.test_losses, label='test loss')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def save_minloss(self, best_result: list):
        with open(self.best_param_pkl, 'wb') as file:
            pickle.dump(best_result, file)
        self.update_minloss()
        self.model.save_checkpoint()

    def update_minloss(self):
        try:
            with open(self.best_param_pkl, 'rb') as file:
                self.minloss_bestacc = pickle.load(file)

        except FileNotFoundError as e:
            self.minloss_bestacc = None
        else:
            print(f'... loading minimal loss {self.minloss_bestacc} ...')