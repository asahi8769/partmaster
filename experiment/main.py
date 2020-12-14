from experiment.RNN import RNNModel
from experiment.CNN import CNNModel
from experiment.trainer import ModelTrainer
from experiment.dataset import Dataset
# from confusion_matrix import *
import os

os.chdir(os.pardir)

data = Dataset(file_path='files/불량유형수기정리.xlsx')
train_iter, test_iter = data.get_iter(batch_sizes=(32, 256))

# model = RNNModel(n_vocab=3000, n_input=20, n_hidden=15, n_rnnlayers=1, n_outputs=512)
model = CNNModel(n_vocab=3000, n_embedding=128, n_outputs=512)
model.load_checkpoint()
trainer = ModelTrainer(model, train_iter, test_iter, lr=0.00001, epochs=1000)
trainer.batch_learn()
trainer.plot_result()
