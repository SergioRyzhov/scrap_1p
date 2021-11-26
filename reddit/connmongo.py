import logging
from typing import Union

from pymongo import MongoClient

MAX_DB_POSTS = 1000
HOST = 'localhost'
PORT = 27017


logging.basicConfig(level=logging.INFO)

client = MongoClient(HOST, PORT)
db = client['reddit']
post_collection = db.post
user_collection = db.profile
if post_collection and user_collection:
    logging.info('Mongo connected')


class ItemsCrudHandler:
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
        if type(data) == list:
            for post in data:
                post_data, user_data = self._split_data(post)
                if post_collection.count_documents({}) < MAX_DB_POSTS:
                    if user_data != {}:  # check an empty line
                        post_result = post_collection.update_one(
                            {'post URL': post['post URL']},
                                                                 {'$set': post_data}, upsert=True)
                        user_result = user_collection.update_one({'username': post['username']},
                                                                 {'$set': user_data}, upsert=True)
                        if post_result.raw_result['n'] != 1 and user_result.raw_result['n'] != 1:
                            logging.error(
                                f"Post{post['post URL']} {post['username']} isn't inserted")
                        else:
                            success = True
                    else:  # insert an empty line
                        post_result = post_collection.update_one({'UNIQUE_ID': data[0]['UNIQUE_ID']},
                                                                 {'$set': post_data}, upsert=True)
                        if post_result.raw_result['n'] != 1:
                            logging.error(
                                f"Post{post['UNIQUE_ID']} isn't inserted")
                        else:
                            success = True
                else:
                    logging.warning(
                        f'Max number of posts {MAX_DB_POSTS} achieved')
                    break
        else:
            post_data, user_data = self._split_data(data)
            if post_collection.count_documents({}) < MAX_DB_POSTS:
                post_result = post_collection.update_one({'post URL': data['post URL']},
                                                         {'$set': post_data}, upsert=True)
                user_result = user_collection.update_one({'username': data['username']},
                                                         {'$set': user_data}, upsert=True)
                if post_result.raw_result['n'] != 1 and user_result.raw_result['n'] != 1:
                    logging.error(
                        f"Post{data['post URL']} {data['username']} isn't inserted")
                else:
                    success = True
            else:
                logging.warning(
                    f'Max number of posts {MAX_DB_POSTS} achieved')
        return success

    def _read_data(self, requested_id: str = '') -> list:
        """Read method

        Args:
            requested_id (str): [description]

        Returns:
            List: [description]
        """
        responce = []
        if requested_id == '':
            posts_result = post_collection.find({})
            for post_result in posts_result:
                collected_data = {}
                try:
                    collected_data['UNIQUE_ID'] = post_result['UNIQUE_ID']
                    collected_data['post URL'] = post_result['post URL']
                    collected_data['post karma'] = post_result['post karma']
                    collected_data['username'] = post_result['username']
                    collected_data['user karma'] = user_collection.find_one(
                        {'username': post_result['username']})['user karma']
                    collected_data['user cake day'] = user_collection.find_one(
                        {'username': post_result['username']})['user cake day']
                    collected_data['comment karma'] = post_result['comment karma']
                    collected_data['post date'] = post_result['post date']
                    collected_data['number of comments'] = post_result['number of comments']
                    collected_data['number of votes'] = post_result['number of votes']
                    collected_data['post category'] = post_result['post category']
                    responce.append(collected_data)
                except KeyError:
                    collected_data['UNIQUE_ID'] = post_result['UNIQUE_ID']
                    responce.append(collected_data)
        else:
            try:
                post_result = post_collection.find_one(
                    {'UNIQUE_ID': requested_id})
                if post_result:
                    post_result.pop('_id')
                    post_result['user karma'] = user_collection.find_one(
                        {'username': post_result['username']})['user karma']
                    post_result['user cake day'] = user_collection.find_one(
                        {'username': post_result['username']})['user cake day']
                    responce.append(post_result)
                else:
                    responce = []
            except KeyError:
                responce.append({'UNIQUE_ID': post_collection.find_one(
                    {'UNIQUE_ID': requested_id})['UNIQUE_ID']})
        return responce

    def _update_data(self, requested_id: str = '', data: dict = {}) -> list:
        """Update method

        Args:
            requested_id (str, optional): [description]. Defaults to ''.
            data (dict, optional): [description]. Defaults to {}.

        Returns:
            list: [description]
        """
        response = []
        if requested_id != '' and data != {}:
            post_result = post_collection.find_one(
                {'UNIQUE_ID': requested_id})
            user_result = user_collection.find_one(
                {'username': post_result['username']})
            for new_item in data.keys():
                if new_item in post_result.keys():
                    new_post_result = post_collection.update_one({new_item: post_result[new_item]},
                                                                 {'$set': {new_item: data[new_item]}}, upsert=True)
                    if new_post_result.raw_result['n'] != 1:
                        logging.error(
                            f"Post{post_result['post URL']} {user_result['username']} isn't updated")
                        break
                if new_item in user_result.keys():
                    if new_item == 'username':
                        posts_result = post_collection.find(
                            {'username': user_result['username']})
                        for post in posts_result:
                            username_result = post_collection.update_one({'username': post['username']},
                                                                         {'$set': {'username': data['username']}}, upsert=True)
                            if username_result.raw_result['n'] != 1:
                                logging.error(
                                    f"Post{post_result['post URL']} {user_result['username']} isn't updated")
                                break
                    new_user_result = user_collection.update_one({new_item: user_result[new_item]},
                                                                 {'$set': {new_item: data[new_item]}}, upsert=True)
                    if new_user_result.raw_result['n'] != 1:
                        logging.error(
                            f"Post{post_result['post URL']} {user_result['username']} isn't updated")
                        break
            response = self._read_data(requested_id)
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
            post_result = post_collection.find_one({'UNIQUE_ID': requested_id})
            if post_result:
                if post_result.get('username'):
                    count_posts = post_collection.find(
                        {'username': post_result['username']}).count()
                    if count_posts == 1:
                        user_delete_result = user_collection.delete_one(
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
