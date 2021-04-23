import pandas as pd
from problem_search.filters import prob_words_not_to_skip, prob_additional_exceptions
from part_search.partsys_search import partsys_3_search
from utils.functions import show_elapsed_time
import torchtext.data as ttd
import torch, os, pickle, re, random
from utils.functions import flatten, remove_duplication
from problem_search.config import *
from collections import Counter
from master_db import MasterDBStorage


class Dataset:
    random.seed(0)

    def __init__(self, file_path, split_ratio=split_ratio, update_csv=False):
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
        if update_csv:  # csv파일과 타깃 인코더를 업그레이드할때만 사용함
            self.df = partsys(self.df)
            self.df = preprocess(self.df)
            self.encode_target()
            self.spawn()
        else:
            self.encode_dataset()
            print("Total Vocabs: ", len(self.text.vocab.stoi))

    @show_elapsed_time
    def get_dataframe(self):
        with open(self.file_path, 'rb') as file:
            # df = pd.read_excel(file, usecols="F, H, K, L")
            df = pd.read_excel(file)
            df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
            print(df)
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
        print("Target :",len(self.tar_encoder.keys()),"classes")

    @show_elapsed_time
    def save_target_decoder(self):
        self.tar_decoder = dict(zip(self.tar_encoder.values(), self.tar_encoder.keys()))
        with open('files/spawn/tar_decoder.pkl', 'wb') as f:
            pickle.dump(self.tar_decoder, f)
        # print("decoder part")
        # print(self.tar_decoder)

    @show_elapsed_time
    def encode_target(self):
        self.df['encoded_target'] = [self.tar_encoder.get(i, 0) for i in self.df['target']]

    @show_elapsed_time
    def encode_dataset(self):
        self.text = ttd.Field(sequential=True, batch_first=True, lower=False,
                              tokenize=str.split,
                              pad_first=True, fix_length=fix_length)
        self.label = ttd.Field(sequential=False, use_vocab=False, is_target=True)
        self.dataset = ttd.TabularDataset(path=self.spawn_path, format='csv', skip_header=True,
                                          fields=[('data', self.text), ('encoded_target', self.label)])

        self.train_dataset, self.test_dataset = self.dataset.split(split_ratio=self.split_ratio,
                                                                   stratified=True,
                                                                   strata_field='encoded_target',
                                                                   random_state=random.getstate())

        self.text.build_vocab(self.dataset, min_freq=3, max_size=n_vocab)
        self.save_encoder_decoder()

    def get_iter(self, batch_sizes=(32, 256)):
        train_iter, test_iter = ttd.Iterator.splits((self.train_dataset, self.test_dataset), sort_key=lambda x: len(x.data),
                                                    batch_sizes=batch_sizes, device=self.device)
        return train_iter, test_iter


def part_names():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols="B:C, F, H, K, L, O")
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
        partnames = remove_duplication(flatten(partnames))
        partnames_kor = df['기준1'].tolist()
        partnames_kor = remove_duplication(partnames_kor)
        partnames += partnames_kor
    with open('files/spawn/부품명리스트.pkl', 'wb') as f:
        pickle.dump(partnames, f)
    return partnames


def model_names():
    df = MasterDBStorage('입고불량이력', to_db=True).df
    model_list = remove_duplication(df['차종'].tolist())
    with open('files/spawn/차종리스트.pkl', 'wb') as f:
        pickle.dump(model_list, f)
    return model_list


def supplier_names():
    df = MasterDBStorage('파트마스터').df
    df = df[['납품업체', '납품업체명']]
    codes = remove_duplication(df['납품업체'].tolist())
    names = remove_duplication(flatten(
        [str(i).upper().replace('(주)', " ").replace('(유)', " ").replace('(', " ").replace(')', " ").split(' ') for i
         in df['납품업체명'].tolist()]))
    names = [i for i in names if len(i) > 0]
    with open('files/spawn/부품사리스트.pkl', 'wb') as f:
        pickle.dump(codes + names, f)
    return codes + names


def get_basic_filters():
    if os.path.isfile('files/spawn/부품명리스트.pkl'):
        with open('files/spawn/부품명리스트.pkl', 'rb') as f:
            part_list = pickle.load(f)
    else:
        part_list = part_names()
    if os.path.isfile('files/spawn/부품사리스트.pkl'):
        with open('files/spawn/부품사리스트.pkl', 'rb') as f:
            supplier_list = pickle.load(f)
    else:
        supplier_list = supplier_names()

    if os.path.isfile('files/spawn/차종리스트.pkl'):
        with open('files/spawn/차종리스트.pkl', 'rb') as f:
            model_list = pickle.load(f)
    else:
        model_list = model_names()

    return part_list, supplier_list, model_list


def preprocess(df, for_train=True):
    part_list, supplier_list, model_list = get_basic_filters()
    words_to_skip = [i for i in part_list + supplier_list + model_list if i not in prob_words_not_to_skip]
    words_to_skip += prob_additional_exceptions
    print("Filtering :", len(words_to_skip))

    word_list = []
    titles = [str(i).upper() for i in df['제목'].tolist()]
    for title in titles:

        name = title.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
            "SUB PART PROBLEM", "SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
            "PRESSURE", "압력").replace("NOT FIXED", "SUBPART").replace("FITTING", "FIT").replace(
            "FITTED","FIT").replace("NOT FIT", "UNFITTING").replace("BAD FIT", "UNFITTING").replace(
            "갭", "GAP").replace("WELDING/PRESS", "웰딩/프레스").replace("WELD LINE", "WELDLINE").replace(
            "홀", "HOLE").replace("BAR CODE", "BARCODE").replace("버", "BURR")

        name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_,]|[\W]", ' ', name)

        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

    df['정리'] = [' '.join(i) for i in word_list]
    df['data'] = df['정리'] + ' ' + df['부품체계_1'] + ' ' + df['부품체계_2'] + ' ' + df['부품체계_3']
    df['data'] = [re.sub("[,.\-_&]", "", str(i)).replace("  ", " ") for i in df['data'].tolist()]
    df['data_len'] = [len(str(i).split(' ')) for i in df['data'].tolist()]
    if for_train:
        df['target'] = [str(i).replace(' ', '') for i in df['target'].tolist()]
        df['target_빈도'] = [Counter(df['target'].tolist())[i] for i in df['target'].tolist()]
        df_ = df[['부품명', 'Part No', '제목', '정리', '부품체계_1', '부품체계_2', '부품체계_3', 'data', 'target',
                           'target_빈도', 'data_len']]
        return df_
    else:
        return df


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
    # from master_db import MasterDBStorage
    # os.chdir(os.pardir)
    #
    #
    # def dom_data():
    #     df = MasterDBStorage('입고불량이력', append_from_file=True).df
    #     df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
    #     df.fillna("", inplace=True)
    #     return df
    #
    # df = partsys(dom_data())
    # df = preprocess(df, for_train=False)
    # df[['제목', '정리', '부품체계_1', '부품체계_2', '부품체계_3', 'data']].to_csv('files\spawn\dom_experiment_data.csv', index=False, encoding='utf-8-sig')
    # os.startfile('files\spawn\dom_experiment_data.csv')

    os.chdir(os.pardir)
    data = Dataset(file_path=file_path, update_csv=True)


