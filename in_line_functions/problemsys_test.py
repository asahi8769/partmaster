import pandas as pd
from in_line_functions.partsys_3_search import partsys_3_search
import re
from functools import reduce
from collections import Counter


def problem_data():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols = "F, H, K, L, O")
        df.sort_values("불량구분", inplace=True)
        df.rename(columns={'불량구분.1': '대분류', '품번': 'Part No', '품명': '부품명'}, inplace=True)
        df.drop_duplicates(subset="제목", keep='first', inplace=True)
        df['발생빈도'] = [Counter(df['불량구분'].tolist())[i] for i in df['불량구분'].tolist()]
        df.sort_values("발생빈도", inplace=True, ascending=False)
    return df


def partsys_1_2(df):
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df_1 = pd.read_excel(file, sheet_name='부품체계1')
        df_2 = pd.read_excel(file, sheet_name='부품체계2')
    partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
    partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
    df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in df['Part No'].tolist()]
    df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in df['Part No'].tolist()]
    return df


def part_names():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file)
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
    return list(set([i for i in reduce(lambda x, y: x + y, partnames)]))


def pre_processing(df):

    # df_partial = df[df['불량구분'] == name]
    # print(df)
    partnames = part_names()
    partnames += ['코리아오토글라스', 'ASSY', 'KOREA', 'CORPORATION', 'HX', 'RR', 'RH', 'VISUAL', 'DEFECT', 'HCF', 'D&R',
                  'REFER', 'THE', 'SAME', 'APPEARANCE','PROBLEM', 'BDM', 'MOBIS', 'KIMCHEON', 'CV', 'COMPL', 'FR', 'LH',
                  'INFORMATION', 'PART', 'WI', 'VER', 'REWORK', 'FI', 'SURFACE', 'SLH', 'UI', 'PPR', 'TRG', 'NOK',
                  'STAGE', 'DEFECTS', 'WRONG', 'OBSERVED', 'SEATING', 'AREA', 'CONDITION', 'CO', 'FOUND', 'PBBLE',
                  'ISSUES', 'PARTS', 'SEALANT', 'TORQUE', 'IMPRESSION', 'PLAKOR', 'ASAN', 'GX', 'LG',
                  'HAUSYS', 'LTD', 'RRRH', 'LN', 'TMA', '도어벨트', '불량', 'ECOPLASTIC', 'NG', 'SC', 'KIA', 'HANKOOK',
                  'NATIONAL','CN','세방전지', 'STICKER','KAC', 'CLEARLH', 'SRH', 'COMBILAMP', 'YZ','HEADRH','TF',
                  '현대모비스', '김천공장','DL', 'FRT', 'VS', 'AQL','CONTAMINATION', 'SAMBOPLATEC', 'HI', 'TR', 'SAMSONG',
                  'KNIFE','INTERNAL', 'HEADLH', 'RP', 'COMPLETED','IQR','GCE','COMING', 'FROM', 'IS','OF', 'SHIN',
                  'CHROME','에스엘', '주식회사', '진량공장', 'ASSI','BEFORE', 'JULY', 'OLD', 'NO', 'SHOWING', 'BH',
                  'IDENTIFICATION', 'FE', 'COLD', 'TEST', 'RIB', 'COMPLETE', 'HEADLAMP', 'BETWEEM', 'HC', 'NOT',
                  ]

    # print(Counter(df['불량구분'].tolist()))

    revised_title = [i.upper() for i in df['제목'].tolist()]
    revised_title = [re.sub("(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[\t0-9\xa0\u3000\n?!\-+_,/\[\]()=@;.']", ' ', i).upper() for i in revised_title]
    df['제목_1'] = [(', ').join(i) for i in [i.split(' ') for i in revised_title]]
    # single_list = [i for i in reduce(lambda x, y: x + y, revised_title) if i not in partnames and len(i) > 1]
    # print(name)
    # print(Counter(single_list))
    # print(Counter(single_list).keys())

    return df


if __name__ == "__main__":
    import os
    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    df = problem_data()
    df = partsys_1_2(df)
    df = partsys_3_search(df)

    seen = set()
    seen_add = seen.add
    problem_list = [i for i in df['불량구분'].tolist() if not (i in seen or seen_add(i))]
    # print(problem_list)
    #
    # for n, i in enumerate(problem_list):
    #     print(n)
    #     if n < 5 :
    #         try:
    #             df_partial = pre_processing(df, i)
    #         except:
    #             print('passing' , i)
    #     else:
    #         break
    # df = pre_processing(df, '폼누락')

    df = pre_processing(df)
    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')