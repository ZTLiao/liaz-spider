import logging
import sys

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class CosUtil:
    def __init__(self, secret_id, secret_key, bucket_name, region):
        self.bucket_name = bucket_name
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=None)
        self.__client = CosS3Client(config)

    def put_object(self, filename, unique_id):
        with open(filename, 'rb') as fp:
            response = self.__client.put_object(
                Bucket=self.bucket_name,
                Body=fp,
                Key=unique_id,
                StorageClass='STANDARD',
                EnableMD5=False
            )
        print(response['ETag'])
