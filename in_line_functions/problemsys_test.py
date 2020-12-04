import pandas as pd


def problem_data():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols = "F, K, L, O")
        df.sort_values("불량구분", inplace=True)
        df.rename(columns={'불량구분.1': '대분류'}, inplace=True)
        df.drop_duplicates(subset="제목", keep='first', inplace=True)
    return df


if __name__ == "__main__":
    # from master_db import MasterDBStorage
    import os
    os.chdir(os.pardir)
    print("Current working directory: {0}".format(os.getcwd()))

    df = problem_data()
    print(df)

    filename = "불량구분결과_test"
    with pd.ExcelWriter(rf'files\spawn\{filename}.xlsx') as writer:
        df.to_excel(writer, sheet_name='품번체계', index=False)
    os.startfile(rf'files\spawn\{filename}.xlsx')