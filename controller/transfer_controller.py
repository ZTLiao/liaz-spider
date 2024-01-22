import os

from fastapi import APIRouter, Request

from config.cos_config import CosConfig
from handler.resource_handler import download
from resp import response
from storage.file_item_db import FileItemDb

import system.global_vars
from utils.cos_util import CosUtil

router = APIRouter()


@router.get('/spider/transfer/upload')
def upload(request: Request):
    resource_url = 'http://' + request.query_params.get('resource_url')
    cos: CosConfig = system.global_vars.systemConfig.get_cos()
    util = CosUtil(cos.secret_id, cos.secret_key, cos.bucket_name, cos.region)
    file_item_db = FileItemDb()
    page_num = 1
    page_size = 20
    while True:
        data = file_item_db.list(page_num, page_size)
        if len(data) == 0:
            break
        for item in data:
            try:
                path = item['path']
                print('path : ', path)
                filename = download(resource_url + path)
                util.put_object(filename, path)
                os.remove(filename)
            except Exception as e:
                print(e)
        page_num += 1
    return response.ok()
