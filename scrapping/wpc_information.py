from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Chrome_options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import re

import os


class WPCPartsNames:
    def __init__(self):
        GC_DRIVER = 'driver/chromedriver.exe'
        CHROME_OPTIONS = Chrome_options()
        CHROME_OPTIONS.add_argument("--start-maximized")
        # CHROME_OPTIONS.add_argument("--headless")
        LOGIN_URL = "https://wpc.mobis.co.kr/Login.jsp"
        self.driver = webdriver.Chrome(GC_DRIVER, options=CHROME_OPTIONS)
        self.driver.get(LOGIN_URL)

    def click_element_id(self, ID, sec):
        try:
            element = WebDriverWait(self.driver, sec).until(EC.element_to_be_clickable((By.ID, ID)))
            element.click()
            return element
        except TimeoutException:
            pass

    def log_in(self):
        id_box = self.driver.find_element_by_id('chkID')
        login_button = self.driver.find_element_by_id('logon')
        id_box.send_keys("1300687")
        ActionChains(self.driver).send_keys(Keys.TAB).send_keys("g202001001*").perform()
        login_button.click()

    def input_partnumber(self, partnumbers):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "m_sBtn_Partslist")))
        # pn_box = self.driver.find_element_by_id('Parts')
        # pn_box.send_keys(partnumbers)
        # search_btn = self.driver.find_element_by_id('m_sBtn_Partslist')
        # search_btn.click()
        # soup = BeautifulSoup(self.driver.page_source, 'lxml')
        new_url = "https://wpc.mobis.co.kr/Parts?cmd=getPartsList2&ptno="+partnumbers+"&pncd=&lang=KR&page=1&hkgb=A&regns=AUS%2CCAN%2CDOM%2CEUR%2CGEN%2CMES%2CTUR%2CUSA&views=Y&sgmts=E%2CJ%2CN%2CR"
        self.driver.get(new_url)

        html = self.driver.page_source
        parsed_html = BeautifulSoup(html, features="lxml")
        text = parsed_html.body.text
        text = str(text).replace("－", "_")
        text = re.sub("[:@\s]", "", text)
        text = re.sub("[\\\\]", ",", text)
        print("")
        part_list = [i.split(r",") for i in text.split(r"^") if len(i[3])>1]
        print(part_list)

        # extracted = re.sub("[:\\\\^@0-9]", "", text)
        # print(parsed_html)
        # print(text)
        # print(extracted)
        #
        # input("terminate")
        #
        # tables = soup.find_all('table')
        # print(tables)


if __name__ == "__main__":
    os.chdir(os.pardir)

    obj = WPCPartsNames()
    obj.log_in()
    obj.input_partnumber("37160")