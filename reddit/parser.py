import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import time
import uuid

URL = 'https://www.reddit.com/top/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}

PARAMS = {'t': 'month'}

id_list = []
data = []

options = Options()
options.add_argument('--disable-infobars')
# options.add_argument('start-maximized')
options.add_argument('--disable-extensions')
options.add_argument("--disable-notifications")
# options.add_experimental_option(
#     "prefs", {"profile.default_content_setting_values.notifications": 1})
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options, executable_path='D:/Рабочий стол/scrap_1p/reddit/chromedriver.exe')

def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def save_file(items):
    with open('reddit.txt', 'w', newline='', encoding='utf-8') as fw:
        for item in items:
            fw.writelines([f"{item['UNIQUE_ID']};", f"{item['post URL']};\n"])


def mouse_over_class_name(path):
    actions = ActionChains(driver)
    section = driver.find_element_by_class_name(path)
    actions.move_to_element(section).perform()

def get_content(html):
    # soup = bs(html.text, 'html.parser')
    found_posts = driver.find_elements_by_class_name('_1oQyIsiPHYt6nx7VOmd1sz')

    for post in found_posts:
        if post.get_attribute('id') not in id_list and len(id_list) < 100:
            id_list.append(post.get_attribute('id'))
            # mouse_over_class_name('_2tbHP6ZydRpjI44J3syuqC')
            data.append({
                'UNIQUE_ID': str(uuid.uuid1()),
                'post URL': post.find_element_by_class_name('_3jOxDPIQ0KaOWpzvSQo-1s').get_attribute('href'),
                'number of comments': post.find_element_by_class_name('_1UoeAeSRhOKSNdY_h3iS1O').text,
                'number of votes': post.find_element_by_class_name('_1E9mcoVn4MYnuBQSVDt1gC').text,
            })



def parse():
    html = get_html(URL, PARAMS)
    if html.status_code == 200:
        driver.get(html.url)
        # actions = ActionChains(driver)
        # time.sleep(3)
        while len(id_list) < 100:
            get_content(html)
            driver.execute_script("window.scrollTo(50, document.body.scrollHeight);")
            # section = driver.find_element_by_id(id_list[count])
            # actions.move_to_element(section).perform()
        # save_file(data)

        print(data)
        # print(id_list)
        print(len(id_list), 'end')
        driver.close()
        driver.quit()
        # print(len(data), 'end')
        # print(html.url)
    else:
        print('error')


parse()
