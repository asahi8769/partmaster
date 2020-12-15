from experiment.RNN import RNNModel
from experiment.CNN import CNNModel
from experiment.trainer import ModelTrainer
from experiment.dataset import Dataset
# from confusion_matrix import *
import os, pickle
import torch

os.chdir(os.pardir)

data = Dataset(file_path='files/불량유형수기정리.xlsx')
train_iter, test_iter = data.get_iter(batch_sizes=(32, 256))

# model = RNNModel(n_vocab=3000, n_input=20, n_hidden=15, n_rnnlayers=1, n_outputs=512)
model = CNNModel(n_vocab=3000, n_embedding=128, n_outputs=512, seed=0)
# model.load_checkpoint()

trainer = ModelTrainer(model, train_iter, test_iter, lr=0.00001, epochs=1000)
trainer.batch_learn()
trainer.plot_result()


sentence1 = 'WRONG SPEC PROBLEM POWER TRAIN & CHASSIS-ETC AUTOMATIC T/M OVER DRIVER 노브&부트'
sentence2 = 'MALFUNCTION PROBLEM POWER TRAIN & CHASSIS-ETC AUTOMATIC T/M OVER DRIVER 노브&부트'
sentence3 = 'SCRATCH DAMAGE DUST PAINT POWER TRAIN & CHASSIS-ETC REAR AXLE 커버_휠'

with open('files/spawn/tar_decoder.pkl', 'rb') as file:
    tar_dict = pickle.load(file)

with open('files/spawn/encoder.pkl', 'rb') as file:
    encoder = pickle.load(file)
    # print(encoder)

with torch.no_grad():
    model.load_checkpoint()
    model.eval()
    for sentence in (sentence1, sentence2, sentence3):
        toks = sentence.split(' ')
        sent_idx = torch.LongTensor([[1]*(20-len(toks))+[encoder.get(i, 0) for i in toks]])
        result = model(sent_idx.to(model.device))
        print(len(result[0]))
        print(tar_dict[int(torch.argmax(result, dim=1))]) # 이번엔 타깃이 전혀 안맞음 -> 타깃도 같은 딕셔너리 공유하도록 수정해볼것




""" https://discuss.pytorch.org/t/loading-model-test-accuracy-drops/22833/4 """
""" https://towardsdatascience.com/how-to-save-and-load-a-model-in-pytorch-with-a-complete-example-c2920e617dee """
""" https://stackoverflow.com/questions/42703500/best-way-to-save-a-trained-model-in-pytorch """ ## must see this