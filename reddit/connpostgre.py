import argparse
import logging
from typing import Union, Tuple, Dict, List
from abstract import CrudHandlerAbs
import psycopg2

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

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS profile (
            id serial UNIQUE NOT NULL PRIMARY KEY,
            username varchar(150) UNIQUE,
            user_karma int,
            user_cake_day varchar(255)
        );
    """
)
if cur.rowcount > 0:
    logging.info('Table profile created successfully')
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS post (
            id serial UNIQUE NOT NULL PRIMARY KEY,
            user_id int,
            UNIQUE_ID varchar(150) UNIQUE NOT NULL,
            post_URL text UNIQUE,
            post_karma int,
            comment_karma int,
            post_date varchar(255),
            number_of_comments varchar(150),
            number_of_votes varchar(30),
            post_category varchar(255),
            CONSTRAINT post_profile_user_id_fk
                FOREIGN KEY (user_id)
                    REFERENCES profile (id) ON DELETE CASCADE
        );
    """
)
if cur.rowcount > 0:
    logging.info('Table post created successfully')


class ItemsCrudHandler(CrudHandlerAbs):
    """CRUD class

    It handles the data received from the server according to the CRUD methods
    """

    @staticmethod
    def _split_data(data: Dict[str, Union[int, str]] = {}) \
            -> Tuple[Dict[str, Union[int, str]], Dict[str, Union[int, str]]]:
        """Method splits parsed data for two tables, post and profile

        @param data: Parsed data from json
        @return: Data split into two tables, post and profile
        """
        if data:
            try:
                post_data = {
                    'UNIQUE_ID': data['UNIQUE_ID'],
                    'post URL': data['post URL'],
                    'post karma': data['post karma'],
                    'comment karma': data['comment karma'],
                    'post date': data['post date'],
                    'number of comments': data['number of comments'],
                    'number of votes': data['number of votes'],
                    'post category': data['post category'],
                }
                profile_data = {
                    'username': data['username'],
                    'user karma': data['user karma'],
                    'user cake day': data['user cake day'],
                }
            except KeyError:
                post_data = {}
                profile_data = {}
        else:
            post_data = {}
            profile_data = {}
        return post_data, profile_data

    def _add_data(self, data: List[Dict[str, Union[int, str]]] = {}) -> bool:
        """Add method

        One of the CRUD method which creates data in db

        @param data: Parsed data from json
        @return: Returns the result of an insert operation, True or False
        """
        success = False
        for post in data:
            cur.execute('SELECT * FROM post')
            if cur.rowcount < MAX_DB_POSTS:
                post_data, user_data = self._split_data(post)
                try:
                    sql_request_add = """
                        INSERT INTO profile (
                            username,
                            user_karma,
                            user_cake_day
                        )
                        VALUES (%s, %s, %s);
                        """
                    cur.execute(sql_request_add, (
                        user_data['username'],
                        user_data['user karma'],
                        user_data['user cake day'],)
                                )
                except psycopg2.errors.UniqueViolation:
                    pass
                try:
                    sql_request_add = """
                    SELECT id FROM profile WHERE username = %s;
                    """
                    cur.execute(sql_request_add, (user_data['username'],))
                    foreign_key = cur.fetchone()[0]
                    sql_request_add = """
                        INSERT INTO post (
                            user_id,
                            UNIQUE_ID,
                            post_URL,
                            post_karma,
                            comment_karma,
                            post_date,
                            number_of_comments,
                            number_of_votes,
                            post_category
                        )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                    cur.execute(sql_request_add, (
                        foreign_key,
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
                logging.warning(f'Max number of posts {MAX_DB_POSTS} achieved')
                break
        return success

    @staticmethod
    def _collect_data(result: Tuple[Union[int, str]]) -> Dict[str, Union[int, str]]:
        """Collects the data read from the database to send in a response

        @param result: A tuple of data read from the database
        @return: Dictionary parsed from a tuple
        """
        collected_data = {
            'UNIQUE_ID': result[1],
            'post URL': result[2],
            'post karma': result[3],
            'username': result[0],
            'user karma': result[9],
            'user cake day': result[10],
            'comment karma': result[4],
            'post date': result[5],
            'number of comments': result[6],
            'number of votes': result[7],
            'post category': result[8],
        }
        return collected_data

    def _read_data(self, requested_id: str = '') -> List[Dict[str, Union[int, str]]]:
        """Read method

        The CRUD method which reads the data from db by UNIQUE_ID or without
        (all the data)

        @param requested_id: UNIQUE_ID to identify post to be read
        @return: A list of one requested post or all posts
        """
        response = []
        sql_request_read = """
                    SELECT
                        profile.username,
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
                        INNER JOIN profile
                            ON profile.id = post.user_id
                    """
        if not requested_id:
            cur.execute(sql_request_read)
            results = cur.fetchall()
            for result in results:
                response.append(self._collect_data(result))
        else:
            sql_request_read = sql_request_read + f"WHERE post.unique_id = '{requested_id}';"
            cur.execute(sql_request_read)
            result = cur.fetchone()
            response.append(self._collect_data(result)) if result is not None else response
        return response

    def _update_data(self, requested_id: str = '', data: Dict[str, Union[int, str]] = {}) \
            -> list[Dict[str, Union[int, str]]]:
        """Update method

        The CRUD method which updates the data in the db by UNIQUE_ID

        @param requested_id: UNIQUE_ID to identify post to be update
        @param data: Dictionary containing data for updating fields
        @return: The post that was updated
        """
        response = []
        success = False
        if requested_id and data:
            for new_item_key in data.keys():
                try:
                    sql_request_update = """
                    UPDATE post SET {} = %s WHERE unique_id = %s;
                    """
                    cur.execute(sql_request_update.format(new_item_key), (data[new_item_key], requested_id))
                except psycopg2.errors.UndefinedColumn:
                    sql_request_update = """
                    SELECT user_id FROM post WHERE unique_id = %s;
                    """
                    cur.execute(sql_request_update, (requested_id,))
                    if cur.rowcount == 1:
                        user_id = cur.fetchone()[0]
                        sql_request_update = """
                        UPDATE profile SET {} = %s WHERE id = %s;
                        """
                        cur.execute(sql_request_update.format(new_item_key), (data[new_item_key], user_id))
                        if cur.rowcount == 1:
                            success = True
                response.append(self._read_data(requested_id)) if success else response
        return response

    @staticmethod
    def _delete_data(requested_id: str = '') -> bool:
        """Delete method

        The CRUD method which deletes the data in the db by UNIQUE_ID

        @param requested_id: UNIQUE_ID to identify post to be delete
        @return: Returns the result of an delete operation, True or False
        """
        success = False
        if requested_id:
            sql_request_delete = """
            SELECT user_id FROM post WHERE unique_id = %s;
            """
            cur.execute(sql_request_delete, (requested_id,))
            if cur.rowcount > 0:
                user_id = cur.fetchone()[0]
                sql_request_select = """
                SELECT * FROM post WHERE user_id = %s;
                """
                sql_request_delete = """
                DELETE FROM post WHERE UNIQUE_ID = %s;
                """
                cur.execute(sql_request_select, (user_id,))
                if cur.rowcount > 1:
                    cur.execute(sql_request_delete, (requested_id,))
                    if cur.rowcount == 1:
                        success = True
                else:
                    sql_request_delete = sql_request_delete + \
                                         f"DELETE FROM profile WHERE id = {user_id};"
                    cur.execute(sql_request_delete, (requested_id,))
                    if cur.rowcount == 1:
                        success = True
        return success
