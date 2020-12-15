from experiment.RNN import RNNModel
from experiment.CNN import CNNModel
from experiment.trainer import ModelTrainer
from experiment.dataset import Dataset
import os, pickle
import torch

os.chdir(os.pardir)

model = CNNModel(n_vocab=700, n_embedding=128, n_outputs=512, seed=0)

data = Dataset(file_path='files/불량유형수기정리.xlsx', update_csv=False)
train_iter, test_iter = data.get_iter(batch_sizes=(32, 1000))
trainer = ModelTrainer(model, train_iter, test_iter, lr=0.00005, epochs=500)
trainer.batch_learn()
trainer.plot_result()


sentence1 = 'WRONG SPEC PROBLEM POWER TRAIN & CHASSIS-ETC AUTOMATIC T/M OVER DRIVER 노브&부트'
sentence2 = 'MALFUNCTION PROBLEM POWER TRAIN & CHASSIS-ETC AUTOMATIC T/M OVER DRIVER 노브&부트'
sentence3 = 'SCRATCHES SEALANT TORQUE PROBLEM MISS EXCESS PAINT LEAK ENGINE CYLINDER BLOCK 팬_오일'

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
        sent_idx = torch.LongTensor([[1]*(15-len(toks))+[encoder.get(i, 0) for i in toks]])
        result = model(sent_idx.to(model.device))
        print(tar_dict[int(torch.argmax(result, dim=1))])




""" https://discuss.pytorch.org/t/loading-model-test-accuracy-drops/22833/4 """
""" https://towardsdatascience.com/how-to-save-and-load-a-model-in-pytorch-with-a-complete-example-c2920e617dee """
""" https://stackoverflow.com/questions/42703500/best-way-to-save-a-trained-model-in-pytorch """ ## must see this