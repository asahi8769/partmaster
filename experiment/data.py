from searches.problemsys_search import *
from searches.filters import prob_words_not_to_skip, prob_additional_exceptions
from searches.partsys_search import partsys_3_search
from utils.functions import show_elapsed_time


class Dataset:
    def __init__(self, file_path, spawn=False):
        self.file_path = file_path
        self.spawn_file = spawn
        self.df = None

    @show_elapsed_time
    def get_dataframe(self):
        with open(self.file_path, 'rb') as file:
            self.df = pd.read_excel(file, usecols="F, H, K, L")
            self.df.rename(columns={'품번': 'Part No', '품명': '부품명', '불량구분': 'Target'}, inplace=True)
            self.preprocess()
        if self. spawn_file:
            self.spawn()
        return self.df

    @show_elapsed_time
    def preprocess(self,):
        self.partsys()
        part_list, supplier_list = get_basic_filters()
        words_to_skip = [i for i in part_list + supplier_list if i not in prob_words_not_to_skip]
        words_to_skip += prob_additional_exceptions
        print("Filtering :", len(words_to_skip))
        word_list = []
        title = [i.upper() for i in self.df['제목'].tolist()]
        for i, n in enumerate(title):
            name = n.replace("SUB-PART", "SUBPART").replace("SUB PART", "SUBPART").replace(
                "SUB PART PROBLEM", "SUBPART").replace("PARTS", "PART").replace("으로", "").replace(
                "PRESSURE", "압력").replace("NOT FIXED", "SUBPART").replace("FITTING", "FIT").replace(
                "FITTED","FIT").replace("NOT FIT", "UNFITTING").replace("BAD FIT", "UNFITTING").replace(
                "갭", "GAP").replace("MARKS","마크").replace("MARK", "마크").replace("WELDING/PRESS", "웰딩/프레스").replace(
                "WELD LINE", "WELDLINE").replace("홀", "HOLE").replace("BAR CODE", "BARCODE")
            name = re.sub("(NO)(\.)[0-9\s]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9_]|[\W]", ' ', name)
            words = [i for i in name.split(' ') if i not in words_to_skip and len(i) > 1]
            word_list.append(words)
        self.df['정리'] = [', '.join(i) for i in word_list]
        self.df['Target_빈도'] = [Counter(self.df['Target'].tolist())[i] for i in self.df['Target'].tolist()]
        self.df['Description'] = self.df['정리'] +', '+ self.df['부품체계_1'] +', '+ self.df['부품체계_2']+', '+ self.df['부품체계_3']
        self.df = self.df[['부품명', 'Part No', '제목', '정리', '부품체계_1', '부품체계_2', '부품체계_3', 'Description', 'Target', 'Target_빈도']]
        self.df.sort_values(['Target_빈도'], inplace=True, ascending=[False])

    @show_elapsed_time
    def partsys(self):
        with open('files/품목구분기준.xlsx', 'rb') as file:
            df_1 = pd.read_excel(file, sheet_name='부품체계1')
            df_2 = pd.read_excel(file, sheet_name='부품체계2')
        partsys_1_dict = dict(zip([str(i) for i in df_1['품번'].tolist()], df_1['부품구분']))
        partsys_2_dict = {str(p): df_2['부품구분'].tolist()[n] for n, p in enumerate(df_2['품번'].tolist())}
        self.df['부품체계_1'] = [partsys_1_dict.get(i[0], '') for i in self.df['Part No'].tolist()]
        self.df['부품체계_2'] = [partsys_2_dict.get(i[:2], '') for i in self.df['Part No'].tolist()]
        self.df = partsys_3_search(self.df)

    @show_elapsed_time
    def spawn(self):
        filename = 'files\spawn\experiment_data.xlsx'
        with pd.ExcelWriter(filename) as writer:
            self.df.to_excel(writer, sheet_name='품번체계', index=False)
        os.startfile(filename)




if __name__ == "__main__":
    os.chdir(os.pardir)
    data = Dataset(file_path='files/불량유형수기정리.xlsx')
    df = data.get_dataframe()

    # data.preprocess()

    print(df.columns)

