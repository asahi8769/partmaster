import re, os
import pandas as pd
from functools import reduce
os.chdir(os.pardir)


def part_names():
    with open('files/품목구분기준.xlsx', 'rb') as file:
        df = pd.read_excel(file)
        partnames = df['품명단어'].tolist()
        partnames = [i.split(', ') for i in partnames]
    return list(set([i for i in reduce(lambda x, y: x + y, partnames)]))


partnames = [i for i in part_names() if i not in ['PAINT', 'DUST', 'SCR']]
partnames += ['코리아오토글라스', 'ASSY', 'KOREA', 'CORPORATION', 'HX', 'RR', 'RH', 'VISUAL', 'DEFECT', 'HCF', 'D&R',
                  'REFER', 'THE', 'SAME', 'APPEARANCE','PROBLEM', 'BDM', 'MOBIS', 'KIMCHEON', 'CV', 'COMPL', 'FR', 'LH',
                  'INFORMATION', 'PART', 'WI', 'VER', 'REWORK', 'FI', 'SURFACE', 'SLH', 'UI', 'PPR', 'TRG', 'NOK',
                  'STAGE', 'DEFECTS', 'WRONG', 'OBSERVED', 'SEATING', 'AREA', 'CONDITION', 'CO', 'FOUND', 'PBBLE',
                  'ISSUES', 'PARTS', 'IMPRESSION', 'PLAKOR', 'ASAN', 'GX', 'LG', 'HAUSYS', 'LTD', 'RRRH', 'LN', 'TMA',
                  '도어벨트', '불량', 'ECOPLASTIC', 'NG', 'SC', 'KIA', 'HANKOOK', 'APPEARANCE'
                  'NATIONAL','CN','세방전지', 'STICKER','KAC', 'CLEARLH', 'SRH', 'COMBILAMP', 'YZ','HEADRH','TF',
                  '현대모비스', '김천공장','DL', 'FRT', 'VS', 'AQL','CONTAMINATION', 'SAMBOPLATEC', 'HI', 'TR', 'SAMSONG',
                  'KNIFE','INTERNAL', 'HEADLH', 'RP', 'COMPLETED','IQR','GCE','COMING', 'FROM', 'IS','OF', 'SHIN',
                  'CHROME','에스엘', '주식회사', '진량공장', 'ASSI','BEFORE', 'JULY', 'OLD', 'NO', 'SHOWING', 'BH',
                  'IDENTIFICATION', 'FE', 'COLD', 'TEST', 'RIB', 'COMPLETE', 'HEADLAMP', 'BETWEEM', 'HC', 'NOT',
                  'DURING', 'NVH', 'OPERATING', 'OPERATION', 'PADDLE', 'STICK', 'RELATED']

i = "(GI291) RR SEAT BELT– WEBBING DAMAGE"

name = re.sub(
    "(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[\t0-9\xa0\u3000\n?!\-+_,/\[\]()=@;.'-]|[^\w]", ' ', re.sub("(O2)", 'OXYGEN', i))

words = [i for i in name.split(' ') if i not in partnames and len(i) > 1]

# print(words)

# a = "1 31  2"
# print(a.split(" "))
#
# print("HDL-RR DR O/S,LH".replace("RR", ""))

i = "FRM 2ND/B RH 5P 17MYM"

name = re.sub("(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_/)])|[0-9\xa0\u3000\n?!\-+_,()=]", ' ', i)

# name = i.replace("SUB PART PROBLEM", "SUBPART").replace("PARTS", "PART")
print(name)