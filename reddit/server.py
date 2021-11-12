import os
import re
import json
import uuid

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


PATH = os.environ.get('CHROME_DRIVER')

HOST = 'localhost'

PORT = 8087


class HttpProcessor(BaseHTTPRequestHandler):
    current_data = []

    def save_file(self, items):
        """Creates reddit-YYYYMMDD.txt file and dumps the data"""
        with open(f'{PATH}/reddit-{datetime.now().strftime("%Y%m%d")}.txt', 'w', newline='', encoding='utf-8') as fw:
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
            except:
                self.resp_text(200, b'Writefile error')

    def resp_text(self, error_code, data=b''):
        """Reduces the number of header send"""
        self.send_response(error_code, f'{error_code}')
        self.send_header('content-type', 'text/html')
        self.end_headers()
        if error_code in [400, 401, 404, 500]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(data)

    def resp_json(self, error_code, data):
        """Reduces the number of header send"""
        self.send_response(error_code)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        if error_code in [400, 401, 404]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
        else:
            self.wfile.write(
                bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))

    def do_GET(self):
        """Handle get requests"""
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
        except:
            self.resp_text(500)

    def do_POST(self):
        """Handle post requests"""
        try:
            if self.path == '/posts/':
                if self.current_data:
                    while True:
                        trigger = True
                        new_item = {'UNIQUE_ID': str(uuid.uuid1())}
                        for item in self.current_data:
                            if new_item['UNIQUE_ID'] == item['UNIQUE_ID']:
                                trigger = False
                                break
                        if trigger:
                            self.current_data.append(new_item)
                            self.resp_json(
                                201, {new_item['UNIQUE_ID']: len(self.current_data) - 1})
                            self.save_file(self.current_data)
                            break
                else:
                    HttpProcessor.current_data.append(
                        {'UNIQUE_ID': str(uuid.uuid1())})
                    self.resp_json(200, {self.current_data[0]['UNIQUE_ID']: 0})
                    self.save_file(self.current_data)
            else:
                length = int(self.headers.get('Content-Length'))
                HttpProcessor.current_data = json.loads(
                    self.rfile.read(length))
                self.resp_json(200, self.current_data)
                self.save_file(self.current_data)
        except:
            self.resp_text(500)

    def do_DELETE(self):
        try:
            if re.findall(r'/posts/\S+', self.path) and self.current_data:
                path = self.path.replace('/posts/', '')
                trigger = True
                for item in self.current_data:
                    if path == item['UNIQUE_ID']:
                        self.current_data.pop(self.current_data.index(item))
                        self.save_file(self.current_data)
                        self.resp_json(200, self.current_data)
                        trigger = False
                if trigger:
                    self.resp_text(200)
            else:
                self.resp_text(404)
        except:
            self.resp_text(500)

    def do_PUT(self):
        try:
            if re.findall(r'/posts/\S+', self.path) and self.current_data:
                path = self.path.replace('/posts/', '')
                trigger = True
                for item in self.current_data:
                    if path == item['UNIQUE_ID']:
                        length = int(self.headers.get('Content-Length'))
                        obtained_data = json.loads(self.rfile.read(length))
                        for key in item.keys():
                            for key_obt in obtained_data.keys():
                                if key_obt == key:
                                    item.update(
                                        {key_obt: obtained_data[key_obt]})
                                    self.resp_json(200, self.current_data)
                                    self.save_file(self.current_data)
                                    trigger = False
                if trigger:
                    self.resp_text(200)
            else:
                self.resp_text(404)
        except:
            self.resp_text(500)


serv = HTTPServer((HOST, PORT), HttpProcessor)
serv.serve_forever()
