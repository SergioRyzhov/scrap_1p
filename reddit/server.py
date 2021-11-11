import os
import json
import logging

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


PATH = os.environ.get('CHROME_DRIVER')

HOST = 'localhost'

PORT = 8087

logging.basicConfig(level=logging.INFO)


class HttpProcessor(BaseHTTPRequestHandler):
    def __init__(self):
        self.data = []
    
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
                logging.info('File written seccessfully')
            except:
                logging.error('Writefile error')

    def do_GET(self):
        """Handle get requests"""
        self.send_response(200, 'ok')
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'respond')
        # print(self.headers)

    def do_POST(self):
        """Handle post requests"""
        self.send_response(200, 'ok')
        self.send_header('content-type', 'application/json')
        self.end_headers()
        length = int(self.headers.get('Content-Length'))
        self.data = json.loads(self.rfile.read(length))
        print(self.data)


serv = HTTPServer((HOST, PORT), HttpProcessor)
serv.serve_forever()
