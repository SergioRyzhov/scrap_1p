import argparse
import json
import logging
import os
import re
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List

import psycopg2
from pymongo import MongoClient

HOST = 'localhost'
PORT = 8087

NUM_DB_POSTS = 1000

parser = argparse.ArgumentParser(description='Reddit server')
parser.add_argument(
    '--user',
    type=str,
    default='postgres',
    help='Username to postrgesql db'
)
parser.add_argument(
    '--pass',
    type=str,
    default='123',
    help='Password to posgresql db'
)
args = parser.parse_args()

USERNAME_POSTGRE = args.number_of_posts
PASSWORD_POSTGRE = args.filename

logging.basicConfig(level=logging.INFO)
logging.info('Server ran...')

PATH = os.environ.get('CHROME_DRIVER')
if not PATH:
    logging.error('You must create the environment var!')

client = MongoClient('localhost', 27017)
db = client['reddit']
post = db.post
profile = db.profile
if post:
    logging.info('MongoDB connected')

postgre_conn = psycopg2.connect(
    dbname='reddit',
    host='localhost',
    port=5432,
    user=USERNAME_POSTGRE,
    password=PASSWORD_POSTGRE,
)
cur = postgre_conn.cursor()
if cur:
    logging.info('Postgresql connected')


class HttpProcessor(BaseHTTPRequestHandler):
    current_data = []
    for item in post.find({}):
        tmp = {}
        try:
            tmp['UNIQUE_ID'] = item['UNIQUE_ID']
            tmp['post URL'] = item['post URL']
            tmp['username'] = item['username']
            tmp['user karma'] = profile.find_one(
                {'username': item['username']})['user karma']
            tmp['user cake day'] = profile.find_one(
                {'username': item['username']})['user cake day']
            tmp['comment karma'] = item['comment karma']
            tmp['post date'] = item['post date']
            tmp['number of comments'] = item['number of comments']
            tmp['number of votes'] = item['number of votes']
            tmp['post category'] = item['post category']
        except:
            tmp['UNIQUE_ID'] = item['UNIQUE_ID']
        current_data.append(tmp)
    if len(current_data) == 0:
        try:
            cur.execute('SELECT * FROM post')
            post_sql = cur.fetchall()
            cur.execute('SELECT * FROM profile')
            user_sql = cur.fetchall()
            for item in post_sql:
                tmp = {}
                try:
                    tmp['UNIQUE_ID'] = item[2]
                    tmp['post URL'] = item[3]
                    tmp['username'] = item[1]
                    cur.execute(
                        'SELECT user_karma FROM profile WHERE username=%s', (item[1],))
                    tmp['user karma'] = cur.fetchone()[0]
                    cur.execute(
                        'SELECT user_cake_day FROM profile WHERE username=%s', (item[1],))
                    tmp['user cake day'] = cur.fetchone()[0]
                    tmp['comment karma'] = item[5]
                    tmp['post date'] = item[6]
                    tmp['number of comments'] = item[7]
                    tmp['number of votes'] = item[8]
                    tmp['post category'] = item[9]
                except:
                    tmp['UNIQUE_ID'] = item[2]
                current_data.append(tmp)
        except:
            pass
    if len(current_data) == 0:
        logging.info('dbs is empty, parse first')

    def _separate_data(self, data: Dict):
        """Separates the data into two parts:
        the first part is a post
        the second part is a user
        """
        post_data = {
            'username': data['username'],
            'UNIQUE_ID': data['UNIQUE_ID'],
            'post URL': data['post URL'],
            'post karma': data['post karma'],
            'comment karma': data['comment karma'],
            'post date': data['post date'],
            'number of comments': data['number of comments'],
            'number of votes': data['number of votes'],
            'post category': data['post category'],
        }
        user_data = {
            'username': data['username'],
            'user karma': data['user karma'],
            'user cake day': data['user cake day'],
        }
        return post_data, user_data

    def _save_mongo(self, items: List[Dict]):
        """Writes the data into db mongo"""
        if not items:
            logging.error("The data is empty. File not created")
            return

        for item in items:
            post_data, user_data = self._separate_data(item)
            try:
                if post.count_documents({}) < NUM_DB_POSTS:
                    post.update_one({'post URL': item['post URL']},
                                    {'$set': post_data}, upsert=True)
                    profile.update_one({'username': item['username']},
                                       {'$set': user_data}, upsert=True)
                else:
                    logging.warning(
                        f'Max number of posts {NUM_DB_POSTS} achieved')
                    break
            except Exception as err:
                logging.error(err)

    def _save_postgre(self, items: List[Dict]):
        """Writes the data into db postgresql"""
        if not items:
            logging.error("The data is empty. File not created")
            return
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS post (
                        id serial UNIQUE NOT NULL PRIMARY KEY,
                        username varchar(150),
                        UNIQUE_ID varchar(150) NOT NULL,
                        post_URL text,
                        post_karma int,
                        comment_karma int,
                        post_date varchar(255),
                        number_of_comments varchar(150),
                        number_of_votes varchar(30),
                        post_category varchar(255)
                    );
                CREATE TABLE IF NOT EXISTS profile (
                        id serial UNIQUE NOT NULL PRIMARY KEY,
                        username varchar(150),
                        user_karma int,
                        user_cake_day varchar(255)
                    );
                """
            )
        except Exception as err:
            logging.error(err)

        for item in items:
            post_data, user_data = self._separate_data(item)
            try:
                cur.execute('SELECT * FROM post')
                if cur.rowcount < NUM_DB_POSTS:
                    cur.execute('SELECT EXISTS(SELECT post_URL FROM post WHERE post_URL=%s)',
                                (post_data['post URL'],))
                    if not cur.fetchone()[0]:
                        cmd = 'INSERT INTO post (username,\
                            UNIQUE_ID, post_URL, post_karma,\
                            comment_karma, post_date, number_of_comments,\
                            number_of_votes, post_category) VALUES (%s, %s, %s,\
                            %s, %s, %s, %s, %s, %s)'
                        cur.execute(cmd, (
                            post_data['username'],
                            post_data['UNIQUE_ID'],
                            post_data['post URL'],
                            post_data['post karma'],
                            post_data['comment karma'],
                            post_data['post date'],
                            post_data['number of comments'],
                            post_data['number of votes'],
                            post_data['post category'],)
                        )
                    cur.execute('SELECT EXISTS(SELECT username FROM profile WHERE username=%s)',
                                (user_data['username'],))
                    if not cur.fetchone()[0]:
                        cmd = 'INSERT INTO profile (username, user_karma, user_cake_day)\
                            VALUES (%s, %s, %s)'
                        cur.execute(cmd, (
                            user_data['username'],
                            user_data['user karma'],
                            user_data['user cake day'],)
                        )
                else:
                    logging.warning(
                        f'Max number of posts {NUM_DB_POSTS} achieved')
                    break
            except Exception as err:
                logging.error(err)
        postgre_conn.commit()

    def resp_text(self, error_code: int, data=b''):
        """Sends the text respond"""
        self.send_response(error_code, f'{error_code}')
        self.send_header('content-type', 'text/html')
        # self.end_headers()
        if error_code in [400, 401, 404, 500]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(data)

    def resp_json(self, error_code: int, data: List[Dict]):
        """Sends the json respond"""
        self.send_response(error_code)
        self.send_header('content-type', 'application/json')
        # self.end_headers()
        if error_code in [400, 401, 404]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(
                bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))

    def do_GET(self):
        """Handles get requests"""
        try:
            if self.path == '/posts/' and self.current_data:
                self.resp_json(200, self.current_data)
            elif re.findall(r'/posts/\S+', self.path) and self.current_data:
                path = self.path.replace('/posts/', '')
                for item in self.current_data:
                    if path == item['UNIQUE_ID']:
                        self.resp_json(200, item)
            else:
                self.resp_text(404)
        except Exception as err:
            logging.error(err)
            self.resp_text(500)

    def do_POST(self):
        """Handles post requests with json or adds new uuid line"""
        try:
            if self.path == '/posts/':
                gen_uuid = str(uuid.uuid1())
                if self.current_data:
                    try:
                        if post.count_documents({}) < NUM_DB_POSTS:
                            post.update_one({'UNIQUE_ID': gen_uuid},
                                            {'$set': {
                                                'UNIQUE_ID': gen_uuid}},
                                            True)
                        else:
                            logging.warning(
                                f'Max number of posts {NUM_DB_POSTS} achieved')
                        cur.execute(
                            'INSERT INTO post (UNIQUE_ID) VALUES (%s);', (gen_uuid,))
                        postgre_conn.commit()
                        logging.info(f'empty post added')
                        self.resp_text(201, b'empty post added')
                        self.resp_json(200, {'UNIQUE_ID': gen_uuid})
                    except Exception as err:
                        logging.error(err)
                else:
                    HttpProcessor.current_data.append(
                        {'UNIQUE_ID': str(uuid.uuid1())})
                    self.resp_json(201, {self.current_data[0]['UNIQUE_ID']: 0})
                    self._save_mongo(self.current_data)
                    self._save_postgre(self.current_data)
            else:
                length = int(self.headers.get('Content-Length'))
                HttpProcessor.current_data = json.loads(
                    self.rfile.read(length))
                self.resp_json(200, self.current_data)
                self._save_mongo(self.current_data)
                self._save_postgre(self.current_data)
        except Exception as err:
            logging.error(err)
            self.resp_text(500)

    def do_DELETE(self):
        """Handles delete requests. Delete element by uuid"""
        try:
            if re.findall(r'/posts/\S+', self.path) and self.current_data:
                path = self.path.replace('/posts/', '')
                if post.find({'UNIQUE_ID': path}).count() == 1:
                    post.delete_one({'UNIQUE_ID': path})

                    cur.execute(
                        'DELETE FROM post WHERE UNIQUE_ID = %s;', (path,))
                    postgre_conn.commit()

                    logging.info(f'{path} post deleted')
                    self.resp_text(200, b'post deleted')
                else:
                    self.resp_text(404)
            else:
                self.resp_text(404)
        except Exception as err:
            logging.error(err)
            self.resp_text(500)

    def do_PUT(self):
        """Handles put requests with json. Update element by uuid."""
        try:
            if re.findall(r'/posts/\S+', self.path) and self.current_data:
                path = self.path.replace('/posts/', '')
                for item in self.current_data:
                    if path == item['UNIQUE_ID']:
                        length = int(self.headers.get('Content-Length'))
                        obtained_data = json.loads(self.rfile.read(length))
                        if post.find({'UNIQUE_ID': path}).count() == 1:
                            post.update_one({'UNIQUE_ID': path}, {
                                            '$set': obtained_data})
                            for key_obt in obtained_data.keys():
                                cur.execute(
                                    'UPDATE post SET {} = %s WHERE UNIQUE_ID = %s;'.format(key_obt.replace(' ', '_')), (obtained_data[key_obt], path,))
                            postgre_conn.commit()
                            logging.info(f'{path} post updatetd')
                            self.resp_text(200, b'post updated')
                        else:
                            self.resp_text(404)
            else:
                self.resp_text(404)
        except Exception as err:
            logging.error(err)
            self.resp_text(500)


try:
    serv = HTTPServer((HOST, PORT), HttpProcessor)
    serv.serve_forever()
except Exception as err:
    logging.error(f"{err}. "+"The server isn't ran")
