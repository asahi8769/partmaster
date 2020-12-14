from searches.problemsys_search import *
from searches.filters import prob_words_not_to_skip, prob_additional_exceptions
from searches.partsys_search import partsys_3_search
from utils.functions import show_elapsed_time
import torchtext.data as ttd
import torch

#  데이터셋을 인코딩하고 이터레이터를 리턴하는 클래스를 만들고, 그 과정에서 백터라이징하는 딕셔너리는 따로 저장되도록 하자

class Dataset:
    def __init__(self, file_path, split_ratio=0.7):
        self.split_ratio = split_ratio
        self.des_tokens = None
        self.tar_tokens = None
        self.document = None
        self.encoder = dict()
        self.decoder = dict()
        self.tar_encoder = dict()
        self.tar_decoder = dict()
        self.file_path = file_path
        self.df = None
        self.spawn_path = 'files\spawn\experiment_data.csv'
        self.train_dataset = None
        self.test_dataset = None
        self.text = None
        self.label = None
        self.dataset = None
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        # self.get_dataframe()  # csv파일을 업그레이드할때만 사용함
        # self.preprocess()
        # self.encode_data()
        self.binary_text_dataset()

    @show_elapsed_time
    def get_dataframe(self):
        with open(self.file_path, 'rb') as file:
            self.df = pd.read_excel(file, usecols="F, H, K, L")

    @show_elapsed_time
    def preprocess(self,):
        self.df.rename(columns={'품번': 'Part No', '품명': '부품명', '불량구분': 'target'}, inplace=True)
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
        self.tar_tokens = self.df['target'].tolist()

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
        self.df[['data', 'encoded_target']].to_csv(self.spawn_path, index=False, encoding='utf-8-sig')
        os.startfile(self.spawn_path)

    @show_elapsed_time
    def get_longest_token(self):
        return max(self.df['data_len'].tolist())

    @show_elapsed_time
    def get_encoder(self):
        idx = 2
        for word_list in self.des_tokens:
            for word in word_list:
                if word not in self.encoder:
                    self.encoder[word] = idx
                    idx += 1
        with open('files/spawn/encoder.pkl', 'wb') as f:
            pickle.dump(self.encoder, f)

    @show_elapsed_time
    def get_decoder(self):
        self.decoder = dict(zip(self.encoder.values(), self.encoder.keys()))
        with open('files/spawn/decoder.pkl', 'wb') as f:
            pickle.dump(self.decoder, f)

    @show_elapsed_time
    def get_target_encoder(self):
        idx = 0
        for word in self.tar_tokens:
            if word not in self.tar_encoder:
                self.tar_encoder[word] = idx
                idx += 1
        with open('files/spawn/tar_encoder.pkl', 'wb') as f:
            pickle.dump(self.tar_encoder, f)

    @show_elapsed_time
    def get_target_decoder(self):
        self.tar_decoder = dict(zip(self.tar_encoder.values(), self.tar_encoder.keys()))
        with open('files/spawn/tar_decoder.pkl', 'wb') as f:
            pickle.dump(self.tar_decoder, f)

    @show_elapsed_time
    def encode_data(self):
        self.get_encoder()
        self.get_decoder()
        self.get_target_encoder()
        self.get_target_decoder()
        longest_len = self.get_longest_token()
        encoded_doc = []
        for word_list in self.des_tokens:
            converted_word_list = []
            for i in range(longest_len - len(word_list)):
                converted_word_list.append(0)
            for word in word_list:
                converted_word_list.append(self.encoder.get(word, 1))
            encoded_doc.append(converted_word_list)

        self.df['encoded_data'] = [', '.join([str(j) for j in i]) for i in encoded_doc]
        self.df['encoded_target'] = [self.encoder.get(i, 1) for i in self.df['target']]
        self.df['encoded_target'] = [self.tar_encoder.get(i, 1) for i in self.df['target']]
        self.spawn()
        print(len(self.tar_encoder.keys()))

    @show_elapsed_time
    def binary_text_dataset(self):
        self.text = ttd.Field(sequential=True, batch_first=True, lower=False,
                              # tokenize='spacy',
                              pad_first=True)
        self.label = ttd.Field(sequential=False, use_vocab=False, is_target=True)
        self.dataset = ttd.TabularDataset(path=self.spawn_path, format='csv', skip_header=True,
                                          fields=[('data', self.text), ('encoded_target', self.label)])
        self.train_dataset, self.test_dataset = self.dataset.split(split_ratio=self.split_ratio )
        self.text.build_vocab(self.train_dataset)
        self.vocab = self.text.vocab
        self.encoder = self.text.vocab.stoi
        self.decoder = self.text.vocab.itos
        # print(self.decoder)

    def get_iter(self, batch_sizes=(32, 256)):
        train_iter, test_iter = ttd.Iterator.splits((self.train_dataset, self.test_dataset),
                                                    sort_key=lambda x: len(x.data),
                                                    batch_sizes=batch_sizes, device=self.device)
        return train_iter, test_iter


if __name__ == "__main__":
    os.chdir(os.pardir)
    data = Dataset(file_path='files/불량유형수기정리.xlsx')
    # data.encode_data()
    # print(data.tokens)

