import os
import re
import json
import uuid
import logging

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


PATH = os.environ.get('CHROME_DRIVER')

HOST = 'localhost'

PORT = 8087

logging.basicConfig(level=logging.INFO)


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
                logging.info('File written seccessfully')
            except:
                logging.error('Writefile error')
                
    def resp(self, error_code, param1, param2):
        """Reduces the number of header send"""
        self.send_response(error_code)
        self.send_header(param1, param2)
        self.end_headers()
        if error_code in [400, 401, 404]:
            self.wfile.write(bytes(f'{error_code}', encoding='utf-8'))
                
    def do_GET(self):
        """Handle get requests"""
        if self.path == '/posts/' and self.current_data:
            self.resp(200, 'content-type', 'application/json')
            self.wfile.write(bytes(json.dumps(self.current_data, ensure_ascii=False), 'utf-8'))
        elif re.findall(r'/posts/\S+', self.path) and self.current_data:
            self.resp(200, 'content-type', 'text/html')
            path = self.path.replace('/posts/', '')
            for item in self.current_data:
                if path == item['UNIQUE_ID']:
                    self.wfile.write(bytes(';'.join([str(value) for value in item.values()]), 'utf-8'))
        else:
            self.resp(404, 'content-type', 'text/html')

    def do_POST(self):
        """Handle post requests"""
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
                        self.resp(201, 'content-type', 'application/json')
                        self.wfile.write(bytes(json.dumps({new_item['UNIQUE_ID']: len(self.current_data) - 1}, ensure_ascii=False), 'utf-8'))
                        self.save_file(self.current_data)
                        break
            else:
                HttpProcessor.current_data.append({'UNIQUE_ID': str(uuid.uuid1())})
                self.resp(404, 'content-type', 'application/json')
                self.wfile.write(bytes(json.dumps({self.current_data[0]['UNIQUE_ID']: 0}, ensure_ascii=False), 'utf-8'))
                self.save_file(self.current_data)
        else:        
            self.resp(200, 'content-type', 'application/json')
            length = int(self.headers.get('Content-Length'))
            HttpProcessor.current_data = json.loads(self.rfile.read(length))
            self.save_file(self.current_data)
    
    def do_DELETE(self):
        if re.findall(r'/posts/\S+', self.path) and self.current_data:
            self.resp(200, 'content-type', 'text/html')
            path = self.path.replace('/posts/', '')
            for item in self.current_data:
                if path == item['UNIQUE_ID']:
                    self.current_data.pop(self.current_data.index(item))
            self.save_file(self.current_data)
        else:
            self.resp(404, 'content-type', 'text/html')
            
    def do_PUT(self):
        if re.findall(r'/posts/\S+', self.path) and self.current_data:
            self.resp(200, 'content-type', 'text/html')
            path = self.path.replace('/posts/', '')
            for item in self.current_data:
                if path == item['UNIQUE_ID']:
                    self.current_data.pop(self.current_data.index(item))
            self.save_file(self.current_data)
        else:
            self.resp(404, 'content-type', 'text/html')
        


serv = HTTPServer((HOST, PORT), HttpProcessor)
serv.serve_forever()
