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
    words_to_skip = [i for i in part_names()+supplier_names() if i not in
                     ['PAINT', 'DUST', 'SCR', 'MOLDING', 'FUNCTION', 'INJECTION', 'DM', '불량', 'HIGH EFFORT',
                      'COUPLING', 'MECHANISM', 'NOISE', 'PACKING', 'EXTRA', 'POSITION', 'WELD', 'PRESS', 'RUST',
                      'HOLE', 'PIN', 'NUT', 'LEVEL', 'LEATHER', 'STICKER', 'ID']]
    additional_exceptions = ['AA', 'AB', 'ABNORAL', 'ABNORMAL', 'ACCORDING', 'ACID', 'ACTR', 'ACU', 'ACUTATOR', 'AFTER',
                             'ALSO', 'AN', 'ANTEENA', 'ANY', 'APPLICATION', 'AQL', 'ARE', 'AREA', 'ASAN', 'ASHA', 'ASSI',
                             'ASSY', 'AUTOGLASS', 'AUTOMOTIVE', 'AVAILABLE', 'BBD', 'BC', 'BDC', 'BDM', 'BE', 'BEFORE',
                             'BELT', 'BETWEEM', 'BETWEEN', 'BH', 'BJA', 'BJB', 'BJC', 'BMU', 'BOOSTER', 'BOTTOM', 'BQ',
                             'BRCT', 'BRD', 'BRK', 'BSA', 'BUTTONS', 'CA', 'CAME', 'CBR', 'CDC', 'CF', 'CHANG',
                             'CHEMICAL', 'CHNL', 'CHROME', 'CKLIP', 'CLEARLH', 'CLIPEND', 'CLOSING', 'CN', 'CNS', 'CO',
                             'COMBILAMP', 'COMES', 'COMING', 'COMPL', 'COMPLETE', 'CONCERN', 'CONNECTORS',
                             'CORPORATION', 'CRETA', 'CV', 'D&R', 'DAEDONG', 'DENSO', 'DH', 'DISCK', 'DKE', 'DL',
                             'DONG', 'DRRH', 'DUA', 'DUE', 'DURIGN', 'DURING', 'DY', 'ECOPLASTIC', 'ECOS', 'EK',
                             'ELEMENT', 'ENDPIECE', 'FB', 'FC', 'FE', 'FI', 'FM', 'FOUND', 'FPSC', 'FR', 'FROM', 'FRT',
                             'FULLER', 'GCB', 'GCC', 'GCD', 'GCE', 'GCF', 'GE', 'GEARS', 'GI', 'GI', 'GIVING', 'GONG',
                             'GRL', 'GRUME', 'GSK', 'GSR', 'GX', 'HADS', 'HANKOOK', 'HAUSYS', 'HC', 'HCD', 'HCE', 'HCF',
                             'HCG', 'HCR', 'HDLLH', 'HE', 'HEADLAMP', 'HEADLH', 'HEADRH', 'HEE', 'HEMMING', 'HENKEL',
                             'HEUNG', 'HI', 'HING', 'HM', 'HMI', 'HMMC', 'HMSK', 'HOME', 'HTK', 'HX', 'HYUNDAI', 'IL',
                             'ILLUMINATION', 'IMT', 'INCOMING', 'IND', 'INDIA', 'INFAC', 'INFORMATION',
                             'INITIAL', 'INSPECTOR', 'INTERMOBILE', 'INTERNAL', 'IQR', 'IS', 'ISIR', 'ISSUE', 'ISSUES',
                             'IT', 'ITS', 'JIG', 'JIN', 'JNT', 'JOIL', 'JS', 'JULY', 'JUNG', 'JUST', 'KA', 'KAC', 'KF',
                             'KIA', 'KIMCHEON', 'KMS', 'KNIFE', 'KNOBB', 'KOMOS', 'KOREA', 'KWANGJIN', 'KYUNG', 'LANE',
                             'LEFT', 'LG', 'LH', 'LHD', 'LINKAGE', 'LIQUID', 'LN', 'LOADING', 'LOT', 'LOUD', 'LPL',
                             'LS', 'LTD', 'LUG', 'MANDO', 'MDPS', 'METAL', 'MJ', 'MOBIS', 'MODEL', 'MONETARY', 'MTGRH',
                             'MU', 'MULTIPLE', 'NAIL', 'NAJEON', 'NATIONAL', 'NEW', 'NG', 'NO.', 'NOIDA', 'NOTCH', 'NVH',
                             'OB', 'OBSERVED', 'OCCURRED', 'OF', 'OFFSET', 'OK', 'OPERATING', 'OPERATION', 'OPERATOR',
                             'PACKED', 'PADDLE', 'PBBLE', 'PCB', 'PCD', 'PCM', 'PDI', 'PHEV', 'PLAKOR', 'PLATECH',
                             'POONGSUNG', 'PP', 'PPR', 'PRESENTED', 'PRIVATE', 'PROBLEM', 'PROTECTION', 'PRTN', 'PSTN',
                             'PTRH', 'PVT', 'PYUNG', 'QARTER', 'QB', 'QC', 'QRT', 'QUALITY', 'QXI', 'RATTLE', 'REAR',
                             'RECEIVED', 'RECEIVING', 'RECIEVED', 'RECIEVING', 'REFER', 'REISSUE', 'RELATED', 'REPAIR',
                             'REWORK', 'RH', 'RIB', 'ROCS', 'ROOFLH', 'ROTATION', 'RP', 'RR', 'RRDR', 'RRRH', 'RT',
                             'RU', 'SAE', 'SAEDONG', 'SAMBOA', 'SAMBOPLATEC', 'SAME', 'SAMPLE', 'SAMSHIN', 'SAMSONG',
                             'SAN', 'SB', 'SC', 'SEAR', 'SEATBELT', 'SEATING', 'SECOND', 'SEEM', 'SENDER', 'SEOYON',
                             'SEQUENCING', 'SEUN', 'SHIFTING', 'SHIN', 'SHINKI', 'SHLD', 'SHOWING', 'SIDELH', 'SL',
                             'SLH', 'SORTED', 'SOS', 'SPOOL', 'SQUEAK', 'SRH', 'SSUNGLASS', 'STAGE', 'STD', 'STICK',
                             'STUDBOLT', 'SUBCONTRACT', 'SUNG', 'SUNGLASS', 'SUNGLASSED', 'SUNGLASSES',
                             'SUPPLIER', 'SUV', 'SVG', 'TACHOMETER', 'TAE', 'TCU', 'TECH', 'TENSR', 'TERMINAL', 'TF',
                             'THAN', 'THE', 'THERE', 'THORTTLE', 'TL', 'TLI', 'TMA', 'KWANGIL', 'INNOVATION', 'UMA',
                             'TOO', 'TR', 'TRANIT', 'TRANS', 'TRANSYS', 'TRG', 'TRIGO', 'TRW', 'TTX', 'TURNS', 'UI',
                             'UIP', 'UNIV', 'UNUSED', 'USED', 'VER', 'VIBRACOUSTIC', 'VISIBLE', 'VISUAL', 'VS', 'WAS',
                             'WEBASTO', 'WHEN', 'WHILE', 'WHISTLE', 'WI', 'WIA', 'WILL', 'WIRRING', 'WON', 'WOO',
                             'YOUNGSAN', 'YPI', 'YZ', 'КК''나전', '도어벨트', '만도', '스트라이커외', '오송', '으로', '인한',
                             'COMPRESSION', 'MTNG', 'BORE', 'VR', 'HOT', 'STAPLE', 'BULB','SEJIN', 'DELTARH', 'DRLH',
                             'JO', 'KMI', 'ACN', 'SAMBO', 'ILJIN', 'HLLD', 'JOYSON', 'SYSTEMS', 'YP', 'REPORT', 'QL',
                             'GAT', 'HCC', 'POLYURETHANE', 'CHE', 'JF', 'КК', 'WERE', 'REJECTED',]
    words_to_skip += additional_exceptions
    print("Filtering :", len(words_to_skip))

    revised_title = [i.upper() for i in df['제목'].tolist()]
    word_list = []
    for i, n in enumerate(revised_title):
        name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
            "SUB PART PROBLEM","SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
            "PRESSURE", "압력").replace("NOT FIXED", "SUBPART").replace("NOT FIT", "UNFITTING").replace(
            "갭", "GAP").replace("MARKS", "마크").replace("MARK", "마크").replace("WELDING/PRESS", "웰딩/프레스").replace(
            "WELD LINE", "WELDLINE").replace("홀", "HOLE")
        name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_]|[\W]", ' ', name)
        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

    df['제목_1'] = [', '.join(i) for i in word_list]
    df['제목_1_발생빈도'] = [Counter(df['제목_1'].tolist())[i] for i in df['제목_1'].tolist()]
    df.sort_values(["발생빈도", "불량구분", "제목_1_발생빈도"], inplace=True, ascending=[False, True, False])
    return df


if __name__ == "__main__":
    import os

    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    df = problem_data()
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

    df.drop_duplicates(subset="제목_1", keep='first', inplace=True)

    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')
