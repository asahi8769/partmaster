from searches.problemsys_search import *
from utils.functions import show_elapsed_time
from searches.partsys_search import partsys_3_search
import torch
from experiment.CNN import CNNModel

class PredictionOnData:
    def __init__(self, file_path, model):
        self.model = model
        self.file_path = file_path
        self.spawn_path = 'files\spawn\experiment_data_predicted.csv'
        self.encoder = self.load_encoder()
        self.tar_dict = self.load_tardict()
        self.des_tokens = None
        self.get_dataframe()
        self.preprocess()
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
    def get_dataframe(self):
        with open(self.file_path, 'rb') as file:
            self.df = pd.read_excel(file, usecols="F, H, K, L")
            self.df.rename(columns={'품번': 'Part No', '품명': '부품명', '수기불량구분': 'target'}, inplace=True)

    @show_elapsed_time
    def preprocess(self,):
        self.partsys()
        part_list, supplier_list = get_basic_filters()
        words_to_skip = [i for i in part_list + supplier_list if i not in prob_words_not_to_skip]
        words_to_skip += prob_additional_exceptions
        print("Filtering :", len(words_to_skip))
        word_list = []
        title = [i.upper() for i in self.df['제목'].tolist()]
        for i, n in enumerate(title):
            name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
                "SUB PART PROBLEM", "SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
                "PRESSURE", "압력").replace("NOT FIXED", "SUBPART").replace("FITTING", "FIT").replace(
                "FITTED","FIT").replace("NOT FIT", "UNFITTING").replace("BAD FIT", "UNFITTING").replace(
                "갭", "GAP").replace("WELDING/PRESS", "웰딩/프레스").replace(
                "WELD LINE", "WELDLINE").replace("홀", "HOLE").replace("BAR CODE", "BARCODE")
            name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_]|[\W]", ' ', name)
            words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
            word_list.append(words)
        self.df['정리'] = [' '.join(i) for i in word_list]
        self.df['target'] = [str(i).replace(' ', '') for i in self.df['target'].tolist()]
        self.df['target_빈도'] = [Counter(self.df['target'].tolist())[i] for i in self.df['target'].tolist()]
        self.df['data'] = self.df['정리'] +' '+ self.df['부품체계_1'] +' '+ self.df['부품체계_2']+' '+ self.df['부품체계_3']
        self.df['data'] = [str(i).replace(',', ' ') for i in self.df['data'].tolist()]
        self.df['data_len'] = [len(i.split(' ')) for i in self.df['data'].tolist()]
        self.df = self.df[['부품명', 'Part No', '제목', '정리', '부품체계_1', '부품체계_2', '부품체계_3', 'data', 'target',
                           'target_빈도', 'data_len']]
        self.df.sort_values(['data_len', 'target_빈도'], inplace=True, ascending=[False, False])
        self.des_tokens = [str(i).split(' ') for i in self.df['data']]

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

    def encode(self):
        with torch.no_grad():
            self.model.load_checkpoint()
            self.model.eval()
            predicts = ["" for _ in self.df['data']]
            for n, sentence in enumerate(self.des_tokens):
                sent_idx = torch.LongTensor([[1] * (15 - len(sentence)) + [self.encoder.get(i, 0) for i in sentence]])
                result = self.model(sent_idx.to(self.model.device))
                predicts[n] = self.tar_dict[int(torch.argmax(result, dim=1))]
        self.df['predict'] = predicts


if __name__ == "__main__":
    os.chdir(os.pardir)
    model = CNNModel(n_vocab=500, n_embedding=128, n_outputs=512, seed=0)
    PredictionOnData('files/불량유형수기정리.xlsx', model=model)