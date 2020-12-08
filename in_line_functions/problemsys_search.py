import pandas as pd
from utils.functions import flatten, remove_duplication
import os, re
import pickle
from collections import Counter
from in_line_functions.config import words_not_to_skip, additional_exceptions


def problem_type_dict():
    with open('files/불량구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='불량구분_1')
        df.fillna('', inplace=True)
        df['불량길이'] = [len(df['제목_1'].tolist()[n].split(', ')) for n in range(len(df))]
        df.sort_values(["불량길이", "제목_1_발생빈도"], inplace=True, ascending=[False, False])
        key_sequence = df['제목_1'].tolist()

    classifier_dict = {
        i: {'불량구분': df['불량구분'].tolist()[n], '부품체계': remove_duplication(df[df['불량구분']==df['불량구분'].tolist()[n]]['부품체계_2'].tolist())}
        for n, i in enumerate(key_sequence)}
    key_sequence = remove_duplication(key_sequence)
    return classifier_dict, key_sequence


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
    return part_list, supplier_list


def pre_processing(df, title):
    part_list, supplier_list = get_basic_filters()
    words_to_skip = [i for i in part_list + supplier_list if i not in words_not_to_skip]
    words_to_skip += additional_exceptions
    print("Filtering :", len(words_to_skip))

    word_list = []
    for i, n in enumerate(title):
        name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
            "SUB PART PROBLEM","SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
            "PRESSURE", "압력").replace("NOT FIXED", "SUBPART").replace("FITTING", "FIT").replace("FITTED", "FIT").replace(
            "NOT FIT", "UNFITTING").replace("BAD FIT", "UNFITTING").replace("갭", "GAP").replace("MARKS", "마크").replace(
            "MARK", "마크").replace("WELDING/PRESS", "웰딩/프레스").replace("WELD LINE", "WELDLINE").replace(
            "홀", "HOLE").replace("BAR CODE", "BARCODE")
        name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_]|[\W]", ' ', name)
        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

    df['제목_1'] = [', '.join(i) for i in word_list]
    df['제목_1_발생빈도'] = [Counter(df['제목_1'].tolist())[i] for i in df['제목_1'].tolist()]
    # df.sort_values(["발생빈도", "불량구분", "제목_1_발생빈도"], inplace=True, ascending=[False, True, False])
    return df


def partsys_3_search(df):
    classifier_dict, key_sequence = problem_type_dict()
    key_sequence = remove_duplication(key_sequence)
    title = [i.upper() for i in df['제목'].tolist()]
    df = pre_processing(df, title)

    audited = ["" for _ in title]
    stage__ = ["" for _ in title]

    for n, i in enumerate(df['제목_1'].tolist()):
        if audited[n] == "":
            for key in key_sequence:
                if key == i:
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[1]일치'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if set(key.split(', ')) == set(i.split(', ')):
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[2]역순'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if len(key.split(', ')) >= 3 and len(i.split(', ')) >= 3 and set(key.split(', ')[0:3]) == set(
                        i.split(', ')[0:3]):
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[3]부분_3'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if len(key.split(', ')) >= 2 and len(i.split(', ')) >= 2 and key.split(', ')[0:2] == i.split(', ')[0:2]:
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[4]부분_2'
                    break
        if audited[n] == "":
            for key in key_sequence:
                k_str = ', '.join(key.split(', ')[1:])
                i_str = ', '.join(i.split(', ')[1:])
                if (k_str in i_str or i_str in k_str) and i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[5]포함'
                    break
        if audited[n] == "":
            for key in key_sequence:
                k_set = set(key.split(', ')[1:])
                i_set = set(i.split(', ')[1:])
                if (k_set.issuperset(i_set) or k_set.issuperset(i_set)) and i.split(', ')[0] == key.split(', ')[0]:
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[6]교차'
                    break
        if audited[n] == "":
            for key in key_sequence:
                if i in key or key in i:
                    audited[n] = classifier_dict[key]['불량구분']
                    stage__[n] = '[7]추정'
                    break

    df['불량정리'] = audited
    df['불량구분결과'] = stage__
    print(Counter(df['불량구분결과']))
    return df


if __name__ == "__main__":
    from master_db import MasterDBStorage
    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    def exp_data():
        df = MasterDBStorage('해외불량이력').df
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
        df.drop_duplicates(subset="Part No", keep='first', inplace=True)
        df.drop_duplicates(subset="부품명", keep='first', inplace=True)
        return df


    def dom_data():
        df = MasterDBStorage('입고불량이력').df
        df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
        return df

    # df = exp_data()
    df = dom_data()

    df = partsys_3_search(df)

    with open('files/품목구분기준.xlsx', 'rb') as file:
        df_1 = pd.read_excel(file, sheet_name='부품체계1')
        df_2 = pd.read_excel(file, sheet_name='부품체계2')
    partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
    partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
    df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in df['Part No'].tolist()]
    df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in df['Part No'].tolist()]

    filename = "불량구분결과_test"

    df = df[['제목', '불량구분', '부품체계_2', '제목_1', '제목_1_발생빈도', '불량정리', '불량구분결과']]
    df_ = df[df['불량정리'] == ""]
    print(sorted([i for i in remove_duplication(flatten([i.split(', ') for i in df_['제목_1'].tolist()])) if len(i)==3]))
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')
