from master_db import MasterDBStorage
from part_search.partsys_search import partsys_3_search
from utils.functions import show_elapsed_time
import pandas as pd


class IncomingFlow:
    def __init__(self):
        self.incoming_df = MasterDBStorage('입고내역조회3개월', to_db=True).df

    @show_elapsed_time
    def _part_type_1_2(self):
        with open('files/품목구분기준.xlsx', 'rb') as file:
            df_1 = pd.read_excel(file, sheet_name='부품체계1')
            df_2 = pd.read_excel(file, sheet_name='부품체계2')
        partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
        partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
        self.incoming_df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in self.incoming_df['Part No'].tolist()]
        self.incoming_df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in self.incoming_df['Part No'].tolist()]

    @show_elapsed_time
    def _part_type_3_4(self):
        partsys_3_search(self.incoming_df)

    @show_elapsed_time
    def pivot_per_partsys(self, col):
        self._part_type_1_2()
        self._part_type_3_4()
        df = self.incoming_df.groupby([col])[['예상케이스']].apply(lambda x: x.astype(float).sum()).reset_index()
        return dict(zip([i for i in df[col]], [int(i) for i in df['예상케이스']]))

    @show_elapsed_time
    def pivot_per_partnum(self):
        df = self.incoming_df.groupby(['Part No'])[['예상케이스']].apply(lambda x: x.astype(float).sum()).reset_index()
        return dict(zip([i for i in df['Part No']], [int(i) for i in df['예상케이스']]))


if __name__ == "__main__":
    import os
    flow_dict = IncomingFlow().pivot_per_partsys('부품체계_3')

    print(flow_dict)



