import system.global_vars

from urllib.parse import unquote

from fastapi import APIRouter, Request

from constants import status
from resp import response
from spiders.acgnbus_spider import AcgNBusSpider
from spiders.baozimh_spider import BaoZiMhSpider
from spiders.bilinovel_spider import BiliNovelSpider
from spiders.cartoonmad_spider import CartoonMadSpider
from spiders.cn_baozimh_spider import CnBaoZiMhSpider
from spiders.colamanga_spider import ColaMangaSpider
from spiders.copymanga_spider import CopyMangaSpider
from spiders.dongmanla_spider import DongManLaSpider
from spiders.dongmanzhijia_spider import DongManZhiJiaSpider
from spiders.fanqie_spider import FanQieSpider
from spiders.hentai321_spider import HenTai321Spider
from spiders.manhuadb_spider import ManHuaDbSpider
from spiders.picyy177_spider import PicYY177Spider
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
        DongManZhiJiaSpider(page_type).parse()
    if script == 'cartoonmad':
        CartoonMadSpider().parse()
    if script == 'colamanga':
        ColaMangaSpider(page_type).parse()
    if script == 'baozimh':
        BaoZiMhSpider().parse()
    if script == 'fanqie':
        FanQieSpider().parse()
    if script == 'copymanga':
        CopyMangaSpider(page_type).parse()
    if script == 'bilinovel':
        BiliNovelSpider(page_type).parse()
    if script == 'manhuadb':
        ManHuaDbSpider().parse()
    if script == 'hentai321':
        HenTai321Spider().parse()
    if script == 'picyy177':
        PicYY177Spider().parse()
    if script == 'comic_upgrade_job':
        CopyMangaSpider().upgrade_job()
    if script == 'cn_baozimh':
        CnBaoZiMhSpider().parse()
    if script == 'acgnbus':
        AcgNBusSpider().parse()
    return response.ok()


@router.get('/spider/script/close')
def close():
    system.global_vars.application.set_close_status(status.YES)
    return response.ok()


@router.get('/spider/script/search')
def search(request: Request):
    script = request.query_params.get('script')
    keyword = request.query_params.get('keyword')
    print('script : ', script, 'keyword : ', keyword)
    keyword = unquote(keyword, encoding='utf-8', errors='replace')
    if script == 'copymanga':
        CopyMangaSpider().search(keyword)
    if script == 'bilinovel':
        BiliNovelSpider().search(keyword)
    return response.ok()
