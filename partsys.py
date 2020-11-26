import pandas as pd
from collections import Counter
import re, os
from master_db import MasterDBStorage
from utils.config import APPEARANCE_DICT


def part_data():
    with open('files/해외누적_김기륜.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols = "F:H")
        df.sort_values("품명", inplace=True)
        df.drop_duplicates(subset="품번", keep='first', inplace=True)
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.reset_index(inplace=True, drop=True)
    return df


def raw_data():
    with open('files/해외누적_김기륜.xlsx', 'rb') as file:
        df = pd.read_excel(file)
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
    return df


def master_data():
    df = MasterDBStorage('파트마스터').df
    df.rename(columns={'Part No':'품번', '부품명':'품명'}, inplace=True)
    df['품명'] = [i.upper() for i in df['품명'].tolist()]
    return df


def exp_data():
    df = MasterDBStorage('해외불량이력').df
    df.rename(columns={'Part No':'품번', '부품명':'품명'}, inplace=True)
    df['품명'] = [i.upper() for i in df['품명'].tolist()]
    return df


def dom_data():
    df = MasterDBStorage('입고불량이력').df
    df.rename(columns={'Part No':'품번', '부품명':'품명'}, inplace=True)
    df['품명'] = [i.upper() for i in df['품명'].tolist()]
    return df


def partsys_1():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='부품체계1')
    partsys_1_dict = dict(zip([str(i) for i in df['품번'].tolist()], df['부품구분']))
    return partsys_1_dict


def partsys_2():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='부품체계2')
    partsys_2_dict = {str(p): df['부품구분'].tolist()[n] for n, p in enumerate(df['품번'].tolist())}
    return partsys_2_dict


def partsys_search(df, classifier_dict, keylist, filename):
    # syslist = df['품목'].tolist()
    namelist = df['품명'].tolist()
    word_list = []
    fr_list = ["" for _ in namelist]
    word_to_skip = ['RH', 'LH', 'ASSY', 'NO', 'A/S', 'ASY', "ASS'Y", 'FR', 'RR', 'FRONT', 'REAR', 'LHD', 'RHD', 'P/SIDE',
                    'D/SIDE', 'CKD', 'NO.', 'L/R', 'FRT', 'ASSEMBLY', 'STD', 'STDB', 'COMPLETE', 'COMPL']

    for n, i in enumerate(namelist):
        name = re.sub(r"[0-9\xa0\u3000\n]", ' ', re.sub("1ST", ' ', re.sub("2ND", ' ', re.sub("3RD", ' ', i))))
        words = [i for i in name.replace("O-R", "OR").replace("-", " ").replace("+", " ").replace("_", " ").replace(
            ",", " ").replace("(", " ").replace(")", " ").replace("=", " ").replace(".", "").replace(
            " & ", "&").split(' ') if i not in word_to_skip and len(i) > 1]
        word_list.append(words)

    for n, i in enumerate(namelist):
        if 'FR' in i or 'FRONT' in i or 'FRT' in i:
            fr_list[n] = 'FR'
        if 'RR' in i or 'REAR' in i:
            fr_list[n] = 'RR'

    df['품명단어'] = [', '.join(i) for i in word_list]
    df['리어프론트'] = fr_list

    audited = ["" for _ in df['품명단어'].tolist()]
    class_1 = ["" for _ in df['품명단어'].tolist()]
    class_2 = ["" for _ in df['품명단어'].tolist()]
    length = ["" for _ in df['품명단어'].tolist()]
    stage = ["" for _ in df['품명단어'].tolist()]
    for n, i in enumerate(df['품명단어'].tolist()):
        if audited[n] == "":
            for key in keylist:
                if key == i:
                    audited[n] = classifier_dict[key]['정리']+f'({fr_list[n]})' if len(fr_list[n])>0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    length[n] = classifier_dict[key]['품명길이']
                    stage[n] = '[1]일치'
                    break
        if audited[n] == "":
            for key in keylist:
                k_str = ', '.join(key.split(', ')[1:])
                i_str = ', '.join(i.split(', ')[1:])
                if (k_str in i_str or i_str in k_str) and i.split(', ')[0] == key.split(', ')[0]:
                    # print(key, '&', i)
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    length[n] = classifier_dict[key]['품명길이']
                    stage[n] = '[2]포함'
                    break
        if audited[n] == "":
            for key in keylist:
                k_set = set(key.split(', ')[1:])
                i_set = set(i.split(', ')[1:])
                if k_set.issuperset(i_set) and i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    length[n] = classifier_dict[key]['품명길이']
                    stage[n] = '[3]부분'
                    break
        if audited[n] == "":
            for key in keylist:
                if sorted(key.split(', ')) == sorted(i.split(', ')):
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    length[n] = classifier_dict[key]['품명길이']
                    stage[n] = '[4]역순'
                    break
        if audited[n] == "":
            for key in keylist:
                if i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['기준1'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['기준1']
                    class_1[n] = classifier_dict[key]['기준1']
                    length[n] = classifier_dict[key]['품명길이']
                    stage[n] = '[5]대표'
                    break
    df['품명길이'] = length
    df['기준1'] = class_1
    df['기준2'] = class_2
    df['정리'] = audited
    df['사정결과'] = stage

    PART_SYS_1 = partsys_1()
    PART_SYS_2 = partsys_2()

    df['부품체계_1'] = [PART_SYS_1.get(i[0], '') for i in df['품번'].tolist()]
    df['부품체계_2'] = [PART_SYS_2.get(i[0:2], '') for i in df['품번'].tolist()]


    print(Counter(df['사정결과']))
    # print(Counter(df['기준1']))
    print(Counter(df['정리']))

    if filename == "품목구분_2_test":
        df.drop_duplicates(subset=['품명단어'], keep='first', inplace=True)
    df.drop_duplicates(subset=['품번'], keep='first', inplace=True)
    df = df[['품번', '품명', '품명단어', '리어프론트', '기준1', '기준2', '정리', '사정결과', '부품체계_1', '부품체계_2', ]]

    with pd.ExcelWriter(rf'files\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\{filename}.xlsx')


def partsys_3():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='부품체계3')
        df.fillna('', inplace=True)
        df['품명길이'] = [len(df['품명단어'].tolist()[n].split(', ')) for n in range(len(df))]
        df.sort_values("품명길이", inplace=True, ascending=False)

    keylist = df['품명단어'].tolist()
    classifier_dict = {i: {'품명길이': len(df['품명단어'].tolist()[n].split(', ')), '기준1': df['기준1'].tolist()[n],
                           '기준2': df['기준2'].tolist()[n], '정리': df['정리'].tolist()[n]}
                       for n, i in enumerate(df['품명단어'].tolist())}
    return classifier_dict, keylist


def appearance_table():
    key = list(APPEARANCE_DICT.keys())
    values = [', '.join(i) for i in list(APPEARANCE_DICT.values())]
    # print(key)
    # print(values)
    df = pd.DataFrame(list(zip(key, values)), columns =['불량명', '단어'])
    # print(df)
    with pd.ExcelWriter('files\불량구분테이블.xlsx') as writer:
        df.to_excel(writer, sheet_name='불량구분_원본', index=True)

if __name__ == "__main__":
    df = dom_data()
    # df = exp_data()
    classifier_dict, keylist = partsys_3()
    partsys_search(df, classifier_dict, keylist, '품목구분_2_test')
    # partsys_search(df, classifier_dict, keylist, '해외불량품목_5년')
    # appearance_table()