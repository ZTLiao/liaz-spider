import json
import os
import uuid

import requests


class ResourceHandler:
    def __init__(self, domain, username, password):
        self.__domain = domain
        self.__username = username
        self.__password = password
        self.__token = None

    def login(self):
        try:
            response = requests.post(url=self.__domain + '/admin/login', data={
                'username': self.__username,
                'password': self.__password
            }, timeout=30)
            if response.status_code == 200:
                json_obj = json.loads(response.content)
                self.__token = json_obj['data']['accessToken']
        except Exception as e:
            print(e)

    def upload(self, bucket_name, filename):
        self.login()
        path = None
        try:
            url = self.__domain + '/admin/upload/' + bucket_name
            with open(filename, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, headers={
                    'Authorization': self.__token
                }, files=files)
                if response.status_code == 200:
                    json_obj = json.loads(response.content)
                    path = json_obj['data']['path']
                    os.remove(filename)
                else:
                    print('upload failed, ', filename)
        except Exception as e:
            print(e)
        return path


def download(url):
    filename = str(uuid.uuid4())
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            filename = None
            print('download failed, ', url)
    except Exception as e:
        filename = None
        print(e)
    return filename


def write_note(content):
    content = content.encode(encoding='utf-8')
    filename = str(uuid.uuid4()) + '.txt'
    try:
        with open(filename, 'wb') as f:
            f.write(content)
    except Exception as e:
        filename = None
        print(e)
    return filename
