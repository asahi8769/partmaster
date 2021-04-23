import pandas as pd
from master_db import MasterDBStorage
import os


def df_edit(d_type):
    """
    불량제목 수기데이터 추가를 위한 데이터 편집 함수
    :param d_type: exp, dom
    :return:
    """
    df = MasterDBStorage(f'{d_type}_spawn', to_db=True).df
    df['data'] = ["해외" if d_type == 'exp' else "국내" for _ in range(len(df))]
    # df['target_기륜책임님'] = ["" for _ in range(len(df))]
    df['target'] = ["" for _ in range(len(df))]
    df['target_2'] = ["" for _ in range(len(df))]
    df['등록'] = ["" for _ in range(len(df))]
    df['발생일자'] = [str(i).split(' ')[0] for i in df['발생일자'].tolist()]

    if d_type == 'exp':
        df['해외결재일'] = [str(i).split(' ')[0] for i in df['해외결재일'].tolist()]
        col = [
            'data', '대표PPR No', 'PPR No', '고객사', '차종', '부품명', 'Part No', '코드', '귀책처', '제목',
            'target', 'target_2', '등록', '해외결재일', '발생일자', '불량구분', '불량유형(대)', '불량유형(중)', '불량유형(소)',
            '담당자', '조치수량'
               ]
    else :
        df['담당자'] = ["" for _ in range(len(df))]
        df['등록'] = ["" for _ in range(len(df))]
        col = [
            'data', '통보서번호', '통보서번호', '고객사', '차종', '부품명', 'Part No', '코드', '업체명', '제목',
            'target', 'target_2', '등록', '등록일자', '발생일자', '불량구분', '대분류명.1', '중분류명.1', '소분류명.1',
            '담당자', '불량수량'
        ]

    return df[col]


def spawn(df):
    df.to_excel('files\spawn\edited_data.xlsx', index=False, encoding='utf-8-sig')
    os.startfile('files\spawn\edited_data.xlsx')


if __name__ == "__main__":
    os.chdir(os.pardir)
    df = df_edit('dom')

    spawn(df)
