import json
import logging
import re
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List

from connmongo import ItemsCrudHandler as mongo
from connpostgre import ItemsCrudHandlerPostgres as postgres

HOST = 'localhost'
PORT = 8087

logging.basicConfig(level=logging.INFO)
logging.info('Server ran...')


class HttpProcessor(BaseHTTPRequestHandler):

    def _load_data(self) -> dict:
        """Gets data from a client

        Returns:
            dict: [description]
        """
        try:
            length = int(self.headers.get('Content-Length'))
            load_data = json.loads(self.rfile.read(length))
        except (json.decoder.JSONDecodeError, TypeError):
            logging.error(
                'Wrong inputed data format, needs "{\"username\":\"one\"}"')
            load_data = {}
        return load_data

    def resp_text(self, error_code: int, data='') -> None:
        """Sends the text respond
        """
        self.send_response(error_code, f'{error_code}')
        self.send_header('content-type', 'text/html')
        self.end_headers()
        if error_code in [404, 500]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(bytes(data, encoding='utf-8'))

    def resp_json(self, error_code: int, data: List[Dict]) -> None:
        """Sends the json respond
        """
        self.wfile.write(
            bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))

    def do_GET(self) -> None:
        """Handles get requests
        """
        try:
            if self.path == '/posts/':
                result = mongo()._read_data()
                result = postgres()._read_data()
                self.resp_json(200, result) if result != [
                ] else self.resp_text(404)
            elif re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                result = mongo()._read_data(requested_id)
                result = postgres()._read_data(requested_id)
                self.resp_json(200, result) if result != [
                ] else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server GET error')
            self.resp_text(500)

    def do_POST(self) -> None:
        """Handles post requests or adds new empty record
        """
        try:
            if self.path == '/posts/':
                gen_uuid = str(uuid.uuid1())
                if mongo()._add_data([{'UNIQUE_ID': gen_uuid}]):
                    self.resp_json(201, {'UNIQUE_ID': gen_uuid})
                    self.resp_text(
                        201, 'Empty data successfully inserted in mongo')
                else:
                    self.resp_text(
                        201, 'Empty data isn\'t inserted in mongo')
                if postgres()._add_data([{'UNIQUE_ID': gen_uuid}]):
                    self.resp_json(201, {'UNIQUE_ID': gen_uuid})
                    self.resp_text(
                        201, 'Empty data successfully inserted in mongo')
                else:
                    self.resp_text(
                        201, 'Empty data isn\'t inserted in mongo')
            else:
                parsed_data = self._load_data()
                if parsed_data == {}:
                    self.resp_text(404)
                else:
                    if mongo()._add_data(parsed_data):
                        self.resp_text(
                            200, 'Parsed data successfully inserted in mongo')
                    else:
                        self.resp_text(
                            200, 'Parsed data isn\'t inserted in mongo')
                    if postgres()._add_data(parsed_data):
                        self.resp_text(
                            200, 'Empty data successfully inserted in mongo')
                    else:
                        self.resp_text(
                            200, 'Empty data isn\'t inserted in mongo')

        except:
            logging.error('Server POST error')
            self.resp_text(500)

    def do_DELETE(self) -> None:
        """Handles delete requests. Delete element by uuid
        """
        try:
            if re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                result = mongo()._delete_data(requested_id)
                result_2 = postgres()._delete_data(requested_id)
                self.resp_text(
                    200, f'post {requested_id} deleted') if result or result_2 \
                    else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server DELETE error')
            self.resp_text(500)

    def do_PUT(self) -> None:
        """Handles put requests with json. Update element by uuid.
        """
        try:
            if re.findall(r'/posts/\S+', self.path):
                requested_id = self.path.replace('/posts/', '')
                load_data = self._load_data()
                result = mongo()._update_data(requested_id, load_data)
                result_2 = postgres()._update_data(requested_id, load_data)
                self.resp_json(200, result) if result != [
                ] or result_2 != [] else self.resp_text(404)
            else:
                self.resp_text(404)
        except:
            logging.error('Server PUT error')
            self.resp_text(500)


try:
    serv = HTTPServer((HOST, PORT), HttpProcessor)
    serv.serve_forever()
except Exception as err:
    logging.error(f"{err}. "+"The server isn't ran")
