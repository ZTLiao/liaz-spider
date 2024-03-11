import pymysql
import logging
import sys

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class CleanUtil:

    def __init__(self):
        self.__mysql_host = None
        self.__mysql_port = None
        self.__mysql_username = None
        self.__mysql_password = None
        self.__mysql_db = None
        self.__cos_secret_id = None
        self.__cos_secret_key = None
        self.__cos_bucket_name = None
        self.__cos_region = None

    def set_mysql(self, host, port, username, password, db):
        self.__mysql_host = host
        self.__mysql_port = port
        self.__mysql_username = username
        self.__mysql_password = password
        self.__mysql_db = db

    def set_cos(self, secret_id, secret_key, bucket_name, region):
        self.__cos_secret_id = secret_id
        self.__cos_secret_key = secret_key
        self.__cos_bucket_name = bucket_name
        self.__cos_region = region

    def get_path_page(self, page_num: int, page_size: int):
        conn = pymysql.connect(
            host=self.__mysql_host,
            port=int(self.__mysql_port),
            user=self.__mysql_username,
            password=self.__mysql_password,
            db=self.__mysql_db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select path from file_item where status = 0 order by file_id limit ' + str(
            (page_num - 1) * page_size) + ', ' + str(page_size))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = []
        return result

    def clean_cos(self):
        print('==== clean cos start ====')
        page_num = 1
        page_size = 200
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        config = CosConfig(Region=self.__cos_region, SecretId=self.__cos_secret_id, SecretKey=self.__cos_secret_key,
                           Token=None)
        cos_client = CosS3Client(config)
        while True:
            try:
                paths = self.get_path_page(page_num, page_size)
                if paths is None or len(paths) == 0:
                    break
                for path in paths:
                    print('path : ', path)
                    response = cos_client.delete_object(Bucket=self.__cos_bucket_name, Key=path)
                    print('response : ', response)
            except Exception as e:
                print(e)
            page_num += 1
        print('==== clean cos end ====')


if __name__ == '__main__':
    util = CleanUtil()
    util.set_mysql('106.53.194.238', '3306', 'root', 'NGQGWZtGRbDhHahS', 'liaz')
    util.set_cos('AKIDb0lVFW6eG6mDh6Mj2FRj5Pgx8EFIFD9B', 'EHKF4oU3d6UoYDhwBGPViwxobI2kN6mY', 'liaz-1301617869',
                 'ap-guangzhou')
    util.clean_cos()
