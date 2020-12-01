import re
import pandas as pd


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
    word_to_skip = ['RH', 'LH', 'ASSY', 'NO', 'A/S', 'ASY', "ASS'Y", 'FR', 'RR', 'FRONT', 'REAR', 'LHD', 'RHD', 'P/SIDE',
                    'D/SIDE', 'CKD', 'NO.', 'L/R', 'FRT', 'ASSEMBLY', 'STD', 'STDB', 'COMPLETE', 'COMPL', 'ASSSY', 'QL',
                    'QLE', 'TL', 'TLE', 'TLZ', 'AT', 'A/T', 'MT', 'M/T', 'PD', 'PDE', 'SL', 'SLE', 'TL', 'TLE']
    word_list = []

    for n, i in enumerate(namelist):
        name = re.sub("[0-9\xa0\u3000\n?!\-+_,()=]", ' ', re.sub("[0-9][A-Z]{2}[$\s,.\-_]", ' ', re.sub(
            "(NO)(\.)[0-9]+", ' ', re.sub("(O2)", 'OXYGEN', i))))

        words = [i for i in name.replace("O-R", "OR").replace(".", "").replace(" & ", "&").replace("'", "").split(
            ' ') if i not in word_to_skip and len(i) > 1]

        word_list.append(words)
    df['품명단어'] = [', '.join(i) for i in word_list]


def fr_process(df, namelist):
    fr_list = ["" for _ in namelist]
    for n, i in enumerate(namelist):
        if 'FR' in i or 'FRONT' in i or 'FRT' in i:
            fr_list[n] = 'FR'
        if 'RR' in i or 'REAR' in i:
            fr_list[n] = 'RR'
    df['리어프론트'] = fr_list
    return fr_list


def partsys_3_search(df):
    classifier_dict, key_sequence = part_type_3_dict
    namelist = [i.upper() for i in df['부품명'].tolist()]
    preprocess(df, namelist)
    fr_list = fr_process(df, namelist)

    audited = ["" for _ in namelist]
    class_1 = ["" for _ in namelist]
    class_2 = ["" for _ in namelist]
    length_ = ["" for _ in namelist]
    stage__ = ["" for _ in namelist]
    for n, i in enumerate(df['품명단어'].tolist()):
        if n % 1000 == 0: print(n)
        if audited[n] == "":
            for key in key_sequence:
                if key == i:
                    audited[n] = classifier_dict[key]['정리'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['정리']
                    class_1[n] = classifier_dict[key]['기준1']
                    class_2[n] = classifier_dict[key]['기준2']
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
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[6]교차'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['기준1'] + f'({fr_list[n]})' if len(fr_list[n]) > 0 else \
                        classifier_dict[key]['기준1']
                    class_1[n] = classifier_dict[key]['기준1']
                    length_[n] = classifier_dict[key]['품명길이']
                    stage__[n] = '[7]대표'
                    break
    df['품명길이'] = length_
    df['기준1'] = class_1
    df['기준2'] = class_2
    df['부품체계_3'] = audited
    df['사정결과'] = stage__
