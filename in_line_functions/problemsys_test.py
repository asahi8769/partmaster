import pandas as pd
from in_line_functions.partsys_3_search import partsys_3_search
import re
from functools import reduce
from collections import Counter
from utils.functions import flatten, remove_duplication


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
        df = pd.read_excel(file, usecols="I:J")
        codes = remove_duplication(df['코드'].tolist())
        names = remove_duplication([i.replace('(주)', " ").split(' ') for i in df['코드'].tolist() if len(i)>0])
    return codes + names


def supplier_names():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file)
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
    return flatten(partnames)


def pre_processing(df):
    words_to_skip = [i for i in part_names() if i not in
                     ['PAINT', 'DUST', 'SCR', 'MOLDING', 'FUNCTION', 'INJECTION', 'DM', '불량', 'HIGH EFFORT',
                      'COUPLING', 'MECHANISM', 'NOISE', 'PACKING', 'EXTRA', 'POSITION']]
    words_to_skip += supplier_names()
    print(words_to_skip)
    words_to_skip += ['코리아오토글라스', 'ASSY', 'KOREA', 'CORPORATION', 'HX', 'RR', 'RH', 'VISUAL', 'HCF', 'D&R',
                      'REFER', 'THE', 'SAME', 'PROBLEM', 'BDM', 'MOBIS', 'KIMCHEON', 'CV', 'COMPL', 'FR', 'LH',
                      'INFORMATION', 'WI', 'VER', 'REWORK', 'FI', 'SLH', 'UI', 'PPR', 'TRG',
                      'STAGE', 'OBSERVED', 'SEATING', 'AREA', 'CO', 'FOUND', 'PBBLE', 'CA',
                      'ISSUES', 'IMPRESSION', 'PLAKOR', 'ASAN', 'GX', 'LG', 'HAUSYS', 'LTD', 'RRRH', 'LN', 'TMA',
                      '도어벨트', 'ECOPLASTIC', 'SC', 'KIA', 'HANKOOK', 'HMSK', 'HM', 'LHD', 'TRANIT',
                      'NATIONAL', 'CN', '세방전지', 'STICKER', 'KAC', 'CLEARLH', 'SRH', 'COMBILAMP', 'YZ', 'HEADRH', 'TF',
                      '현대모비스', '김천공장', 'DL', 'FRT', 'VS', 'AQL', 'SAMBOPLATEC', 'HI', 'TR', 'SAMSONG',
                      'KNIFE', 'INTERNAL', 'HEADLH', 'RP', 'IQR', 'GCE', 'COMING', 'FROM', 'IS', 'OF', 'SHIN',
                      'CHROME', '에스엘', '주식회사', '진량공장', 'ASSI', 'BEFORE', 'JULY', 'NO', 'SHOWING', 'BH',
                      'FE', 'RIB', 'COMPLETE', 'HEADLAMP', 'BETWEEM', 'HC', 'BJC', 'BJA', 'GSK', 'GI',
                      'BJB', 'UNIV', 'JNT', 'LUG', 'PRTN', 'CKLIP', 'WAS', 'QRT', 'EK', 'PDI', 'KNOBB', 'CHNL', 'OFFSET',
                      'GE', 'VIBRACOUSTIC', 'NOIDA', 'PRIVATE', 'INDIA', 'BRCT', 'HCG', 'QC', 'DH', 'REAR',
                      'HMI', 'TLI', 'HING', 'RRDR', 'ACTR', 'NAJEON', 'КК', 'SPOOL', 'HYUNDAI', 'CONCERN', 'GI', 'BELT',
                      'SIDELH', 'FM', 'PLATECH', 'QARTER', 'SUV', 'GCF', 'RECIEVING', 'RU', 'WIRRING', 'CONNECTORS',
                      'TL', 'SL', 'INCOMING', 'VISIBLE', 'STUDBOLT', 'WOO', 'ISSUE', 'DISCK', 'METAL',
                      'PACKED', 'SUPPLIER', 'PYUNG', 'JUNG', 'GONG','TERMINAL', 'NAIL', 'DUE', 'SAE', 'DONG', 'SUNG',
                      'IND', 'PTRH', 'ENDPIECE', 'HEMMING', 'SEQUENCING', 'MONETARY','AUTOGLASS', 'AVAILABLE','CHEMICAL',
                      'DENSO', 'DM', 'FC', 'HENKEL', 'MULTIPLE', 'OPERATOR', 'POONGSUNG', 'SAEDONG', 'SAMSHIN', 'SEAR',
                      'SEUN', 'WON', '나전', 'PROTECTION', 'AB', 'AFTER', 'ALSO', 'ASHA', 'AUTOMOTIVE', 'BBD',
                      'BE', 'BMU', 'BOOSTER', 'BSA', 'BUTTONS', 'CBR', 'CDC', 'CNS','DAEDONG', 'GEARS', 'GIVING', 'HE',
                      'HEUNG', 'HOME', 'IL', 'ILLUMINATION', 'INFAC', 'INSPECTOR','IT', 'ITS', 'JUST', 'KF', 'KWANGJIN',
                      'LANE','LPL', 'LS','PHEV','PP','PSTN', 'QB','SECOND', 'SEEM', 'SEOYON', 'SOS', 'SSUNGLASS',
                      'SUBCONTRACT', 'LIQUID', 'ECOS', 'OK', '일흥','AN','CHANG','COMES','ELEMENT','HEE', 'HMMC',
                      'SUNGLASS', 'SUNGLASSED', 'SUNGLASSES', 'SVG', 'TACHOMETER', 'TCU', 'TRANS','REISSUE',
                      'UIP', 'WHEN', 'WILL', 'KA', 'KYUNG', 'LINKAGE', 'MDPS','WEBASTO', 'WHILE', 'PCB', 'PRESENTED',
                      'ABNORMAL', 'SHLD', 'ABNORAL', 'DURING', 'NVH', 'OPERATING', 'OPERATION', 'PADDLE',
                      'STICK', 'RELATED', 'TENSR', 'THERE', 'TRANSYS', 'TURNS', 'WHISTLE', 'LOUD', 'RATTLE', 'ROTATION',
                      'SHIFTING','SQUEAK','세동', '스트라이커외', '오송','인알파코리아', '인지디스플레이','평화정공', '현담산업',
                      'BDC', 'FB', 'FULLER', 'HCR', 'HDLLH', 'INITIAL', 'KMS','MANDO','MODEL','NEW','PVT', 'QUALITY',
                      'RECEIVED', 'RECEIVING', 'RECIEVED', 'RT', 'SAMBOA', 'SENDER','UNUSED', 'USED','WIA','경주공장',
                      'YOUNGSAN', '경창산업','삼보에이앤티','MU','CLIPEND','GCD', 'GRUME', 'REPAIR', 'ROOFLH', 'SAN',
                      'CAME', 'HCE', 'LEFT', 'APPLICATION','BQ','DURIGN','GCB','GSR', 'JIN', 'MTGRH', 'QXI', 'SB',
                      'SEATBELT','YPI','BC', 'BETWEEN', 'ANTEENA', 'JS', 'MJ', 'CRETA', 'PCD', 'HADS', 'AA', 'BRD', 'BRK',
                      'NOTCH', 'OB', 'OCCURRED','ROCS','THREAD', 'THREADED', 'THREADS', 'FPSC', '만도', '익산공장', '인한',
                      '으로', 'CLOSING', 'HCD', 'HTK','ACID','ARE', 'SORTED', 'TRIGO', 'ACUTATOR', 'ANY','ACU', 'PCM',
                      'THORTTLE', 'DKE', 'GCC', 'INTERMOBILE', 'JOIL', 'SHINKI', 'TAE', 'TECH','DUA', '선일다이파스',
                      '코리아에프티', 'LOADING', 'JIG','ACCORDING', 'CF', 'DRRH', 'ISIR', 'SAMPLE', 'THAN', 'TOO', 'LOT',
                      'TRW', 'DY', 'GRL', 'STD', 'TTX', '삼진정공', '에코플라스틱', '엘지하우시스', '포승공장', 'IMT', 'KOMOS',
                      'BOTTOM']

    # print(Counter(df['불량구분'].tolist()))

    revised_title = [i.upper() for i in df['제목'].tolist()]
    word_list = []
    for i, n in enumerate(revised_title):
        name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace("SUB PART PROBLEM", "SUBPART").replace(
            "PARTS", "PART").replace("으로", "").replace("PRESSURE", "압력").replace("OIL LEAK", "누유").replace(
            "WATER LEAK", "누수").replace("NOT FIXED", "SUBPART").replace("NOT FIT", "NOT FIT").replace(
            "갭", "GAP").replace("MARK", "마크")
        name = re.sub("(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[\t0-9\xa0\u3000\n?!\-+_,/\[\]()=@;.'&:-]|[\W]", ' ', name)
        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

    df['제목_1'] = [', '.join(i) for i in word_list]
    df['제목_1_발생빈도'] = [Counter(df['제목_1'].tolist())[i] for i in df['제목_1'].tolist()]
    # df.sort_values("제목_1_발생빈도", inplace=True, ascending=False)
    df.sort_values(["발생빈도", "불량구분", "제목_1_발생빈도"], inplace=True, ascending=[False, True, False])
    return df


if __name__ == "__main__":
    import os

    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    df = problem_data()
    df = partsys_1_2(df)
    df = partsys_3_search(df)

    # problem_list = df['불량구분'].tolist()
    problem_list = remove_duplication(df['불량구분'].tolist())
    print(problem_list[:20])
    df = pre_processing(df)
    # print(Counter(df['불량구분'].tolist()))
    print(sum(list(Counter(df['불량구분'].tolist()).values())[0:20])/len(df))
    # print(Counter(df['불량구분'].tolist()).values()[0:20])/len(df))

    # ['스크래치', '파손', '오염', '작동불량', '노이즈', '이종', '기포', '크랙', '이물유입', '갭', '서브파트누락', 'DTC불량',
    # '도장이물', '누유', '휨', '칩', '치수불량', '미성형', '수량부족', '찍힘']
    filter = '찍힘'

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

    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')
