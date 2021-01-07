from master_db import MasterDBStorage
from utils.functions import show_elapsed_time
import pandas as pd
import warnings, os
from collections import Counter
from utils.config import PACKAGING_CENTER
from part_search.partsys_search import partsys_3_search
from problem_search.predict import PredictionOnData
from problem_search.config import *
from problem_search.CNN import CNNModel
from rankings import RankFilter


class Master:
    warnings.filterwarnings('ignore')
    master_col = ['고객사', '차종', 'Part No', '부품명', '단위', '포장장', '납품업체', '납품업체명', '부품로트 대상여부']

    def __init__(self, d_type):
        self.type = d_type
        self.master_df = MasterDBStorage('파트마스터', append_from_file=True).df
        self.master_df = self.master_df[self.master_col]
        self.inspection_df = MasterDBStorage('중점검사표', append_from_file=True).df
        self.inspection_df['Part No'] = [i.replace(" ", "") for i in self.inspection_df['Part No'].tolist()]
        if self.type == 'dom':
            self.dom_insp_df = MasterDBStorage('입고불량이력', append_from_file=True).df
            self.dom_insp_df['Part No'] = [i.replace(" ", "") for i in self.dom_insp_df['Part No'].tolist()]
        if self.type == 'exp':
            self.exp_insp_df = MasterDBStorage('해외불량이력', append_from_file=True).df
            self.exp_insp_df.rename(columns={'품번': 'Part No', '품명' : '부품명'}, inplace=True)

        self.in_business_df = MasterDBStorage('매입대', append_from_file=True).df
        self.part_sys_2_df = MasterDBStorage('품번체계', append_from_file=True).df
        self.packingspect_df = MasterDBStorage('전차종포장사양서', append_from_file=True).df
        self.spawn_name = rf'files\spawn\{self.type}_spawn.xlsx'

    @show_elapsed_time
    def packaging_spec_information(self):
        incomming_date = [i.split('.')[0] for i in self.packingspect_df['최종입고일자'].tolist()]
        part_list = self.packingspect_df['부품코드'].tolist()
        middle_box_code_list = self.packingspect_df['중박스코드'].tolist()
        middle_box = self.packingspect_df['부품업체중포장여부'].tolist()
        big_box = self.packingspect_df['부품업체대포장여부'].tolist()
        supplier_packing_list = ["" for _ in range(len(middle_box))]

        for n, i in enumerate(part_list):
            if middle_box[n] == 'Y' or big_box[n] == 'Y':
                supplier_packing_list[n] = True
            else:
                supplier_packing_list[n] = False

        imcomming_date_dict = dict(zip(part_list, incomming_date))
        weight_dict = dict(zip(part_list, self.packingspect_df['단중'].tolist()))
        supplier_packing_dict = dict(zip(part_list, supplier_packing_list))
        middle_box_code_dict = dict(zip(part_list, middle_box_code_list))

        self.master_df['최종입고일'] = [imcomming_date_dict.get(i, '') for i in self.master_df['Part No'].tolist()]
        self.master_df['단중'] = [weight_dict.get(i, '') for i in self.master_df['Part No'].tolist()]
        self.master_df['업체포장여부'] = [supplier_packing_dict.get(i, '') for i in self.master_df['Part No'].tolist()]
        self.master_df['중박스코드'] = [middle_box_code_dict.get(i, '') for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def packaging_center(self):
        self.master_df['포장장명'] = [PACKAGING_CENTER.get(i, '') for i in self.master_df['포장장'].tolist()]

    @staticmethod
    @show_elapsed_time
    def part_type_1_2(df):
        with open('files/품목구분기준.xlsx', 'rb') as file:
            df_1 = pd.read_excel(file, sheet_name='부품체계1')
            df_2 = pd.read_excel(file, sheet_name='부품체계2')
        partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
        partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
        df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in df['Part No'].tolist()]
        df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in df['Part No'].tolist()]
        return df

    @staticmethod
    @show_elapsed_time
    def part_type_3_4(df):
        partsys_3_search(df)
        return df

    @show_elapsed_time
    def inspection_binary(self):
        inspection_item = set(self.inspection_df['Part No'].tolist())
        self.master_df['중점검사표유무'] = [True if i in inspection_item else False for i in
                                     self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def business_binary(self):
        business_item = set(self.in_business_df['업체코드'].tolist())
        self.master_df['거래지속여부'] = [True if i in business_item else False for i in
                                     self.master_df['납품업체'].tolist()]

    @show_elapsed_time
    def dom_prob_type(self):
        types = set([i for i in self.dom_insp_df['불량구분'].tolist() if i not in ['전체']])
        temp_df = self.dom_insp_df.groupby(['Part No', "불량구분"]).size().reset_index(name="freq")
        dom_insp_item = temp_df['Part No'].tolist()
        temp_df.set_index(['Part No', '불량구분'], inplace=True)
        item_dict = {i: {t: 0 for t in types} for i in dom_insp_item}
        for i in dom_insp_item:
            for t in types:
                try :
                    count = temp_df.loc[(i, t), 'freq']
                except KeyError :
                    count = 0
                item_dict[i][t] = + count
        for t in types:
            self.master_df[f'입고_{t}'] = [item_dict.get(i, {t: 0 for t in types})[t] for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def exp_prob_type(self):
        types = set([i for i in self.exp_insp_df['불량구분'].tolist() if i not in ['']])
        temp_df = self.exp_insp_df.groupby(['Part No', "불량구분"]).size().reset_index(name="freq")
        exp_insp_item = temp_df['Part No'].tolist()
        temp_df.set_index(['Part No', '불량구분'], inplace=True)
        item_dict = {i: {t: 0 for t in types} for i in exp_insp_item}
        for i in exp_insp_item:
            for t in types:
                try :
                    count = temp_df.loc[(i, t), 'freq']
                except KeyError :
                    count = 0
                item_dict[i][t] = + count
        for t in types:
            self.master_df[f'해외_{t}'] = [item_dict.get(i, {t: 0 for t in types})[t] for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def dom_frequency(self):
        dom_freq = Counter(self.dom_insp_df['Part No'].tolist())
        self.master_df['입고불량발생빈도'] = [dom_freq.get(i, 0) for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def exp_frequency(self):
        exp_freq = Counter(self.exp_insp_df['Part No'].tolist())
        self.master_df['해외불량발생빈도'] = [exp_freq.get(i, 0) for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def dom_amount(self):
        amount_dict = dict()
        for n, i in enumerate(self.dom_insp_df['Part No'].tolist()):
            if i not in amount_dict.keys():
                amount_dict[i] = int(self.dom_insp_df.loc[n, '불량수량'])
            else:
                amount_dict[i] += int(self.dom_insp_df.loc[n, '불량수량'])
        self.master_df['입고불량발생수량'] = [amount_dict.get(i, 0) for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def exp_amount(self):
        amount_dict = dict()
        for n, i in enumerate(self.exp_insp_df['Part No'].tolist()):
            if i not in amount_dict.keys():
                amount_dict[i] = int(self.exp_insp_df.loc[n, '조치수량'])
            else:
                amount_dict[i] += int(self.exp_insp_df.loc[n, '조치수량'])
        self.master_df['해외불량조치수량'] = [amount_dict.get(i, 0) for i in self.master_df['Part No'].tolist()]

    @show_elapsed_time
    def prob_specify(self, df):
        model = CNNModel(n_vocab=n_vocab, n_embedding=n_embedding, n_outputs=n_outputs, seed=0)
        df = PredictionOnData(df=df, model=model).encode()
        titles_rewritten = df["제목_정리"].tolist()
        print(Counter(titles_rewritten))
        # return df

    @show_elapsed_time
    def appearance_type(self, df):
        with open(file_path, 'rb') as file:
            sys_df = pd.read_excel(file, sheet_name="체계")
            types_forvision = sys_df[sys_df['비전검사대상'] == "○"]['불량명'].tolist()

        temp_df = df.groupby(['Part No', "제목_정리"]).size().reset_index(name="freq")
        insp_item = temp_df['Part No'].tolist()
        titles = temp_df['제목_정리'].tolist()

        temp_df.set_index(['Part No', '제목_정리'], inplace=True)
        item_dict = {i: {t: 0 for t in types_forvision} for i in insp_item}
        for i in insp_item:
            for t in types_forvision:
                try:
                    count = temp_df.loc[(i, t), 'freq']
                except KeyError:
                    count = 0
                item_dict[i][t] = + count
        for t in types_forvision:
            self.master_df[f'비전_{t}'] = [item_dict.get(i, {t: 0 for t in types_forvision})[t] for i in
                                         self.master_df['Part No'].tolist()]

        item_dict_2 = {i : list() for i in df['Part No']}
        for n, i in enumerate (insp_item):
            t = titles[n]
            if t in types_forvision and t not in item_dict_2[i]:
                item_dict_2[i].append(t)

        self.master_df['_비전가능불량상세'] = [','.join(i) if type(i) == list else i for i in [item_dict_2.get(i, "") for i in self.master_df['Part No'].tolist()]]
        self.master_df['_비전가능불량유형수'] = [len(i) if type(i) == list else 0 for i in [item_dict_2.get(i, "") for i in self.master_df['Part No'].tolist()]]

    @classmethod
    def run(cls, d_type='exp'):
        obj = cls(d_type)
        obj.packaging_center()
        obj.packaging_spec_information()
        obj.inspection_binary()
        obj.business_binary()
        obj.master_df = obj.part_type_1_2(obj.master_df)
        obj.master_df = obj.part_type_3_4(obj.master_df)
        
        if obj.type == 'dom':
            obj.dom_prob_type()
            obj.dom_frequency()
            obj.dom_amount()
            obj.prob_specify(obj.dom_insp_df)
            obj.appearance_type(obj.dom_insp_df)
            return obj.master_df, obj.dom_insp_df

        if obj.type == 'exp':
            obj.exp_prob_type()
            obj.exp_frequency()
            obj.exp_amount()
            obj.prob_specify(obj.exp_insp_df)
            obj.appearance_type(obj.exp_insp_df)
            return obj.master_df, obj.exp_insp_df

        obj.update_db(obj.master_df, df_name='master')

    @show_elapsed_time
    def update_db(self, df, df_name='master'):
        if df_name == 'master':
            table_name = df_name + '_' + self.type + '_spawn'
        else :
            table_name = self.type + '_spawn'
        MasterDBStorage.run(table_name, df=df)


if __name__ == "__main__":

    d_type = 'exp'
    df_master, df_aux = Master.run(d_type=d_type)
    grouped_df_1, grouped_df_3 = RankFilter('exp').grouping()

    with pd.ExcelWriter(rf'files\spawn\{d_type}_부품선정.xlsx') as writer:
        df_master.to_excel(writer, sheet_name=f'master+{d_type}', index=False)
        df_aux.to_excel(writer, sheet_name=f'{d_type}_raw', index=False)
        grouped_df_1.to_excel(writer, sheet_name='대표부품기준', index=False)
        grouped_df_3.to_excel(writer, sheet_name='부품상세기준', index=False)
    os.startfile(rf'files\spawn\{d_type}_부품선정.xlsx')