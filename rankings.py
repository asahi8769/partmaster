import pandas as pd
import warnings, os
from utils.functions import show_elapsed_time
from master_db import MasterDBStorage
# from utils.functions import remove_duplication


class RankFilter:
    warnings.filterwarnings('ignore')

    def __init__(self, type):
        table_name = 'master_' + type + '_spawn' # todo : fix this
        insp_name = type + '_spawn'

        self.spawn_name = rf'files\spawn\{type}_ranking.xlsx'
        self.master_df = MasterDBStorage(table_name, to_db=True).df
        self.master_df.fillna("", inplace=True)


        # print(len(self.master_df))
        # self.master_df.drop_duplicates(subset="Part No", keep=False, inplace=True)
        # print(len(self.master_df))
        self.master_df_trimmed = self.master_filter()

        # self.insp_df = MasterDBStorage(insp_name, to_db=True).df
        # self.insp_df.fillna("", inplace=True)

    @show_elapsed_time
    def master_filter(self):
        print('Remaining Parts Before Filtering :', len(self.master_df))

        self.master_df['최종입고일'] = [0 if i == "" else int(i) for i in self.master_df['최종입고일'].tolist()]
        self.master_df['단중'] = [float(i) if i != '' else 0 for i in self.master_df['단중'].tolist()]

        filters = (
                (self.master_df['최종입고일'] >= 20201101)
                # & (self.master_df['단중'] <= 4000)
                & (0 < self.master_df['단중'])
                # & (self.master_df['업체포장여부'] != 1)
                # & (self.master_df['중점검사표유무'] == 1)
                & (self.master_df['거래지속여부'] == 1)
                # & ((self.master_df['포장장명'].str.contains('아산') & self.master_df['중박스코드'].str.startswith('P')) | (
                # self.master_df['포장장명'] == '아산3포장장'))
                & (self.master_df['포장장명'] == '아산3포장장')
        )
        trimmed = self.master_df[filters]
        trimmed.drop_duplicates(subset="Part No", inplace=True)
        print('Remaining Parts After Filtering :', len(trimmed))
        return trimmed

    @show_elapsed_time
    def grouping(self):
        criterion_list = list(filter(lambda x: x.startswith('비전'), self.master_df.columns.tolist()))
        counts = {i: self.master_df[i].sum() for i in criterion_list}
        criterion_list = sorted(criterion_list, key=counts.get, reverse=True)

        grouped_df_1 = self.col_sum(criterion_list, '기준1')
        grouped_df_3 = self.col_sum(criterion_list, '부품체계_3')

        return grouped_df_1, grouped_df_3, self.master_df_trimmed

    def col_sum(self, group, col):
        idx = ['부품체계_1', '부품체계_2', col]
        df = self.master_df.groupby(idx)[group].apply(lambda x: x.astype(float).sum()).reset_index()

        partcate = df[col].tolist()
        partcate_1 = df["부품체계_1"].tolist()
        partcate_2 = df["부품체계_2"].tolist()

        df['비전대상선정'] = ["" for _ in range(len(partcate))]
        # df['품번수'] = self.master_df_trimmed.groupby(idx).size().reset_index(name='counts')['counts'].tolist()

        df['품번수'] = [len(self.master_df_trimmed[(self.master_df_trimmed[col]==i) &
                                                  (self.master_df_trimmed["부품체계_1"]== partcate_1[n]) &
                                                  (self.master_df_trimmed["부품체계_2"] == partcate_2[n])])
                     for n, i in enumerate(partcate)]

        cols = df.columns.tolist()
        popped = [cols.pop(-1)]
        popped_1 = [cols.pop(-1)]
        # popped_2 = [cols.pop(-1)]
        cols = cols[:len(idx)] + popped_1+ popped + cols[len(idx):]
        df = df[cols]

        num_class = [0 for _ in range(len(df))]
        prob_dict = [list() for _ in range(len(df))]

        for n in range(len(num_class)):
             for j in group:
                if df.loc[n, j] > 0:
                    num_class[n] += 1
                    prob_dict[n].append(j)

        # print(prob_dict)
        df['_비전가능불량유형수'] = num_class
        df['_비전가능불량건수'] = df[group].sum(axis=1)
        df['발생불량'] = [' '.join(i).replace('비전_', "") for i in prob_dict]
        df = df.sort_values(["_비전가능불량유형수", "_비전가능불량건수"], ascending=(False, False))
        df = df[df[col] != ""]



        return df


if __name__ == "__main__":

    types = ['exp', 'dom']

    for d_type in types:
        data = RankFilter(d_type)
        grouped_df_1, grouped_df_3, master_df_trimmed = data.grouping()

        with pd.ExcelWriter(rf'files\spawn\{d_type}_ranking.xlsx') as writer:
            master_df_trimmed.to_excel(writer, sheet_name='마스터', index=False)
            grouped_df_1.to_excel(writer, sheet_name='대표부품기준', index=False)
            grouped_df_3.to_excel(writer, sheet_name='부품상세기준', index=False)

        os.startfile(rf'files\spawn\{d_type}_ranking.xlsx')
