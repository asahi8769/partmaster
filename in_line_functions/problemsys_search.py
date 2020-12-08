import pandas as pd
from utils.functions import flatten, remove_duplication
from master_db import MasterDBStorage
import os, re
import pickle
from collections import Counter


def problem_type_dict():
    with open('files/불량구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, sheet_name='불량구분_1')
        df.fillna('', inplace=True)
        df['불량길이'] = [len(df['제목_1'].tolist()[n].split(', ')) for n in range(len(df))]
        key_sequence = df['제목_1'].tolist()

    classifier_dict = {
        i: {'불량구분': df['불량구분'].tolist()[n], '부품체계': remove_duplication(df[df['불량구분']==df['불량구분'].tolist()[n]]['부품체계_2'].tolist())}
        for n, i in enumerate(key_sequence)}
    return classifier_dict, key_sequence


def part_names():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols="B:C, F, H, K, L, O")
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
        partnames = flatten(partnames)
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


def pre_processing(df, revised_title):
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

    words_to_skip = [i for i in part_list + supplier_list if i not in
                     ['PAINT', 'DUST', 'SCR', 'MOLDING', 'FUNCTION', 'INJECTION', 'DM', '불량', 'HIGH EFFORT',
                      'COUPLING', 'MECHANISM', 'NOISE', 'PACKING', 'EXTRA', 'POSITION', 'WELD', 'PRESS', 'RUST',
                      'HOLE', 'PIN', 'NUT', 'LEVEL', 'LEATHER', 'STICKER', 'ID', 'OPEN']]
    additional_exceptions = ['AA', 'AB', 'ABNORAL', 'ABNORMAL', 'ACCORDING', 'ACID', 'ACTR', 'ACU', 'ACUTATOR', 'AFTER',
                             'ALSO', 'AN', 'ANTEENA', 'ANY', 'APPLICATION', 'AQL', 'ARE', 'AREA', 'ASAN', 'ASHA',
                             'ASSI','KMI', 'ACN', 'SAMBO', 'ILJIN', 'HLLD', 'JOYSON', 'SYSTEMS', 'YP', 'REPORT', 'QL',
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
                             'MU', 'MULTIPLE', 'NAIL', 'NAJEON', 'NATIONAL', 'NEW', 'NG', 'NO.', 'NOIDA', 'NOTCH',
                             'NVH', 'GAT', 'HCC', 'POLYURETHANE', 'CHE', 'JF', 'КК', 'WERE', 'REJECTED',
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
                             'COMPRESSION', 'MTNG', 'BORE', 'VR', 'HOT', 'STAPLE', 'BULB', 'SEJIN', 'DELTARH', 'DRLH',
                             'JO']
    words_to_skip += additional_exceptions
    print("Filtering :", len(words_to_skip))

    word_list = []
    for i, n in enumerate(revised_title):
        name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
            "SUB PART PROBLEM", "SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
            "PRESSURE", "압력").replace("NOT FIXED", "UNFIXED").replace("FITTING", "FIT").replace("FITTED", "FIT").replace(
            "NOT FIT", "UNFITTING").replace("갭", "GAP").replace("MARKS", "마크").replace("MARK", "마크").replace(
            "WELDING/PRESS", "웰딩/프레스").replace("WELD LINE", "WELDLINE").replace("홀", "HOLE")
        name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_]|[\W]", ' ', name)
        words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
        word_list.append(words)

    df['제목_1'] = [', '.join(i) for i in word_list]
    df['제목_1_발생빈도'] = [Counter(df['제목_1'].tolist())[i] for i in df['제목_1'].tolist()]
    # df.sort_values(["발생빈도", "불량구분", "제목_1_발생빈도"], inplace=True, ascending=[False, True, False])
    return df


def partsys_3_search(df):
    classifier_dict, key_sequence = problem_type_dict()
    revised_title = [i.upper() for i in df['제목'].tolist()]
    df = pre_processing(df, revised_title)

    audited = ["" for _ in revised_title]
    problem_class = ["" for _ in revised_title]

    for n, i in enumerate(df['제목'].tolist()):
        if audited[n] == "":
            for key in key_sequence:
                if key == i:
                    audited[n] = classifier_dict[key]['불량구분']


if __name__ == "__main__":
    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    def exp_data():
        df = MasterDBStorage('해외불량이력').df
        df['품명'] = [i.upper() for i in df['품명'].tolist()]
        df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
        df.drop_duplicates(subset="Part No", keep='first', inplace=True)
        df.drop_duplicates(subset="부품명", keep='first', inplace=True)
        return df

    df = exp_data()
    classifier_dict, key_sequence = problem_type_dict()
    print(classifier_dict)