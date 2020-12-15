from searches.problemsys_search import *
from searches.filters import prob_words_not_to_skip, prob_additional_exceptions
from searches.partsys_search import partsys_3_search
from utils.functions import show_elapsed_time
import torchtext.data as ttd
import torch
import random


class Dataset:
    def __init__(self, file_path, split_ratio=0.7, update_csv=False):
        self.split_ratio = split_ratio
        self.tar_tokens = None
        self.document = None
        self.encoder = dict()
        self.decoder = dict()
        self.tar_encoder = dict()
        self.tar_decoder = dict()
        self.file_path = file_path
        self.spawn_path = 'files\spawn\experiment_data.csv'
        self.train_dataset = None
        self.test_dataset = None
        self.text = None
        self.label = None
        self.dataset = None
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.df = self.get_dataframe()
        self.save_target_encoder()
        self.save_target_decoder()
        if update_csv:  # csv파일을 업그레이드할때만 사용함
            self.df = partsys(self.df)
            self.df = preprocess(self.df)
            self.encode_data()
        else:
            self.binary_text_dataset()


    @show_elapsed_time
    def get_dataframe(self):
        with open(self.file_path, 'rb') as file:
            df = pd.read_excel(file, usecols="F, H, K, L")
            df.rename(columns={'품번': 'Part No', '품명': '부품명', '수기불량구분': 'target'}, inplace=True)
        return df

    @show_elapsed_time
    def spawn(self):
        self.df[['data', 'encoded_target']].to_csv(self.spawn_path, index=False, encoding='utf-8-sig')
        os.startfile(self.spawn_path)

    @show_elapsed_time
    def save_encoder_decoder(self):
        with open('files/spawn/encoder.pkl', 'wb') as f:
            pickle.dump(self.text.vocab.stoi, f)
        with open('files/spawn/decoder.pkl', 'wb') as f:
            pickle.dump(self.text.vocab.itos, f)

    @show_elapsed_time
    def save_target_encoder(self):
        idx = 0
        self.tar_tokens = self.df['target'].tolist()
        for word in self.tar_tokens:
            if word not in self.tar_encoder:
                self.tar_encoder[word] = idx
                idx += 1
        with open('files/spawn/tar_encoder.pkl', 'wb') as f:
            pickle.dump(self.tar_encoder, f)
        print(self.tar_encoder)

    @show_elapsed_time
    def save_target_decoder(self):
        self.tar_decoder = dict(zip(self.tar_encoder.values(), self.tar_encoder.keys()))
        with open('files/spawn/tar_decoder.pkl', 'wb') as f:
            pickle.dump(self.tar_decoder, f)
        # print("decoder part")
        # print(self.tar_decoder)

    @show_elapsed_time
    def encode_data(self):
        self.df['encoded_target'] = [self.tar_encoder.get(i, 0) for i in self.df['target']]
        self.spawn()

    @show_elapsed_time
    def binary_text_dataset(self):
        self.text = ttd.Field(sequential=True, batch_first=True, lower=False,
                              tokenize=str.split,
                              pad_first=True, fix_length=15)
        self.label = ttd.Field(sequential=False, use_vocab=False, is_target=True)
        self.dataset = ttd.TabularDataset(path=self.spawn_path, format='csv', skip_header=True,
                                          fields=[('data', self.text), ('encoded_target', self.label)])
        self.train_dataset, self.test_dataset = self.dataset.split(split_ratio=self.split_ratio)

        self.text.build_vocab(self.train_dataset, min_freq=5, max_size=10000)
        self.save_encoder_decoder()

    def get_iter(self, batch_sizes=(32, 256)):
        train_iter, test_iter = ttd.Iterator.splits((self.train_dataset, self.test_dataset), sort_key=lambda x: len(x.data),
                                                    batch_sizes=batch_sizes, device=self.device)
        return train_iter, test_iter


def preprocess(df):
    part_list, supplier_list = get_basic_filters()
    words_to_skip = [i for i in part_list + supplier_list if i not in prob_words_not_to_skip]
    words_to_skip += prob_additional_exceptions
    print("Filtering :", len(words_to_skip))
    word_list = []
    title = [i.upper() for i in df['제목'].tolist()]
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
    df['정리'] = [' '.join(i) for i in word_list]
    df['target'] = [str(i).replace(' ', '') for i in df['target'].tolist()]
    df['target_빈도'] = [Counter(df['target'].tolist())[i] for i in df['target'].tolist()]
    df['data'] = df['정리'] +' '+ df['부품체계_1'] +' '+ df['부품체계_2']+' '+ df['부품체계_3']
    df['data'] = [re.sub("[\W]", "",str(i).replace(',', ' ')) for i in df['data'].tolist()]
    df['data_len'] = [len(i.split(' ')) for i in df['data'].tolist()]
    df_ = df[['부품명', 'Part No', '제목', '정리', '부품체계_1', '부품체계_2', '부품체계_3', 'data', 'target',
                       'target_빈도', 'data_len']]
    # df_.sort_values(['data_len', 'target_빈도'], inplace=True, ascending=[False, False])
    return df_


@show_elapsed_time
def partsys(df):
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df_1 = pd.read_excel(file, sheet_name='부품체계1')
        df_2 = pd.read_excel(file, sheet_name='부품체계2')
    partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
    partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
    df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in df['Part No'].tolist()]
    df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in df['Part No'].tolist()]
    df = partsys_3_search(df)
    return df


if __name__ == "__main__":
    os.chdir(os.pardir)
    data = Dataset(file_path='files/불량유형수기정리.xlsx', update_csv=True)
    # data = Dataset(file_path='files/불량유형수기정리.xlsx', update_csv=False)
    # data.encode_data()
    # print(data.tokens)

