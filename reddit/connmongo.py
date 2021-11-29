import logging
from typing import Union, Tuple, Dict, List

from pymongo import MongoClient
from abstract import CrudHandlerAbs

MAX_DB_POSTS = 1000
HOST = 'localhost'
PORT = 27017

logging.basicConfig(level=logging.INFO)

client = MongoClient(HOST, PORT)
db = client['reddit']
post_collection = db.post
profile_collection = db.profile
if post_collection and profile_collection:
    logging.info('Mongo connected')


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
                    'username': data['username'],  # foreign key
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
            post_data, user_data = self._split_data(post)
            if post_collection.count_documents({}) < MAX_DB_POSTS:
                post_result = post_collection.update_one(
                    {'post URL': post['post URL']},
                    {'$set': post_data}, upsert=True)
                user_result = profile_collection.update_one({'username': post['username']},
                                                            {'$set': user_data}, upsert=True)
                if post_result.raw_result['n'] != 1 and user_result.raw_result['n'] != 1:
                    logging.error(
                        f"Post{post['post URL']} {post['username']} isn't inserted")
                else:
                    success = True
            else:
                logging.warning(
                    f'Max number of posts {MAX_DB_POSTS} achieved')
                break
        return success

    def _read_data(self, requested_id: str = '') -> List[Dict[str, Union[int, str]]]:
        """Read method

        The CRUD method which reads the data from db by UNIQUE_ID or without
        (all the data)

        @param requested_id: UNIQUE_ID to identify post to be read
        @return: A list of one requested post or all posts
        """
        response = []
        if not requested_id:
            posts_result = post_collection.find({})
            for post_result in posts_result:
                try:
                    collected_data = {
                        'UNIQUE_ID': post_result['UNIQUE_ID'],
                        'post URL': post_result['post URL'],
                        'post karma': post_result['post karma'],
                        'username': post_result['username'],
                        'user karma': profile_collection.find_one(
                            {'username': post_result['username']})['user karma'],
                        'user cake day': profile_collection.find_one(
                            {'username': post_result['username']})['user cake day'],
                        'comment karma': post_result['comment karma'],
                        'post date': post_result['post date'],
                        'number of comments': post_result['number of comments'],
                        'number of votes': post_result['number of votes'],
                        'post category': post_result['post category'],
                    }
                    response.append(collected_data)
                except KeyError:
                    logging.error('Read data error')
        else:
            try:
                post_result = post_collection.find_one(
                    {'UNIQUE_ID': requested_id})
                if post_result:
                    post_result.pop('_id')
                    post_result['user karma'] = profile_collection.find_one(
                        {'username': post_result['username']})['user karma']
                    post_result['user cake day'] = profile_collection.find_one(
                        {'username': post_result['username']})['user cake day']
                    response.append(post_result)
                else:
                    response = []
            except KeyError:
                logging.error('Read data error')
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
        if requested_id and data:
            post_result = post_collection.find_one(
                {'UNIQUE_ID': requested_id})
            user_result = profile_collection.find_one(
                {'username': post_result['username']})
            for new_item in data.keys():
                if new_item in post_result.keys():
                    new_post_result = post_collection.update_one({new_item: post_result[new_item]},
                                                                 {'$set': {new_item: data[new_item]}}, upsert=True)
                    if new_post_result.raw_result['n'] != 1:
                        break
                if new_item in user_result.keys():
                    if new_item == 'username':
                        posts_result = post_collection.find(
                            {'username': user_result['username']})
                        for post in posts_result:
                            username_result = post_collection.update_one({'username': post['username']},
                                                                         {'$set': {'username': data['username']}},
                                                                         upsert=True)
                            if username_result.raw_result['n'] != 1:
                                logging.error(
                                    f"Post{post_result['post URL']} {user_result['username']} isn't updated")
                                break
                    new_user_result = profile_collection.update_one({new_item: user_result[new_item]},
                                                                    {'$set': {new_item: data[new_item]}}, upsert=True)
                    if new_user_result.raw_result['n'] != 1:
                        break
            response = self._read_data(requested_id)
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
            post_result = post_collection.find_one({'UNIQUE_ID': requested_id})
            if post_result:
                if post_result.get('username'):
                    count_posts = post_collection.find(
                        {'username': post_result['username']}).count()
                    if count_posts == 1:
                        user_delete_result = profile_collection.delete_one(
                            {'username': post_result['username']})
                        if user_delete_result.deleted_count != 1:
                            logging.error(
                                f"{post_result['username']} isn't deleted")
                delete_result = post_collection.delete_one(
                    {'UNIQUE_ID': requested_id})
                if delete_result.deleted_count != 1:
                    logging.error(f"post {requested_id} isn't deleted")
                else:
                    success = True
        return success
