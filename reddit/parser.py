import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint

URL = 'https://www.reddit.com/top/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def get_content(html):
    soup = bs(html, 'html.parser')
    unique_id = soup.find('div', {'class': '_1oQyIsiPHYt6nx7VOmd1sz'}).get('id')
    print(unique_id)


def parse():
    params = {'t': 'month'}
    html = get_html(URL, params)
    if html.status_code == 200:
        get_content(html.text)
        # print(html.url)
    else:
        print('error')


parse()