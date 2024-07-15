import time
import re
import yaml
import bs4
import requests
import json
import pandas as pd
import urllib.request as request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

config = yaml.load(open('dcard.yml'), Loader=yaml.Loader)
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

timeout = 20
data_dict = {}
listt = ['樓層', '學校', '公司產業', '單位', '學歷', '年資', '月薪', '稅前年薪', '週工時']
for l in listt:
    data_dict[l] = []

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')                 # 瀏覽器不提供可視化頁面
    options.add_argument('-no-sandbox')               # 以最高權限運行
    options.add_argument('--start-maximized')        # 縮放縮放（全屏窗口）設置元素比較準確
    options.add_argument('--disable-gpu')            # 谷歌文檔說明需要加上這個屬性來規避bug
    options.add_argument('--window-size=1920,1080')  # 設置瀏覽器按鈕（窗口大小）
    options.add_argument('--incognito')               # 啟動無痕
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches',['enable-automation'])       #不顯示 Chrome目前受到自動測試軟體控制

    with open('cookies.json') as f:
        cookies = json.load(f)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd( "Page.addScriptToEvaluateOnNewDocument",{"source" : "Object.defineProperty(navigator, 'webdriver', {get: () => false})"})
    url = config['url']

    with request.urlopen(url) as response:
        data = json.read().decode('utf-8')
    print(data)
    driver.get(url)
    # for cookie in cookies:
    #     driver.add_cookie(cookie)
    # driver.refresh()

    return driver

def main():
    driver = get_driver()
    driver.save_screenshot("datacamp.png") 
    input('')
    # old_to_new = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/div[6]/div/div/div/div[1]/button[2]')))
    # driver.execute_script('arguments[0].click();', old_to_new)       #scrapy解決selenium中無法點擊Element
    # message = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/div[6]/div/div/div/div[2]/div')))
    # number = int(re.findall(r'\d+', message.text)[0])
    # # print(number)
    # scroll_to_bottom(driver, number)
    # data_dict = search(driver)

    # for key, value in data_dict.items():
    #     print(key, len([item for item in value if item]))

    df = pd.DataFrame(data_dict)
    # df_sorted = df.sort_values(by='樓層')
    df.to_excel('salary.xlsx', index=False)

def get_cookies(driver):
    cookies = driver.get_cookies()
    cookies_list = []
    for cookie in cookies:
        cookie_dict = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie['path'],
            # 'expiry': cookie['expiry'],  # 可能为 None，需要处理
            'secure': cookie['secure']
        }
        cookies_list.append(cookie_dict)

    with open('cookies.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(cookies_list, f, allow_unicode=True)

def scroll_to_bottom(driver, number):
    last = driver.execute_script('return document.documentElement.scrollHeight')
    i = 500
    while True:
    # for i in range(3):
        search(driver)

        i = i+500
        driver.execute_script('window.scrollTo(0, '+ str(i) +');')
        time.sleep(2)

        new = driver.execute_script('return document.documentElement.scrollHeight')
        print(f'原高度 {last}，新高度 {new}')

        code = len(data_dict['樓層'])
        if len(data_dict['樓層']) != number:
            print(f'目前到達 {code}')
            # if code == 30:
            #     break
        else:
            break

def search(driver):
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    salary = soup.find_all(attrs={'data-key': True})
    
    for sal in salary:
        # print(s)
        if 'comment' in sal['data-key']:
            university = sal.find_all('div', class_='d_a5_1p d_h_1q tw4hypf')
            subtitle = sal.find_all('div', class_='d_x9_34 d_xi_2v c1ehvwc9')
            code = sal.find_all('span', class_='d_1938jqx_42phs0 dl7cym2')
            # print(code, university, subtitle)
            
            for i in range(len(code)):
                if code[i].text.strip() in data_dict['樓層']:
                    continue
                else:
                    data_dict['樓層'].append(code[i].text.strip())
                    data_dict['學校'].append(university[i].text.strip())

                    for sub in subtitle[i]:
                        pattern = re.compile(r'一、公司產業：([^\n]+).*?二、單位：([^\n]+).*?三、學歷：([^\n]+).*?四、年資：([^\n]+).*?五、月薪：([^\n]+).*?六、稅前年薪：([^\n]+).*?七、週工時：([^\n]+h)', re.DOTALL)
                        matches = pattern.search(sub.text)
                        if matches:
                            data_dict['公司產業'].append(matches.group(1))
                            data_dict['單位'].append(matches.group(2))
                            data_dict['學歷'].append(matches.group(3))
                            data_dict['年資'].append(matches.group(4))
                            data_dict['月薪'].append(matches.group(5))
                            data_dict['稅前年薪'].append(matches.group(6))
                            data_dict['週工時'].append(matches.group(7))
                        else:
                            data_dict['公司產業'].append('')
                            data_dict['單位'].append('')
                            data_dict['學歷'].append('')
                            data_dict['年資'].append('')
                            data_dict['月薪'].append('')
                            data_dict['稅前年薪'].append('')
                            data_dict['週工時'].append('')

    # print(data_dict)
    return data_dict

if __name__ == '__main__':
    main()