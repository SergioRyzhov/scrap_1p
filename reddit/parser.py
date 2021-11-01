import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from threading import Thread
import logging
import time
import uuid

URL = 'https://www.reddit.com/top/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}

PARAMS = {'t': 'month'}

HOST = 'https://www.reddit.com'

PATH = 'D:/Рабочий стол/scrap_1p/reddit/'

NUMBER_OF_THREADS = 2

logging.basicConfig(level=logging.INFO)

start = time.time()
# id_list = []
id_set = set()
data = []

options = Options()
# options.add_argument('start-maximized')
options.add_argument('--window-size=1024,1080')
# options.add_argument("--headless")
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
    """Does get request and returns response"""
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def save_file(items):
    """Creates reddit-YYYYMMDDHHMM.txt format file and dumps the data.   
    Returns nothing.
    """
    with open(f'{PATH}reddit-{datetime.now().strftime("%Y%m%d%H%M")}.txt', 'w', newline='', encoding='utf-8') as fw:
        try:
            for item in items:
                fw.writelines([
                    f"{item['UNIQUE_ID']};",
                    f"{item['post URL']};",
                    f"{item['username']};",
                    f"{item['user karma']};",
                    f"{item['user cake day']};",
                    f"{item['post karma']};",
                    f"{item['comment karma']};",
                    f"{item['post date']};",
                    f"{item['number of comments']};",
                    f"{item['number of votes']};",
                    f"{item['post category']};\n",
                ])
            logging.info('File written seccessfully')
        except:
            logging.error(
                'Writefile error. Try to delete last file.txt manually.')

def data_add(*args):
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
    """returns soup from html page"""
    return bs(html, 'html.parser')

def get_content(i):
    """
    Main function scraps the data right from the website.
    Scrapped data appends in data list (global var).
    """
    driver = webdriver.Chrome(options=options, executable_path=f'{PATH}chromedriver.exe')
    html = get_html(URL, PARAMS)
    if html.status_code == 200:
        logging.info(f'[{i}]Connection established')
        driver.get(html.url)
        while len(data) < 100:
            try:
                found_posts = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
            except:
                continue
            for i, post in enumerate(found_posts, 1):
                try:
                    post_id = post.get_attribute('id')
                    if post_id in id_set and len(data) >= 100:
                        continue
                    # id_list.append(post_id)
                    id_set.add(post_id)
                    post_content = post.text.split('\n')

                    try:
                        pub_date_elem = post.find_element(By.CLASS_NAME, '_3jOxDPIQ0KaOWpzvSQo-1s')
                        pub_date_elem.location_once_scrolled_into_view
                        driver.execute_script("window.scrollTo(0, window.scrollY - 80)")
                        ActionChains(driver).move_to_element(pub_date_elem).perform()
                    except:
                        raise Exception('')

                    username = post_content[2].replace('•Posted byu/', '')
                    post_url = post.find_element(By.CLASS_NAME, '_3jOxDPIQ0KaOWpzvSQo-1s').get_attribute('href')
                    request = requests.get(f'{HOST}/user/{username}/about.json', headers=HEADERS)
                    if request.json().get('data').get('subreddit').get('over_18'):
                        logging.warning(
                            f"You must be 18+ to view {username}'s community")
                        raise Exception('')
                    comment_karma = request.json().get('data').get('comment_karma')
                    user_karma = request.json().get('data').get('total_karma')
                    post_karma = request.json().get('data').get('link_karma')

                    for _ in range(10):
                        try:
                            post_date = driver.find_element(By.CLASS_NAME, '_2J_zB4R1FH2EjGMkQjedwc').text
                            if post_date != '':
                                break
                        except:
                            ActionChains(driver).move_to_element(pub_date_elem).perform()
                            raise Exception('')

                    for item in post_content:
                        if item.find('Comments') != -1:
                            number_of_comments = item
                    if number_of_comments == '':
                        raise Exception('')
                            # number_of_comments = post.find_element(By.CLASS_NAME, '_1UoeAeSRhOKSNdY_h3iS1O').text

                    number_of_votes = post_content[0]
                    post_category = post_content[1]
                    if post_category == '':
                        raise Exception('')

                    try:
                        open_user = request.json().get('data').get('subreddit').get('url')
                        driver.execute_script(f'window.open("{HOST + open_user}", "new_window")')
                        driver.switch_to.window(driver.window_handles[1])
                        user_html = get_html(HOST + open_user)
                        cake_day = get_soup(user_html.text).find('span', {'id': 'profile--id-card--highlight-tooltip--cakeday'}).text
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        logging.warning(f"Can't open {username} profile")
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
    else:
        logging.error(f'Connection error: {html.status_code}')

    try:
        group_posts_next = driver.find_element(By.ID, list(id_set)[len(id_set)-1])
        group_posts_next.location_once_scrolled_into_view
    except:
        logging.warning(f'Missed scrolling')
        driver.close()
        driver.quit()
        return


def parse():
    """
    Parse function controls other functions.
    Creates connection.
    Looks at filling data and calls functions to scroll blocks with parsed posts.
    """
    # barrier = Barrier(NUMBER_OF_THREADS)
    threads = []
    for i in range(NUMBER_OF_THREADS):
        # t = Thread(target=get_content, args=(barrier, i))
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
