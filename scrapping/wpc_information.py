from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Chrome_options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from utils.functions import try_until_success
from master_db import MasterDBStorage

import re, os, pickle, time
from tqdm import tqdm
import sys
from utils.functions import update_chromedriver


class WPCPartsNames:
    def __init__(self, df, visible=False):
        # self.df = df
        self.df_part_list = df['Part No'].tolist()
        self.wpc_dict = self.load_wpcdict()
        GC_DRIVER = 'driver/chromedriver.exe'
        CHROME_OPTIONS = Chrome_options()
        CHROME_OPTIONS.add_argument("--start-maximized")
        if not visible:
            CHROME_OPTIONS.add_argument("--headless")
            CHROME_OPTIONS.add_argument("--disable-gpu")
        LOGIN_URL = "https://wpc.mobis.co.kr/Login.jsp"
        self.driver = webdriver.Chrome(GC_DRIVER, options=CHROME_OPTIONS)
        self.driver.get(LOGIN_URL)

    def load_wpcdict(self):
        try:
            with open('files/spawn/wpc_part.pkl', 'rb') as file:
                wpc_dict = pickle.load(file)
            return wpc_dict
        except FileNotFoundError:
            return dict()

    def save_wpcdict(self):
        with open('files/spawn/wpc_part.pkl', 'wb') as f:
            pickle.dump(self.wpc_dict, f)

    @try_until_success
    def log_in(self):
        id_box = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[1]/td[1]/input")))
        login_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
            (By.XPATH, "html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[1]/td[2]/button")))
        id_box.send_keys("1300687")
        ActionChains(self.driver).send_keys(Keys.TAB).send_keys("g202001001*").perform()
        login_button.click()
        WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/table/tbody/tr/td[7]/div/img")))
        print("Logged in Successfully")

    def search_part_info(self, partnumbers):
        search_url = "https://wpc.mobis.co.kr/Parts?cmd=getPartsList2&ptno=" + partnumbers + \
                     "&pncd=&lang=KR&page=1&hkgb=A&regns=AUS%2CCAN%2CDOM%2CEUR%2CGEN%2CMES%2CTUR%2CUSA&views=Y&sgmts=E%2CJ%2CN%2CR"
        self.driver.get(search_url)
        html = BeautifulSoup(self.driver.page_source, features="lxml")
        text = html.body.text.replace("－", "_").replace("-", "_")
        text = re.sub("[:@\s]", "", text)
        text = re.sub("[\\\\]", ",", text)
        return [j for j in [i.split(",") for i in text.split(",^")] if j[0] is not '']

    def iterative_search(self, slice=6):
        n = 0
        for i in tqdm(self.df_part_list):
            n += 1

            if i in self.wpc_dict.keys():
                if self.wpc_dict[i] != '__no_result__':
                    continue
                else:
                    i = i[:slice]
            info = self.search_part_info(i)
            try:
                self.wpc_dict[i] = info[0][3]
            except IndexError:
                self.wpc_dict[i] = '__no_result__'
            # print(i, self.wpc_dict[i])
            if n % 20 == 0:
                time.sleep(0.5)
                self.save_wpcdict()
        self.save_wpcdict()

    def close(self):
        self.driver.delete_all_cookies()
        self.driver.quit()
        # sys.exit()


def dom_data():
    df = MasterDBStorage('입고불량이력', append_from_file=True).df
    df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
    df['Part No'] = [i.replace(" ", "").replace("-", "") for i in df['Part No'].tolist()]
    df['Part No'] = [i[0:10] for i in df['Part No'].tolist()]
    df.drop_duplicates(subset="Part No", keep='first', inplace=True)
    return df


def exp_data():
    df = MasterDBStorage('해외불량이력', append_from_file=True).df
    df['품명'] = [i.upper() for i in df['품명'].tolist()]
    df.rename(columns={'품번': 'Part No', '품명': '부품명'}, inplace=True)
    df['Part No'] = [i.replace(" ", "").replace("-", "") for i in df['Part No'].tolist()]
    df['Part No'] = [i[0:10] for i in df['Part No'].tolist()]
    df.drop_duplicates(subset="Part No", keep='first', inplace=True)
    return df


def master_data():
    df = MasterDBStorage('파트마스터', append_from_file=True).df
    df['부품명'] = [i.upper() for i in df['부품명'].tolist()]
    df['Part No'] = [i.replace(" ", "").replace("-", "") for i in df['Part No'].tolist()]
    df['Part No'] = [i[0:10] for i in df['Part No'].tolist()]
    df.drop_duplicates(subset="Part No", keep='first', inplace=True)
    # print(df['Part No'].tolist())
    return df


if __name__ == "__main__":
    os.chdir(os.pardir)
    df1 = dom_data()
    # df2 = exp_data()
    # df3 = master_data()
    # update_chromedriver()

    for df in [
        df1,
        # df2,
        # df3
    ]:
        try:
            obj = WPCPartsNames(df, visible=False)
        except Exception as e:  # e.split('\n')[1] = Current browser version is 87.0.4280.88 with binary path C:\Program Files\Google\Chrome\Application\chrome.exe
            print(e)
            required_version = str(e).split('\n')[1].split(' ')[4].split('.')[0]
            update_chromedriver(browserVersion=required_version)
            obj = WPCPartsNames(df, visible=False)

        obj.log_in()
        obj.iterative_search()
        obj.close()
