from searches.problemsys_search import *
from utils.functions import show_elapsed_time
from searches.partsys_search import partsys_3_search
import torch
from experiment.CNN import CNNModel
from experiment.dataset import preprocess, partsys
from experiment.config import *


class PredictionOnData:
    def __init__(self, df, model):
        self.model = model
        # self.file_path = file_path
        self.spawn_path = 'files\spawn\experiment_data_predicted.csv'
        self.encoder = self.load_encoder()
        self.tar_dict = self.load_tardict()
        self.des_tokens = None
        self.df = df
        self.df = partsys(self.df)
        self.df = preprocess(self.df, for_train=False)
        self.encode()
        self.spawn()

    @show_elapsed_time
    def load_encoder(self):
        with open('files/spawn/encoder.pkl', 'rb') as file:
            encoder = pickle.load(file)
        return encoder

    @show_elapsed_time
    def load_tardict(self):
        with open('files/spawn/tar_decoder.pkl', 'rb') as file:
            tar_dict = pickle.load(file)
        return tar_dict

    @show_elapsed_time
    def partsys(self):
        with open('files/품목구분기준.xlsx', 'rb') as file:
            df_1 = pd.read_excel(file, sheet_name='부품체계1')
            df_2 = pd.read_excel(file, sheet_name='부품체계2')
        partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
        partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
        self.df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in self.df['Part No'].tolist()]
        self.df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in self.df['Part No'].tolist()]
        self.df = partsys_3_search(self.df)

    @show_elapsed_time
    def spawn(self):
        self.df.to_csv(self.spawn_path, index=False, encoding='utf-8-sig')
        os.startfile(self.spawn_path)

    @show_elapsed_time
    def encode(self):
        with torch.no_grad():
            self.model.load_checkpoint()
            self.model.eval()
            predicts = ["" for _ in self.df['data']]
            self.des_tokens = [str(i).split(' ') for i in self.df['data']]
            for n, sentence in enumerate(self.des_tokens):
                sent_idx = torch.LongTensor([[1] * (fix_length - len(sentence)) + [self.encoder.get(i, 0) for i in sentence]])
                result = self.model(sent_idx.to(self.model.device))
                predicts[n] = self.tar_dict[int(torch.argmax(result, dim=1))]
        self.df['predict'] = predicts


if __name__ == "__main__":
    from master_db import MasterDBStorage
    os.chdir(os.pardir)


    def learning_data():
        with open('files/불량유형수기정리.xlsx', 'rb') as file:
            df = pd.read_excel(file, usecols="F, H, K, L")
            df.rename(columns={'품번': 'Part No', '품명': '부품명', '수기불량구분': 'target'}, inplace=True)
        return df

    def exp_data():
        df = MasterDBStorage('해외불량이력', append_from_file=True).df
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
        # df.drop_duplicates(subset="Part No", keep='first', inplace=True)
        # df.drop_duplicates(subset="부품명", keep='first', inplace=True)
        return df

    df = exp_data()
    # df = learning_data()

    model = CNNModel(n_vocab=n_vocab, n_embedding=n_embedding, n_outputs=n_outputs, seed=0)
    PredictionOnData(df=df, model=model)