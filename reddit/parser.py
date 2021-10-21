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

id_list = []
data = {}



def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response



def get_content(html):
    soup = bs(html.text, 'html.parser')
    found_posts = soup.find_all('div', {'class': '_1oQyIsiPHYt6nx7VOmd1sz'})
    for post in found_posts:
        if post not in id_list and len(id_list) < 100:
            id_list.append(post.get('id'))
            data['id'] = post.get('id')
            data['link'] = post.find('a', {'class': '_3jOxDPIQ0KaOWpzvSQo-1s'}).get('href')




def parse():
    params = {'t': 'month'}
    html = get_html(URL, params)
    if html.status_code == 200:
        options = Options()
        options.add_argument('--disable-infobars')
        options.add_argument('start-maximized')
        options.add_argument('--disable-extensions')
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1})
        driver = webdriver.Chrome(
            options=options, executable_path='D:/Рабочий стол/scrap_1p/reddit/chromedriver.exe')
        driver.get(html.url)
        time.sleep(2)

        get_content(html)

        while len(id_list) < 100:
            section = driver.find_element_by_xpath(
                f'//div[contains(@id, "{id_list[len(id_list)-1]}")]')
            actions = ActionChains(driver)
            actions.move_to_element(section).perform()

            get_content(html)

        # print(id_list)
        print(data)
        print(len(id_list), 'end')
        # print(html.url)
    else:
        print('error')


parse()
