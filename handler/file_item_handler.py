import os
import time
import uuid

import requests

import system.global_vars
from config.cos_config import CosConfig
from storage.file_item_db import FileItemDb
from utils.cos_util import CosUtil


class FileItemHandler:
    def __init__(self):
        cos: CosConfig = system.global_vars.systemConfig.get_cos()
        self.__cos_util = CosUtil(cos.secret_id, cos.secret_key, cos.bucket_name, cos.region)
        self.__file_item_db = FileItemDb()
        self.filename = None

    def upload(self, bucket_name, filename, file_type):
        self.filename = filename
        suffix = ''
        array = filename.split('.')
        if len(array) > 1:
            suffix = array[1]
        unique_id = int(round(time.time() * 1000))
        path = '/' + bucket_name + '/' + str(unique_id)
        try:
            size = os.path.getsize(filename)
            e_tag = self.__cos_util.put_object(filename, path)
            if e_tag is not None:
                self.__file_item_db.save(bucket_name, filename, size, path, unique_id, suffix, file_type)
        except Exception as e:
            print(e)
        finally:
            os.remove(filename)
        return path

    def download(self, url):
        suffix = ''
        array = url.split('.')
        if len(array) > 1:
            suffix = array[len(array) - 1]
        self.filename = str(uuid.uuid4())
        if suffix != '':
            self.filename = self.filename + '.' + suffix
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(self.filename, 'wb') as f:
                    f.write(response.content)
            else:
                self.filename = None
                print('download failed, ', url)
        except Exception as e:
            self.filename = None
            print(e)
        return self.filename

    def write_content(self, content):
        content = content.encode(encoding='utf-8')
        self.filename = str(uuid.uuid4()) + '.txt'
        try:
            with open(self.filename, 'wb') as f:
                f.write(content)
        except Exception as e:
            self.filename = None
            print(e)
        return self.filename
