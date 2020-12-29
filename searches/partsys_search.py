import re, pickle
import pandas as pd
from collections import Counter


def part_type_3_dict():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='부품체계3')
        df.fillna('', inplace=True)

        df['품명길이'] = [len(df['품명단어'].tolist()[n].split(', ')) for n in range(len(df))]
        df.sort_values("품명길이", inplace=True, ascending=False)
        key_sequence = df['품명단어'].tolist()

    classifier_dict = {i: {'품명길이': df['품명길이'].tolist()[n], '기준1': df['기준1'].tolist()[n],
                           '기준2': df['기준2'].tolist()[n], '정리': df['정리'].tolist()[n]}
                       for n, i in enumerate(key_sequence)}
    return classifier_dict, key_sequence


def preprocess(df, namelist):
    word_list = []
    fr_list = ["" for _ in namelist]
    words_to_skip = ['RH', 'LH', 'ASSY', 'NO', 'A/S', 'ASY', 'LHD', 'RHD', 'CKD', 'L/R', 'ASSEMBLY', 'STD', 'BUS'
                     'STDB', 'COMPLETE', 'COMPL', 'ASSSY', 'QL', 'QLE', 'TL', 'TLE', 'TLZ', 'AT', 'A/T', 'MT', 'M/T',
                     'PD', 'PDE', 'SL', 'SLE', 'TL', 'TLE', 'QY', 'SPORTAGE', 'SONATA', 'LF', 'ACCENT', 'HYUNDAI', 'KIA',
                     'RIO', 'TUCSON', 'SOLATI', 'KD', 'ASM', 'TL/QL', 'CEED', 'FORTE', 'LIMITED', 'CRETA', 'SANTAFE',
                     'SOLARIS', 'ELANTRA', 'COMPT', 'FR', 'RR', 'FRONT', 'FRT', 'REAR', 'COMPLT', "NX", "SC", "IQP", "LSU",
                     "SLZ", "IP", "FT", "PE", "GB", "YP", "TRK", "BUS"]

    for n, i in enumerate(namelist):
        name = i.replace("O-R", "OR").replace(" & ", "&").replace("O2", "OXYGEN").replace("'", "").replace("’", "").replace("`", "").replace(".", "")
        name = re.sub("(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9\xa0\u3000\n?!\-+_,()=]", ' ', name)
        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

        if 'FR' in i or 'FRONT' in i or 'FRT' in i:
            fr_list[n] = 'FR'
        elif 'RR' in i or 'REAR' in i:
            fr_list[n] = 'RR'

    df['품명단어'] = [', '.join(i) for i in word_list]
    df['리어프론트'] = fr_list
    # print(fr_list)
    return df


def partsys_3_search(df):
    classifier_dict, key_sequence = part_type_3_dict()
    namelist = [i.upper() for i in df['부품명'].tolist()]
    df = preprocess(df, namelist)

    fr_list = df['리어프론트'].tolist()
    # print(fr_list)

    audited = ["" for _ in namelist]
    class_1 = ["" for _ in namelist]
    class_2 = ["" for _ in namelist]
    class_3 = ["" for _ in namelist]
    length_ = ["" for _ in namelist]
    stage__ = ["" for _ in namelist]
    for n, i in enumerate(df['품명단어'].tolist()):
        # if n % 1000 == 0: print(n)
        if audited[n] == "":
            for key in key_sequence:
                if key == i:
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[1]일치'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if set(key.split(', ')) == set(i.split(', ')):
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[2]역순'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if len(key.split(', ')) >= 3 and len(i.split(', ')) >= 3 and set(key.split(', ')[0:3]) == set(
                        i.split(', ')[0:3]):
                    # print(key, '&', i)
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[3]부분_3'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if len(key.split(', ')) >= 2 and len(i.split(', ')) >= 2 and key.split(', ')[0:2] == i.split(', ')[0:2]:
                    # print(key, '&', i)
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[4]부분_2'
                    break
        if audited[n] == "":
            for key in key_sequence:
                k_str = ', '.join(key.split(', ')[1:])
                i_str = ', '.join(i.split(', ')[1:])
                if (k_str in i_str or i_str in k_str) and i.split(', ')[0] == key.split(', ')[0]:
                    # print(key, '&', i)
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[5]포함'
                    break
        if audited[n] == "":
            for key in key_sequence:
                k_set = set(key.split(', ')[1:])
                i_set = set(i.split(', ')[1:])
                if (k_set.issuperset(i_set) or k_set.issuperset(i_set)) and i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[6]교차'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['기준1'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['기준1']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_3[n] = classifier_dict[key]['정리']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[7]대표'
                    break
    df['품명길이'] = length_
    df['기준1'] = class_1
    df['기준2'] = class_2
    df['부품체계_3'] = class_3
    df['부품체계_4'] = audited
    df['사정결과'] = stage__


    print(Counter(df['사정결과']))
    # print(Counter(df['기준1']))
    # print(Counter(df['정리']))
    return df


if __name__ == "__main__":
    from master_db import MasterDBStorage
    import os

    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))


    def load_wpcdict():
        try :
            with open('files/spawn/wpc_part.pkl', 'rb') as file:
                wpc_dict = pickle.load(file)
            return wpc_dict
        except FileNotFoundError:
            return dict()


    def master_data():
        df = MasterDBStorage('파트마스터', append_from_file=True).df
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.drop_duplicates(subset="품번", keep='first', inplace=True)
        df.drop_duplicates(subset="품명", keep='first', inplace=True)
        return df


    def exp_data():
        df = MasterDBStorage('해외불량이력', append_from_file=True).df
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
        df.drop_duplicates(subset="Part No", keep='first', inplace=True)
        df.drop_duplicates(subset="부품명", keep='first', inplace=True)
        return df


    def dom_data():
        df = MasterDBStorage('입고불량이력', append_from_file=True).df
        df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
        return df

    # df = master_data()
    df = dom_data()
    # df = exp_data()
    df['Part No'] = [i.replace(" ", "").replace("-", "") for i in df['Part No'].tolist()]
    df['Part No'] = [i[0:10] for i in df['Part No'].tolist()]
    df.drop_duplicates(subset="Part No", keep='first', inplace=True)

    classifier_dict, keylist = part_type_3_dict()
    df = partsys_3_search(df)
    wpc_dict = load_wpcdict()
    # print(wpc_dict)

    with open('files/품목구분기준.xlsx', 'rb') as file:
        df_1 = pd.read_excel(file, sheet_name='부품체계1')
        df_2 = pd.read_excel(file, sheet_name='부품체계2')
    partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
    partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
    df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in df['Part No'].tolist()]
    df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in df['Part No'].tolist()]
    df['wpc_10'] = [wpc_dict.get(i, "") for i in df['Part No'].tolist()]
    df['wpc_6'] = [wpc_dict.get(i[:6], "") for i in df['Part No'].tolist()]
    # print(wpc_dict['0K2KB688H1'])

    df = df[['Part No', '부품명', '품명단어', '기준1', '기준2', '부품체계_3', '부품체계_4', '사정결과', '부품체계_1', '부품체계_2',
             'wpc_10', 'wpc_6']]

    filename = "품목구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.drop_duplicates(subset="품명단어", keep='first', inplace=True)
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')