import pandas as pd


def part_data():
    with open('files/불량유형수기정리.xlsx', 'rb') as file:
        df = pd.read_excel(file, usecols = "F:H")
        # df.sort_values("품명", inplace=True)
        # df.drop_duplicates(subset="품번", keep='first', inplace=True)
    return df


if __name__ == "__main__":
    from master_db import MasterDBStorage
    import os