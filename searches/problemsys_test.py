from searches.problemsys_search import *
from master_db import MasterDBStorage


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


def exp_data():
    df = MasterDBStorage('해외불량이력', append_from_file=True).df
    df['품명'] = [i.upper() for i in df['품명'].tolist()]
    df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
    df.drop_duplicates(subset="Part No", keep='first', inplace=True)
    df.drop_duplicates(subset="부품명", keep='first', inplace=True)
    return df


def dom_data():
    df = MasterDBStorage('입고불량이력',append_from_file=True).df
    df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
    return df


def problem_type_dict():
    with open('files/불량구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='불량구분_1')
        df.fillna('', inplace=True)
        df['불량길이'] = [len(df['제목_1'].tolist()[n].split(', ')) for n in range(len(df))]
        df.sort_values(["불량길이"], inplace=True, ascending=[False])
        key_sequence = df['제목_1'].tolist()
    classifier_dict = {i: {'불량구분': df['불량구분'].tolist()[n]} for n, i in enumerate(key_sequence)}
    key_sequence = remove_duplication(key_sequence)
    return classifier_dict, key_sequence


if __name__ == "__main__":
    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    # df = problem_data()
    df = dom_data()
    df = partsys_1_2(df)
    classifier_dict, key_sequence = problem_type_dict()
    df = problemsys_search(df, classifier_dict, key_sequence)

    problem_list = remove_duplication(df['불량구분'].tolist())
    print(problem_list[40:60])
    print(sum(list(Counter(df['불량구분'].tolist()).values())[0:40]) / len(df))

    df = df[['불량구분', '제목', '부품체계_2', '제목_1', '제목_1_발생빈도', '불량정리', '불량구분결과']]
    df.drop_duplicates(subset="제목_1", keep='first', inplace=True)

    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')


    # ['스크래치', '파손', '오염', '작동불량', '노이즈', '이종', '기포', '크랙', '이물유입', '갭', '서브파트누락', 'DTC불량',
    # '도장이물', '누유', '휨', '칩', '치수불량', '미성형', '수량부족', '찍힘']
    # ['덴트', '패드이탈', '버', '발청', '홀누락', '깨짐', '기공', '누수', '홀위치불량', '핀휨', '서브파트이종', '눌림', '플레이트오조립', '웰드너트위치불량', '바디갭',
    #  '핀홀', '홀치수불량', '주름', '도장기포', '라벨누락']
    # ['이색', '굴곡', '가스켓이탈', '찢어짐', '볼트누락', '사운드작동불가', '커버닫힘불량', '서브파트오조립', '벌브소손', '들뜸', '브라켓누락', '렌즈조정불량', '너트누락',
    #  '패드짧음', '잠김동작불량', '콜드테스트불량', '점등불량', '볼트덜조임', '와셔이탈', '작동속도느림']

    # filter = '이색'
    # filter = None

    # for n, i in enumerate(problem_list):
    #     try:
    #         df_partial = df[df['불량구분'] == i]
    #     except KeyError:
    #         print('passing', i)
    #     else:
    #         if filter is not None and i == filter:
    #             print(i, remove_duplication(df_partial['제목_1'].tolist()))
    #             print(sorted(flatten([i.split(', ') for i in remove_duplication(df_partial['제목_1'].tolist())])))
    #             df = df[df['불량구분'] == filter]

    # df.drop_duplicates(subset="제목_1", keep='first', inplace=True)
    # df.drop_duplicates(subset=['제목_1', '부품체계_2'], keep='first', inplace=True)
    #
    # df = df[['제목', '불량구분', '부품체계_2', '제목_1', '제목_1_발생빈도']]
    # df['불량길이'] = [len(df['제목_1'].tolist()[n].split(', ')) for n in range(len(df))]
    # df.sort_values(["불량길이", "제목_1_발생빈도"], inplace=True, ascending=[False, False])
    #
    # filename = "불량구분결과_test"
    # with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
    #     df.to_excel(writer, sheet_name='품번체계', index=False)
    # os.startfile(rf'files\spawn\{filename}.xlsx')
