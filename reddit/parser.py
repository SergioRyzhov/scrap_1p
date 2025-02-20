import argparse
import json
import logging
import os
import time
import uuid
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup as bs
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

PORT = 8087

API_HOST = 'http://localhost'

URL = 'https://www.reddit.com/top/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}

PARAMS = {'t': 'month'}

HOST = 'https://www.reddit.com'

NUMBER_OF_THREADS = 4

if os.name == 'nt':
    DRIVER_PART = 'chromedriver.exe'
else:
    DRIVER_PART = 'chromedriver'

parser = argparse.ArgumentParser(description='Reddit post parser')
parser.add_argument(
    '--number_of_posts',
    type=int,
    default=100,
    help='Number of posts'
)
parser.add_argument(
    '--filename',
    type=str,
    default=f'reddit-{datetime.now().strftime("%Y%m%d%H%M")}.txt',
    help='Filename'
)
args = parser.parse_args()

NUMBER_OF_POSTS = args.number_of_posts

FILENAME = args.filename

logging.basicConfig(level=logging.INFO)

PATH = os.environ.get('CHROME_DRIVER')
if not PATH:
    logging.error('You must create the environment var!')


start = time.time()
id_set = set()
data = []

options = Options()
# options.add_argument('start-maximized')
options.add_argument('--window-size=1024,1080')
options.add_argument("--headless")
options.add_argument('--incognito')
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--disable-notifications')
options.add_argument('--disable-default-apps')
options.add_argument('--disable-bundled-ppapi-flash')
options.add_argument('--disable-modal-animations')
options.add_argument('--disable-login-animations')
options.add_argument('--disable-pull-to-refresh-effect')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--autoplay-policy=document-user-activation-required')
options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 1})
options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2})
options.add_experimental_option("excludeSwitches", ["enable-logging"])


def get_html(url, params=None):
    """Makes url request and returns the response"""
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def save_file(items):
    """Transfers json file to the server"""
    try:
        requests.post(f'{API_HOST}:{PORT}', data=json.dumps(items))
        logging.info('File transferred to the server seccessfully')
    except:
        logging.error('File transfer error')


def element_mouseover(driver, post):
    """Hover mouse over element and load JS.
    Returns element
    """
    pub_date_elem = post.find_element(By.CLASS_NAME, '_3jOxDPIQ0KaOWpzvSQo-1s')
    pub_date_elem.location_once_scrolled_into_view
    driver.execute_script("window.scrollTo(0, window.scrollY - 80)")
    ActionChains(driver).move_to_element(pub_date_elem).perform()
    return pub_date_elem


def scrap_cake_day(driver, request):
    """Scraps cake_day and returns it"""
    open_user = request.json().get('data').get('subreddit').get('url')
    driver.execute_script(f'window.open("{HOST + open_user}", "new_window")')
    driver.switch_to.window(driver.window_handles[1])
    user_html = get_html(HOST + open_user)
    cake_day = get_soup(user_html.text).find(
        'span', {'id': 'profile--id-card--highlight-tooltip--cakeday'}).text
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return cake_day


def data_add(*args):
    """Adds data into the data global variable"""
    if len(data) < NUMBER_OF_POSTS:
        data.append({
            'UNIQUE_ID': str(uuid.uuid1()),
            'post URL': args[0],
            'username': args[1],
            'user karma': int(args[2]),
            'user cake day': args[3],
            'post karma': int(args[4]),
            'comment karma': int(args[5]),
            'post date': args[6],
            'number of comments': args[7],
            'number of votes': args[8],
            'post category': args[9],
        })
        logging.info(f'[№{len(data)}] {args[1]} parsed seccessfully')


def get_soup(html):
    """Returns soup from html page"""
    return bs(html, 'html.parser')


def get_content(thread):
    """Main function scraps the data right from the website.
    Scrapped data appends in data list (global var).
    """
    scroll_list = []
    if DRIVER_PART == 'chromedriver':
        display = Display(visible=0, size=(1024, 1080))
        display.start()
    driver = webdriver.Chrome(
        options=options, executable_path=f'{PATH}/{DRIVER_PART}')
    html = get_html(URL, PARAMS)
    if html.status_code == 200:
        logging.info(f'[{thread}]Connection established')
        driver.get(html.url)
        while len(data) < NUMBER_OF_POSTS:
            try:
                found_posts = driver.find_elements(
                    By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
                if found_posts == '':
                    continue
            except:
                continue
            for post in found_posts:
                post_id = post.get_attribute('id')
                if post_id not in id_set:
                    if len(data) >= NUMBER_OF_POSTS:
                        break
                    id_set.add(post_id)
                    scroll_list.append(post_id)
                    try:
                        post_content = post.text.split('\n')

                        pub_date_elem = element_mouseover(driver, post)
                        if pub_date_elem == '':
                            raise Exception('')

                        username = post_content[2].replace('•Posted byu/', '')
                        post_url = post.find_element(
                            By.CLASS_NAME, '_3jOxDPIQ0KaOWpzvSQo-1s').get_attribute('href')
                        request = requests.get(
                            f'{HOST}/user/{username}/about.json', headers=HEADERS)
                        if request.json().get('data').get('subreddit').get('over_18'):
                            logging.warning(
                                f"You must be 18+ to view {username}'s community")
                            raise Exception('')

                        comment_karma = request.json().get('data').get('comment_karma')
                        user_karma = request.json().get('data').get('total_karma')
                        post_karma = request.json().get('data').get('link_karma')
                        if post_karma == '' and user_karma == '' and comment_karma == '':
                            raise Exception('')

                        post_date = driver.find_element(
                            By.CLASS_NAME, '_2J_zB4R1FH2EjGMkQjedwc').text
                        if post_date == '':
                            raise Exception('')

                        for item in post_content:
                            if item.find('Comments') != -1:
                                number_of_comments = item
                        if number_of_comments == '':
                            raise Exception('')

                        number_of_votes = post_content[0]
                        post_category = post_content[1].replace('r/', '')
                        if post_category == '':
                            raise Exception('')

                        cake_day = scrap_cake_day(driver, request)
                        if cake_day == '':
                            raise Exception('')
                    except:
                        continue
                    data_add(
                        post_url,
                        username,
                        user_karma,
                        cake_day,
                        post_karma,
                        comment_karma,
                        post_date,
                        number_of_comments,
                        number_of_votes,
                        post_category
                    )
            try:
                group_posts_next = driver.find_element(
                    By.ID, scroll_list[len(scroll_list)-1])
                group_posts_next.location_once_scrolled_into_view
            except:
                logging.warning(f'Missed scrolling')
                continue
    else:
        logging.error(f'Connection error: {html.status_code}')
    driver.quit()


def parse():
    """Parse function controls other functions.
    Creates threads.
    Calls save_file function.
    Loggins and of script.
    """
    threads = []
    for i in range(NUMBER_OF_THREADS):
        t = Thread(target=get_content, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    save_file(data)

    logging.info(f'Job well done. Parsed {len(data)} posts')
    logging.info(
        f'The script work time {(time.time() - start) / 60:.2f} minutes')


parse()
