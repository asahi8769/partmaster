from problem_search.CNN import CNNModel
from problem_search.trainer import ModelTrainer
from problem_search.dataset import Dataset
import os, pickle
import torch
from problem_search.config import *

os.chdir(os.pardir)

model = CNNModel(n_vocab=n_vocab, n_embedding=n_embedding, n_outputs=n_outputs, seed=0)
model.load_checkpoint()

data = Dataset(file_path=file_path, update_csv=False)
train_iter, test_iter = data.get_iter(batch_sizes=(32, 256))
trainer = ModelTrainer(model, train_iter, test_iter, lr=lr, epochs=epochs)
trainer.batch_learn()
trainer.plot_result()


sentence1 = 'WRONG SPEC PROBLEM POWER TRAIN & CHASSIS-ETC AUTOMATIC T/M OVER DRIVER 노브&부트'  # 이종
sentence2 = 'MALFUNCTION PROBLEM POWER TRAIN & CHASSIS-ETC AUTOUI-CL-011MATIC T/M OVER DRIVER 노브&부트'  # 작동불량
sentence3 = 'SCRATCHES SEALANT TORQUE PROBLEM MISS EXCESS PAINT LEAK ENGINE CYLINDER BLOCK 팬_오일'  # 스크래치

with open('files/spawn/tar_decoder.pkl', 'rb') as file:
    tar_dict = pickle.load(file)
    print(tar_dict)

with open('files/spawn/encoder.pkl', 'rb') as file:
    encoder = pickle.load(file)

with torch.no_grad():
    model.load_checkpoint()
    model.eval()
    for sentence in (sentence1, sentence2, sentence3):
        toks = sentence.split(' ')
        sent_idx = torch.LongTensor([[1]*(fix_length-len(toks))+[encoder.get(i, 0) for i in toks]])
        result = model(sent_idx.to(model.device))
        print(tar_dict[int(torch.argmax(result, dim=1))])