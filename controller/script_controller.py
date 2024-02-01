from fastapi import APIRouter, Request

from resp import response
from spiders.dongmanla_spider import DongManLaSpider
from spiders.dongmanzhijia_spider import DongManZhiJiaSpider
from spiders.shuhuangwang_spider import ShuHuangWangSpider

router = APIRouter()


@router.get('/spider/script/execute')
def execute(request: Request):
    script = request.query_params.get('script')
    page_type = request.query_params.get('page_type')
    if page_type is None:
        page_type = 0
    if script == 'dongmanla':
        DongManLaSpider(page_type).parse()
    if script == 'shuhuangwang':
        ShuHuangWangSpider(page_type).parse()
    if script == 'dongmanzhijia':
        spider = DongManZhiJiaSpider()
        if page_type == '0':
            spider.parse()
        elif page_type == '1':
            pass
    return response.ok()
