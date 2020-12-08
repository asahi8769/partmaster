import pandas as pd
from in_line_functions.partsys_3_search import partsys_3_search
import re
from collections import Counter
from utils.functions import flatten, remove_duplication
from in_line_functions.config import words_not_to_skip, additional_exceptions


def problem_data():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols="B:C, F, H, K, L, O")
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
        df = pd.read_excel(file, usecols="B:C, F, H, K, L, O")
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
    return flatten(partnames)


def supplier_names():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols="I:J")
        codes = remove_duplication(df['코드'].tolist())
        names = remove_duplication(flatten(
            [str(i).upper().replace('(주)', " ").replace('(유)', " ").replace('(', " ").replace(')', " ").split(' ') for i
             in df['귀책처'].tolist()]))
        names = [i for i in names if len(i) > 0]
    return codes + names


def pre_processing(df):
    words_to_skip = [i for i in part_names()+supplier_names() if i not in words_not_to_skip]
    words_to_skip += additional_exceptions
    print("Filtering :", len(words_to_skip))

    revised_title = [i.upper() for i in df['제목'].tolist()]
    word_list = []
    for i, n in enumerate(revised_title):
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
    df.sort_values(["발생빈도", "불량구분", "제목_1_발생빈도"], inplace=True, ascending=[False, True, False])
    return df


if __name__ == "__main__":
    import os
    from master_db import MasterDBStorage

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

    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    # df = problem_data()
    df = dom_data()
    df = partsys_1_2(df)
    df = partsys_3_search(df)

    problem_list = remove_duplication(df['불량구분'].tolist())
    print(problem_list[40:60])
    df = pre_processing(df)
    print(sum(list(Counter(df['불량구분'].tolist()).values())[0:40]) / len(df))


    # ['스크래치', '파손', '오염', '작동불량', '노이즈', '이종', '기포', '크랙', '이물유입', '갭', '서브파트누락', 'DTC불량',
    # '도장이물', '누유', '휨', '칩', '치수불량', '미성형', '수량부족', '찍힘']
    # ['덴트', '패드이탈', '버', '발청', '홀누락', '깨짐', '기공', '누수', '홀위치불량', '핀휨', '서브파트이종', '눌림', '플레이트오조립', '웰드너트위치불량', '바디갭',
    #  '핀홀', '홀치수불량', '주름', '도장기포', '라벨누락']
    # ['이색', '굴곡', '가스켓이탈', '찢어짐', '볼트누락', '사운드작동불가', '커버닫힘불량', '서브파트오조립', '벌브소손', '들뜸', '브라켓누락', '렌즈조정불량', '너트누락',
    #  '패드짧음', '잠김동작불량', '콜드테스트불량', '점등불량', '볼트덜조임', '와셔이탈', '작동속도느림']

    # filter = '이색'
    filter = None

    for n, i in enumerate(problem_list):
        try:
            df_partial = df[df['불량구분'] == i]
        except KeyError:
            print('passing', i)
        else:
            if filter is not None and i == filter:
                print(i, remove_duplication(df_partial['제목_1'].tolist()))
                print(sorted(flatten([i.split(', ') for i in remove_duplication(df_partial['제목_1'].tolist())])))
                df = df[df['불량구분'] == filter]

    # df.drop_duplicates(subset="제목_1", keep='first', inplace=True)
    df.drop_duplicates(subset=['제목_1', '부품체계_2'], keep='first', inplace=True)

    df = df[['제목', '불량구분', '부품체계_2', '제목_1', '제목_1_발생빈도']]
    df['불량길이'] = [len(df['제목_1'].tolist()[n].split(', ')) for n in range(len(df))]
    df.sort_values(["불량길이", "제목_1_발생빈도"], inplace=True, ascending=[False, False])

    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')
