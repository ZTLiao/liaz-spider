from fastapi import APIRouter, Request

from resp import response
from spiders.dongmanla_spider import DongManLaSpider
from spiders.shuhuangwang_spider import ShuHuangWangSpider

router = APIRouter()


@router.get('/spider/execute')
def spider(request: Request):
    resource_url = 'http://8.134.215.58'
    username = 'liaozetao'
    password = 'e10adc3949ba59abbe56e057f20f883e'
    script_name = request.query_params.get('script')
    if script_name == 'dongmanla':
        DongManLaSpider(resource_url, username, password, 1).parse()
    if script_name == 'shuhuangwang':
        ShuHuangWangSpider(resource_url, username, password).parse()
    return response.ok()
