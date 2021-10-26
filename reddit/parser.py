import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import logging
import time
import uuid

URL = 'https://www.reddit.com/top/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}

PARAMS = {'t': 'month'}

HOST = 'https://www.reddit.com/'


logging.basicConfig(level=logging.INFO)

start = time.time()
id_list = []
data = []

options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-infobars')
# options.add_argument('start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--disable-notifications')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--autoplay-policy=no-user-gesture-required')
options.add_argument('--disable-bundled-ppapi-flash')
options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 1})
options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2})
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(
    options=options, executable_path='D:/Рабочий стол/scrap_1p/reddit/chromedriver.exe')


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def save_file(items):
    with open('reddit.txt', 'w', newline='', encoding='utf-8') as fw:
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


def get_content(html):
    try:
        found_posts = driver.find_elements_by_class_name(
            '_1oQyIsiPHYt6nx7VOmd1sz')

        for post in found_posts:
            try:
                post_id = post.get_attribute('id')
            except:
                logging.warning("Can't find the id")
                continue
            if post_id not in id_list and len(data) < 100:
                id_list.append(post_id)
                try:
                    try:
                        pub_date_elem = post.find_element_by_class_name(
                            '_3jOxDPIQ0KaOWpzvSQo-1s')
                    except:
                        logging.warning('pub_date_elem not found')
                    try:
                        pub_date_elem.location_once_scrolled_into_view
                    except:
                        logging.warning("Can't scroll to pub_date_elem")
                    try:
                        driver.execute_script(
                            "window.scrollTo(0, window.scrollY - 80)")
                    except:
                        logging.warning("Can't scroll -80")
                    try:
                        ActionChains(driver).move_to_element(
                            pub_date_elem).perform()
                    except:
                        logging.warning(
                            "Can't perform mouseover pub_date_elem")
                        continue

                except:
                    logging.warning("Missed the post focus")
                    continue

                try:
                    username = post.find_element_by_class_name(
                        '_2tbHP6ZydRpjI44J3syuqC').text.replace('u/', '')
                except:
                    logging.warning('Missed the username')
                    continue

                try:
                    post_url = post.find_element_by_class_name(
                        '_3jOxDPIQ0KaOWpzvSQo-1s').get_attribute('href')
                except:
                    logging.warning(f'Missed the post_url of {username}')
                    continue

                try:
                    request = requests.get(
                        f'{HOST}user/{username}/about.json', headers=HEADERS)
                    if request.json().get('data').get('subreddit').get('over_18'):
                        logging.warning(
                            f"You must be 18+ to view {username}'s community")
                        continue
                except:
                    logging.warning(f'Missed the reqest {username}')
                    continue

                try:
                    comment_karma = request.json().get('data').get('comment_karma')
                except:
                    logging.warning(f'Missed the comment_karma {username}')
                    continue

                try:
                    user_karma = request.json().get('data').get('total_karma')
                except:
                    logging.warning(f'Missed the user_karma {username}')
                    continue

                try:
                    post_karma = request.json().get('data').get('link_karma')
                except:
                    logging.warning(f'Missed the post_karma {username}')
                    continue

                for _ in range(10):
                    try:
                        post_date = driver.find_element_by_class_name(
                            '_2J_zB4R1FH2EjGMkQjedwc').text
                        if post_date != '':
                            break
                    except:
                        ActionChains(driver).move_to_element(
                            pub_date_elem).perform()
                        continue
                if post_date == '':
                    logging.warning(f'Missed the post_date {username}')
                    continue

                try:
                    number_of_comments = post.find_element_by_class_name(
                        '_1UoeAeSRhOKSNdY_h3iS1O').text
                except:
                    logging.warning(
                        f'Missed the number_of_comments {username}')
                    continue

                try:
                    number_of_votes = post.find_element_by_class_name(
                        '_1E9mcoVn4MYnuBQSVDt1gC').text
                except:
                    logging.warning(f'Missed the number_of_votes {username}')
                    continue

                try:
                    post_category = post.find_element_by_class_name(
                        '_2mHuuvyV9doV3zwbZPtIPG').text.replace('r/', '')
                except:
                    logging.warning(f'Missed the post_category {username}')
                    continue

                try:
                    open_user = post.find_element_by_class_name(
                        '_2tbHP6ZydRpjI44J3syuqC')
                    driver.execute_script(
                        f'window.open("{open_user.get_attribute("href")}", "new_window")')
                    driver.switch_to.window(driver.window_handles[1])
                    cake_day = driver.find_element_by_id(
                        'profile--id-card--highlight-tooltip--cakeday').text
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    logging.warning(f"Can't open {username} profile")
                    continue

                data.append({
                    'UNIQUE_ID': str(uuid.uuid1()),
                    'post URL': post_url,
                    'username': username,
                    'user karma': int(user_karma),
                    'user cake day': cake_day,
                    'post karma': int(post_karma),
                    'comment karma': int(comment_karma),
                    'post date': post_date,
                    'number of comments': number_of_comments,
                    'number of votes': number_of_votes,
                    'post category': post_category,
                })
                logging.info(
                    f'[№{len(data)}] The {username} parsed seccessfully')
    except:
        logging.info(f'[№{len(data)}] The {username} parse failed')


def parse():
    html = get_html(URL, PARAMS)
    if html.status_code == 200:
        logging.info('Connection established')
        driver.get(html.url)
        while len(data) < 100:
            get_content(html)
            try:
                group_posts_next = driver.find_element_by_id(
                    id_list[len(id_list)-1])
                group_posts_next.location_once_scrolled_into_view
            except:
                logging.warning(f'Missed scrolling')
                continue
        save_file(data)

        driver.close()
        driver.quit()

        logging.info(f'Job well done. Parsed {len(data)} posts')
        logging.info(
            f'The script work time {int(time.time() - start)} seconds')

    else:
        logging.error(f'Connection error: {html.status_code}')


parse()
