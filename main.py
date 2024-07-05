import time
import re
import yaml
import bs4
import hyperlink
import openpyxl
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

config = yaml.load(open('dcard.yml'), Loader=yaml.Loader)

timeout = 20
dlist = []
slist = []

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')                 # 瀏覽器不提供可視化頁面
    options.add_argument('-no-sandbox')               # 以最高權限運行
    options.add_argument('--start-maximized')        # 縮放縮放（全屏窗口）設置元素比較準確
    options.add_argument('--disable-gpu')            # 規避部分chrome gpu bug
    options.add_argument('--window-size=1920,1080')  # 設置瀏覽器按鈕（窗口大小）
    options.add_argument('--incognito')               # 啟動無痕
    options.add_argument('--log-level=3')           # 這個option可以讓你跟headless時網頁端的console.log說掰掰
    options.add_argument('--disable-dev-shm-usage')     # 使用共享內存RAM
    options.add_argument('blink-settings=imagesEnabled=false')  # 不加載圖片提高效率
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])

    driver = webdriver.Chrome(options=options)
    url = config['url']
    
    driver.get(url)

    return driver

def main():
    driver = get_driver()
    number = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/div[6]/div/div/div/div[2]/div')))
    print(int(re.findall(r'\d+', number.text)[0]))
    scroll_to_bottom(driver, number)
    df = pd.DataFrame(slist)
    df_sorted = df.sort_values(by='樓層')
    df_sorted.to_excel('salary.xlsx', index=False)

def scroll_to_bottom(driver, number):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5) 
        search(driver)
        pattern()
        if len(slist) == number:
            break  

def search(driver):
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    salary = soup.find_all(attrs={'data-key': True})

    for s in salary:
        if 'comment' in s['data-key']:
            ss = s.text.split('\n')
            for line in ss:
                # print(line)
                if line not in dlist:
                    dlist.append(line)
                    print(dlist)

def pattern():
    pattern = re.compile(r'(B\d+).*?男(國立\w+大學).*?一、公司產業：([^\n]+).*?二、單位：([^\n]+).*?三、學歷：([^\n]+).*?四、年資：([^\n]+).*?五、月薪：([^\n]+).*?六、稅前年薪：([^\n]+).*?七、週工時：([^\n]+h)', re.DOTALL)
    matches = pattern.findall('\n'.join(dlist))
    for match in matches:
        code, university, industry, unit, degree, experience, salary, annual_salary, working_hours = match
        datas = {
            '樓層': code,
            '學校': university,
            '公司產業': industry,
            '單位': unit,
            '學歷': degree,
            '年資': experience,
            '月薪': salary,
            '稅前年薪': annual_salary,
            '週工時': working_hours
        }
        if datas not in slist:
            slist.append(datas)


if __name__ == '__main__':
    main()