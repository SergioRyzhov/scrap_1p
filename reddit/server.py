import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Union

from connmongo import ItemsCrudHandler as Mongo
from connpostgre import ItemsCrudHandler as Postgres

HOST = 'localhost'
PORT = 8087

logging.basicConfig(level=logging.INFO)
logging.info('Server ran...')


class HttpProcessor(BaseHTTPRequestHandler):
    """Server class

    Accepts requests from the client, processes is and sends to work with the db.
    """

    def __init__(self):
        self.mongo_obj = Mongo()
        self.postgresql_obj = Postgres()

    def _load_data(self) -> Union[List[Dict[str, Union[str, int]]], Dict[str, Union[str, int]]]:
        """Load data method

        Loads parsed data from request, checks json format,
        decodes into dictionary.

        @return: Dictionary decoded from json.
        """
        try:
            length = int(self.headers.get('Content-Length'))
            load_data = json.loads(self.rfile.read(length))
        except (json.decoder.JSONDecodeError, TypeError):
            logging.error(
                'Wrong inputed data format, needs "{\"username\":\"one\"}"')
            load_data = {}
        return load_data

    def resp_text(self, error_code: int, data: str = '') -> None:
        """Text respond

        Accepts an error code and a string to be sent,
        forms a response and sends it to client.

        @param error_code: integer
        @param data: string [text to send to a client]
        @return: None
        """
        self.send_response(error_code, f'{error_code}')
        self.send_header('content-type', 'text/html')
        self.end_headers()
        if error_code in [404, 500]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(bytes(data, encoding='utf-8'))

    def resp_json(self, data: List[Dict[str, Union[str, int]]]) -> None:
        """Json respond

        Accepts an post or posts in a list of dictionaries,
        forms it and sends to client.

        @param data: post or posts
        @return: None
        """
        self.wfile.write(
            bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))

    def do_GET(self) -> None:
        """Get handler

        Receives GET requests, checks for a UNIQUE_ID in the request
        and sends it to the database handler.
        """
        try:
            if self.path == '/posts/':
                result = self.mongo_obj.read_data()
                result_2 = self.postgresql_obj.read_data()
                self.resp_json(result) if result or result_2 else self.resp_text(404)
            elif re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                result = self.mongo_obj.read_data(requested_id)
                result_2 = self.postgresql_obj.read_data(requested_id)
                self.resp_json(result) if result_2 or result else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server GET error')
            self.resp_text(500)

    def do_POST(self) -> None:
        """POST handler

        Receives POST requests with json data, sends to the database handler.
        """
        try:
            parsed_data = self._load_data()
            if not parsed_data:
                self.resp_text(404)
            else:
                if self.mongo_obj.add_data(parsed_data) and self.postgresql_obj.add_data(parsed_data):
                    self.resp_text(200, 'Parsed data successfully inserted')
                else:
                    self.resp_text(200, 'Parsed data isn\'t inserted')
        except:
            logging.error('Server POST error')
            self.resp_text(500)

    def do_DELETE(self) -> None:
        """DELETE handler

        Receives DELETE requests, checks for a UNIQUE_ID in the request
        and sends it to the database handler.
        """
        try:
            if re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                result = self.mongo_obj.delete_data(requested_id)
                result_2 = self.postgresql_obj.delete_data(requested_id)
                self.resp_text(
                    200, f'post {requested_id} deleted') if result and result_2 else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server DELETE error')
            self.resp_text(500)

    def do_PUT(self) -> None:
        """PUT handler

        Receives PUT requests with json data and UNIQUE_ID,
        sends to the database handler.
        """
        try:
            if re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                load_data = self._load_data()
                result = self.mongo_obj.update_data(requested_id, load_data)
                result_2 = self.postgresql_obj.update_data(requested_id, load_data)
                self.resp_json(result) if result and result_2 else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server PUT error')
            self.resp_text(500)


try:
    serv = HTTPServer((HOST, PORT), HttpProcessor)
    serv.serve_forever()
except:
    logging.error("The server isn't ran")
