import argparse
import logging
from typing import Union

import psycopg2
from psycopg2.extensions import AsIs
from pymongo import results

logging.basicConfig(level=logging.INFO)

MAX_DB_POSTS = 1000
HOST = 'localhost'
PORT = 5432

parser = argparse.ArgumentParser(description='Reddit server')
parser.add_argument(
    '--user',
    type=str,
    default='postgres',
    help='Username to postrgesql db'
)
parser.add_argument(
    '--password',
    type=str,
    default='123',
    help='Password to posgresql db'
)
parser.add_argument(
    '--db',
    type=str,
    default='reddit',
    help='Name of posgresql db'
)
args = parser.parse_args()

USERNAME_POSTGRE = args.user
PASSWORD_POSTGRE = args.password
DB_NAME = args.db

postgre_conn = psycopg2.connect(
    dbname='reddit',
    host=HOST,
    port=PORT,
    user=USERNAME_POSTGRE,
    password=PASSWORD_POSTGRE,
)
postgre_conn.autocommit = True
if postgre_conn:
    logging.info('Postgresql connected')
cur = postgre_conn.cursor()


class CreateTables:
    def __init__(self) -> None:
        """Creates tables
        """        
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS post (
                        id serial UNIQUE NOT NULL PRIMARY KEY,
                        user_id int,
                        username varchar(150),
                        UNIQUE_ID varchar(150) UNIQUE NOT NULL,
                        post_URL text UNIQUE,
                        post_karma int,
                        comment_karma int,
                        post_date varchar(255),
                        number_of_comments varchar(150),
                        number_of_votes varchar(30),
                        post_category varchar(255)
                    );
                CREATE TABLE IF NOT EXISTS profile (
                        id serial UNIQUE NOT NULL PRIMARY KEY,
                        username varchar(150) UNIQUE,
                        user_karma int,
                        user_cake_day varchar(255)
                    );
                ALTER TABLE post
                    ADD CONSTRAINT post_profile_user_id_fk
                        FOREIGN KEY (user_id) REFERENCES profile(id);
                """
            )
        except psycopg2.errors.DuplicateObject:
            logging.warning('Tables already exists')


class ItemsCrudHandlerPostgres:
    def _split_data(self, data: dict = {}) -> tuple:
        """Split argument data into two parts

        Args:
            data (dict, optional): [description]. Defaults to {}.

        Returns:
            tuple: Tuple of dictionares
        """
        if data != {}:
            try:
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
            except KeyError:
                post_data = {'UNIQUE_ID': data['UNIQUE_ID']}
                user_data = {}
        else:
            post_data = {}
            user_data = {}
        return post_data, user_data

    def _add_data(self, data: Union[list, dict] = {}) -> bool:
        """Insert method

        Args:
            data (Union[list, dict], optional): [description]. Defaults to {}.

        Returns:
            bool: [description]
        """
        success = False
        for post in data:
            cur.execute('SELECT * FROM post')
            if cur.rowcount < MAX_DB_POSTS:
                post_data, user_data = self._split_data(post)
                if user_data != {}:  # check an empty line
                    try:
                        sql_request = """
                            INSERT INTO profile (
                                username,
                                user_karma,
                                user_cake_day
                            )
                            VALUES (%s, %s, %s);
                            """
                        cur.execute(sql_request, (
                            user_data['username'],
                            user_data['user karma'],
                            user_data['user cake day'],)
                        )
                    except psycopg2.errors.UniqueViolation:
                        pass
                    try:
                        sql_request = """
                        SELECT id FROM profile WHERE username = %s;
                        """
                        cur.execute(sql_request, (user_data['username'],))
                        foreign_key = cur.fetchone()[0]
                        sql_request = """
                            INSERT INTO post (
                                user_id,
                                username,
                                UNIQUE_ID,
                                post_URL,
                                post_karma,
                                comment_karma,
                                post_date,
                                number_of_comments,
                                number_of_votes,
                                post_category
                            )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                        cur.execute(sql_request, (
                            foreign_key,
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
                    except psycopg2.errors.UniqueViolation:
                        success = True
                else:
                    try:
                        sql_request = """INSERT INTO post (UNIQUE_ID) VALUES (%s);"""
                        cur.execute(sql_request, (post_data['UNIQUE_ID'],))
                        success = True
                    except psycopg2.errors.UniqueViolation:
                        logging.error('Data exists')
            else:
                logging.warning(f'Max number of posts {MAX_DB_POSTS} achieved')
                break
        return success

    def _read_data(self, requested_id: str = '') -> list:
        """Read method

        Args:
            requested_id (str, optional): [description]. Defaults to ''.

        Returns:
            list: [description]
        """        
        response = []

        def _collect_data() -> dict:
            """Collects the data in a dict

            Returns:
                dict: [Post data for response]
            """                       
            collected_data = {}
            collected_data['UNIQUE_ID'] = result[1]
            collected_data['post URL'] = result[2]
            collected_data['post karma'] = result[3]
            collected_data['username'] = result[0]
            collected_data['user karma'] = result[9]
            collected_data['user cake day'] = result[10]
            collected_data['comment karma'] = result[4]
            collected_data['post date'] = result[5]
            collected_data['number of comments'] = result[6]
            collected_data['number of votes'] = result[7]
            collected_data['post category'] = result[8]
            return collected_data

        if requested_id == '':
            sql_request = """
            SELECT
                post.username,
                post.unique_id,
                post.post_url,
                post.post_karma,
                post.comment_karma,
                post.post_date,
                post.number_of_comments,
                post.number_of_votes,
                post.post_category,
                profile.user_karma,
                profile.user_cake_day
            FROM post
                LEFT JOIN profile
                    ON profile.id = post.user_id;
            """
            cur.execute(sql_request)
            results = cur.fetchall()
            for result in results:
                response.append(_collect_data())
        else:
            sql_request = """
            SELECT
                post.username,
                post.unique_id,
                post.post_url,
                post.post_karma,
                post.comment_karma,
                post.post_date,
                post.number_of_comments,
                post.number_of_votes,
                post.post_category,
                profile.user_karma,
                profile.user_cake_day
            FROM post
                LEFT JOIN profile
                    ON profile.id = post.user_id
            WHERE post.unique_id = %s;
            """
            cur.execute(sql_request, (requested_id,))
            result = cur.fetchone()
            response.append(_collect_data()) if result != None else response
        return response

    def _update_data(self, requested_id: str = '', data: dict = {}) -> list:
        """Update method

        Args:
            requested_id (str, optional): [description]. Defaults to ''.
            data (dict, optional): [description]. Defaults to {}.

        Returns:
            list: [description]
        """        
        response = []
        index_err = False
        if requested_id != '' and data != {}:
            for new_item_key in data.keys():
                if new_item_key == 'username': # update username one to many
                    try:
                        old_username = self._read_data(requested_id)[0]['username']
                        
                        sql_request = """
                        UPDATE post SET {} = %s WHERE username = %s;
                        """
                        cur.execute(sql_request.format(new_item_key), (data[new_item_key], old_username))
                        sql_request = """
                        UPDATE profile SET {} = %s WHERE username = %s;
                        """
                        cur.execute(sql_request.format(new_item_key), (data[new_item_key], old_username))
                    except IndexError:
                        index_err = True
                else:
                    try:
                        sql_request = """
                        UPDATE post SET {} = %s WHERE unique_id = %s;
                        """
                        cur.execute(sql_request.format(new_item_key), (data[new_item_key], requested_id))
                    except:
                        try:
                            sql_request = """
                            UPDATE profile SET {} = %s WHERE unique_id = %s;
                            """
                            cur.execute(sql_request.format(new_item_key), (data[new_item_key], requested_id))
                        except IndexError:
                            index_err = True
            if not index_err:
                response.append(self._read_data(requested_id))
        return response
            

    def _delete_data(self, requested_id: str = '') -> bool:
        """Delete method

        Args:
            requested_id (str, optional): [description]. Defaults to ''.

        Returns:
            bool: [description]
        """        
        success = False
        if requested_id != '':
            sql_request = """
            SELECT username FROM post WHERE unique_id = %s;
            """
            cur.execute(sql_request, (requested_id,))
            if cur.rowcount > 0:
                user = cur.fetchone()[0]
                sql_request = """
                SELECT * FROM post WHERE username = %s;
                """
                cur.execute(sql_request, (user,))
                if cur.rowcount > 1:
                    sql_request = """
                    DELETE FROM post WHERE UNIQUE_ID = %s;
                    """
                    cur.execute(sql_request, (requested_id,))
                    if cur.rowcount == 1:
                        success = True
                else:                
                    sql_request = """
                    DELETE FROM post WHERE UNIQUE_ID = %s;
                    DELETE FROM profile WHERE username = %s;
                    """
                    cur.execute(sql_request, (requested_id, user,))
                    if cur.rowcount == 1:
                        success = True
        return success

tables_obj = CreateTables()
