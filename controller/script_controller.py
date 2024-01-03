from fastapi import APIRouter, Request

from resp import response
from spiders.dongmanla_spider import DongManLaSpider
from spiders.shuhuangwang_spider import ShuHuangWangSpider

router = APIRouter()


@router.get('/script/execute')
def execute(request: Request):
    script = request.query_params.get('script')
    resource_url = request.query_params.get('resource_url')
    username = request.query_params.get('username')
    password = request.query_params.get('password')
    page_type = request.query_params.get('page_type')
    if page_type is None:
        page_type = 0
    if script == 'dongmanla':
        DongManLaSpider(resource_url, username, password, page_type).parse()
    if script == 'shuhuangwang':
        ShuHuangWangSpider(resource_url, username, password, page_type).parse()
    return response.ok()
