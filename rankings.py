import pandas as pd
import warnings, os
from utils.functions import show_elapsed_time
from part_master import MasterDBStorage


class DomeFilter:
    warnings.filterwarnings('ignore')

    def __init__(self, type):
        table_name = 'master_' + type + '_spawn'
        self.spawn_name = rf'files\{type}_ranking.xlsx'
        self.master_df = MasterDBStorage(table_name).df
        self.master_df.fillna("", inplace=True)
        self.master_df.apply(pd.to_numeric, errors='ignore')
        self.pre_processing()
        self.filtering()
        print('Remaining Parts After Filtering :', len(self.master_df))
        self.grouping()

    def pre_processing(self):
        self.master_df['최종입고일'] = [int(i.split('.')[0]) if i != '' else 0 for i in self.master_df['최종입고일'].tolist()]
        self.master_df['단중'] = [float(i) if i != '' else 0 for i in self.master_df['단중'].tolist()]
        self.master_df['업체포장여부'] = ['True' if i == '1.0' else 'False' for i in self.master_df['업체포장여부'].tolist()]

    def filtering(self):
        filters = (
                (self.master_df['최종입고일'] >= 20200601)
                & (self.master_df['단중'] <= 4000)
                & (self.master_df['단중'] > 0)
                # & (self.master_df['업체포장여부'] != 'True')
                # & (self.master_df['중점검사표유무'] == 'True')
                & (self.master_df['거래지속여부'] == 'True')
                & ((self.master_df['포장장명'].str.contains('아산') & self.master_df['중박스코드'].str.startswith('P'))|(self.master_df['포장장명'] == '아산3포장장'))
        )
        self.master_df = self.master_df[filters]
        # print(self.master_df['포장장명'].tolist())

    @show_elapsed_time
    def grouping(self):
        criterion_list = list(filter(lambda x: x.startswith('외관') or x == '_외관불량유형수', self.master_df.columns.tolist()))
        grouped_df_3 = self.master_df.groupby(['부품체계_3'])[criterion_list].apply(
            lambda x: x.astype(float).sum()).reset_index()
        grouped_df_4 = self.master_df.groupby(['부품체계_4'])[criterion_list].apply(
            lambda x: x.astype(float).sum()).reset_index()
        with pd.ExcelWriter(self.spawn_name) as writer:
            grouped_df_3.to_excel(writer, sheet_name='부품체계_3_기준', index=False)
            grouped_df_4.to_excel(writer, sheet_name='부품체계_4_기준', index=False)
        os.startfile(self.spawn_name)


if __name__ == "__main__":
    DomeFilter('dom')
    DomeFilter('exp')
