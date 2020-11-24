import pandas as pd
import sqlite3
import warnings
from utils.functions import show_elapsed_time
from utils.config import SQL_SCHEMA


class MasterDBStorage:
    warnings.filterwarnings('ignore')

    def __init__(self, name, append_from_file=True):
        self.table_name = name
        self.excel_name = rf'files\{self.table_name}.xlsx'
        self.db = "master.db"
        self.db_directory = rf"files\{self.db}"

        if append_from_file:
            try:
                self.df = self.sql_to_df()
            except Exception as e:
                self.db_schema()
                self.db_append_table()
                self.df = self.sql_to_df()

    @show_elapsed_time
    def df_to_sql(self, df):
        with sqlite3.connect(self.db_directory) as conn:
            df.to_sql(self.table_name, con=conn, if_exists='append', index=None, index_label=None)

    @show_elapsed_time
    def sql_to_df(self):
        with sqlite3.connect(self.db_directory) as conn:
            return pd.read_sql(f'SELECT * FROM {self.table_name}', conn)

    @show_elapsed_time
    def db_append_table(self):
        with open(self.excel_name, 'rb') as file:
            df = pd.read_excel(file, converters={'품번': lambda x: str(x), '업체코드': lambda x: str(x)})
            print(df)
            df.fillna('', inplace=True)
            df = df.applymap(str)

        self.df_to_sql(df)

    @show_elapsed_time
    def db_schema(self):
        query = SQL_SCHEMA.get(self.table_name, None)
        if query is None:
            return
        print(f'Query being executed.. {query}')
        with sqlite3.connect(self.db_directory) as conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

    def db_tables(self):
        with sqlite3.connect(self.db_directory) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return tuple(i[0] for i in cursor.fetchall())

    @classmethod
    @show_elapsed_time
    def db_drop_table(cls, name):
        obj = cls(name, append_from_file=False)
        with sqlite3.connect(obj.db_directory) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP table {obj.table_name};")

    @classmethod
    def run(cls, name, df=None):
        try:
            cls.db_drop_table(name)
        except:
            pass
        if df is None:
            cls(name)
        else:
            cls(name, append_from_file=True).df_to_sql(df)


if __name__ == "__main__":
    MasterDBStorage.run('품번체계')

    # with open('files/해외불량이력.xlsx', 'rb') as file:
    #     master_df = pd.read_excel(file)
    #     master_df.fillna('', inplace=True)
    #     master_df = master_df.applymap(str)
    # print(master_df.columns)
    # with sqlite3.connect('files/test_db.db') as conn:
    #     master_df.to_sql('master', con=conn, if_exists='replace', index=None, index_label=None)




