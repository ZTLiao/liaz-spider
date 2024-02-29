import time
from datetime import datetime

import requests
import bs4
import system.global_vars

from config.redis_config import RedisConfig
from constants import bucket, file_type
from constants.redis_key import NOVEL_DETAIL
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb
from storage.novel_subscribe_db import NovelSubscribeDb
from storage.novel_volume_db import NovelVolumeDb
from utils.redis_util import RedisUtil


class BiliNovelSpider:
    def __init__(self, page_type=1):
        self.domain = 'https://www.bilinovel.com'
        self.page_type = page_type
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.novel_db = NovelDb()
        self.novel_volume_db = NovelVolumeDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.asset_db = AssetDb()
        self.novel_subscribe_db = NovelSubscribeDb()
        self.file_item_handler = FileItemHandler()
        redis: RedisConfig = system.global_vars.systemConfig.get_redis()
        self.redis_util = RedisUtil(redis.host, redis.port, redis.db, redis.password)

    def parse(self):
        page_type = '5' if int(self.page_type) == 0 else '0'
        try:
            index = 0
            while True:
                index += 1
                xiao_shuo_url = self.domain + '/wenku/lastupdate_0_0_0_0_0_0_' + page_type + '_' + str(
                    index) + '_0.html'
                print(xiao_shuo_url)
                xiao_shuo_response = requests.get(xiao_shuo_url)
                xiao_shuo_response_text = xiao_shuo_response.text
                xiao_shuo_soup = bs4.BeautifulSoup(xiao_shuo_response_text, 'html.parser')
                xiao_shuo_items = xiao_shuo_soup.select('li.book-li a')
                for xiao_shuo_item in xiao_shuo_items:
                    detail_uri: str = xiao_shuo_item.get('href')
                    if not detail_uri.startswith('/novel'):
                        print(detail_uri)
                        continue
                    detail_url = self.domain + detail_uri
                    xiao_shuo_detail_response = requests.get(detail_url)
                    xiao_shuo_detail_response_text = xiao_shuo_detail_response.text
                    xiao_shuo_detail_soup = bs4.BeautifulSoup(xiao_shuo_detail_response_text, 'html.parser')
                    xiao_shuo_detail_item = xiao_shuo_detail_soup.select('div.book-detail-info .book-layout')[0]
                    title = xiao_shuo_detail_item.find('h1').text.replace('\'', '\\\'')
                    cover = xiao_shuo_detail_item.find('img').get('src')
                    print(cover)
                    novel_id = self.novel_db.get_novel_id(title)
                    if novel_id is None or novel_id == 0:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    author = xiao_shuo_detail_item.select('span.authorname a')[0].text
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    category_items = xiao_shuo_detail_item.select('span.tag-small-group em.tag-small a')
                    category_ids = []
                    category_str = ''
                    category_index = 0
                    for category_item in category_items:
                        category = category_item.text.strip()
                        category = category.replace('\'', '\\\'').replace(',', '').replace('#', '').replace('\n',
                                                                                                            '').strip()
                        self.category_db.save(category)
                        category_id = self.category_db.get_category_id(category)
                        category_ids.append(str(category_id))
                        category_str += category
                        if category_index != len(category_items) - 1:
                            category_str += ','
                        category_index += 1
                    category_id_str = ','.join(category_ids)
                    description = xiao_shuo_detail_soup.select('section.book-summary content')[0].text
                    print('title : ', title, ', description : ', description)
                    self.novel_db.save(title, cover, description, 1, category_id_str, category_str, str(author_id),
                                       author, 0, '')
                    novel_id = self.novel_db.get_novel_id(title)
                    asset_key = title + '|' + author
                    self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, str(author_id))
                    volume_uri = xiao_shuo_detail_soup.select('div.module-merge .book-status')[0].get('href')
                    volume_url = self.domain + volume_uri
                    print(volume_url)
                    xiao_shuo_volume_response = requests.get(volume_url)
                    xiao_shuo_volume_response_text = xiao_shuo_volume_response.text
                    xiao_shuo_volume_soup = bs4.BeautifulSoup(xiao_shuo_volume_response_text, 'html.parser')
                    volume_items = xiao_shuo_volume_soup.select('div.catalog-volume')
                    volume_index = 0
                    for volume_item in volume_items:
                        volume_index += 1
                        volume_name = volume_item.find('h3').text.replace('\'', '\\\'')
                        self.novel_volume_db.save(novel_id, volume_name, volume_index)
                        novel_volume_id = self.novel_volume_db.get_novel_volume_id(novel_id, volume_name)
                        chapter_items = volume_item.select('.chapter-li-a')
                        chapter_index = self.novel_chapter_db.get_seq_no_by_novel_volume_id(novel_id, novel_volume_id)
                        for chapter_item in chapter_items:
                            chapter_index += 1
                            chapter_name = chapter_item.text.replace('\'', '\\\'')
                            count = self.novel_chapter_db.count_by_novel_volume_id(novel_id, novel_volume_id,
                                                                                   chapter_name)
                            self.novel_chapter_db.save_by_novel_volume_id(novel_id, novel_volume_id, chapter_name,
                                                                          chapter_index)

                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            if count == 0 and novel_chapter_id is not None:
                                self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                                self.novel_db.upgrade(novel_id)
                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            chapter_uri: str = chapter_item.get('href')
                            if not chapter_uri.endswith('.html'):
                                print('volume name : ', volume_name, ', chapter uri : ', chapter_uri)
                                continue
                            chapter_url = self.domain + chapter_uri
                            print(chapter_url)
                            xiao_shuo_chapter_response = requests.get(chapter_url, headers={
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                                'Accept-Language': 'zh-CN,zh;q=0.9',
                            })
                            xiao_shuo_chapter_response_text = xiao_shuo_chapter_response.text
                            time.sleep(2)
                            xiao_shuo_chapter_soup = bs4.BeautifulSoup(xiao_shuo_chapter_response_text, 'html.parser')
                            img_tags = xiao_shuo_chapter_soup.find_all('img')
                            page_index = 0
                            if len(img_tags) != 0:
                                for img in img_tags:
                                    path = img.get('data-src')
                                    print(path)
                                    page_index += 1
                                    novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                        novel_id, novel_volume_id, chapter_name)
                                    page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        file_name = self.file_item_handler.download(path, headers={
                                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                                            'Referer': self.domain,
                                        })
                                        if file_name is not None:
                                            path = self.file_item_handler.upload(bucket.INSET, file_name,
                                                                                 file_type.IMAGE_JPEG)
                                        print(path)
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path,
                                                                        page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                            content_items = xiao_shuo_chapter_soup.select('div#acontentz')
                            if len(content_items) > 0:
                                content_items = content_items[0]
                            print(content_items)
                            content = ''
                            for content_item in content_items.select('p, br'):
                                tag: str = content_item.prettify()
                                text = content_item.text
                                if len(text) != 0:
                                    if 'br' in tag:
                                        content += '\n'
                                    else:
                                        content += content_item.text + '\n'
                            content = replace_secret_text(content)
                            if len(content) == 0:
                                continue
                            page_index += 1
                            page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                          page_index)
                            if page_count == 0:
                                file_name = self.file_item_handler.write_content(content)
                                path = None
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.NOVEL, file_name,
                                                                         file_type.TEXT_PLAIN)
                                print(path)
                                if path is not None:
                                    self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, page_index)
                                    self.novel_subscribe_db.upgrade(novel_id)
                    self.redis_util.delete(NOVEL_DETAIL + str(novel_id))
        except Exception as e:
            print(e)

    def job(self):
        try:
            now = datetime.now().strftime("%Y-%m-%d")
            index = 0
            while True:
                index += 1
                xiao_shuo_url = self.domain + '/wenku/lastupdate_0_0_0_0_0_0_0_' + str(index) + '_0.html'
                print(xiao_shuo_url)
                xiao_shuo_response = requests.get(xiao_shuo_url)
                xiao_shuo_response_text = xiao_shuo_response.text
                xiao_shuo_soup = bs4.BeautifulSoup(xiao_shuo_response_text, 'html.parser')
                xiao_shuo_items = xiao_shuo_soup.select('li.book-li a')
                for xiao_shuo_item in xiao_shuo_items:
                    detail_uri: str = xiao_shuo_item.get('href')
                    if not detail_uri.startswith('/novel'):
                        print(detail_uri)
                        continue
                    detail_url = self.domain + detail_uri
                    xiao_shuo_detail_response = requests.get(detail_url)
                    xiao_shuo_detail_response_text = xiao_shuo_detail_response.text
                    xiao_shuo_detail_soup = bs4.BeautifulSoup(xiao_shuo_detail_response_text, 'html.parser')
                    date = xiao_shuo_detail_soup.select('div.book-meta-l')[0].text.replace('最后更新·', '')
                    print(date)
                    if now != date:
                        print('novel date : ', date)
                        return
                    xiao_shuo_detail_item = xiao_shuo_detail_soup.select('div.book-detail-info .book-layout')[0]
                    title = xiao_shuo_detail_item.find('h1').text.replace('\'', '\\\'')
                    cover = xiao_shuo_detail_item.find('img').get('src')
                    print(cover)
                    novel_id = self.novel_db.get_novel_id(title)
                    if novel_id is None or novel_id == 0:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    author = xiao_shuo_detail_item.select('span.authorname a')[0].text
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    category_items = xiao_shuo_detail_item.select('span.tag-small-group em.tag-small a')
                    category_ids = []
                    category_str = ''
                    category_index = 0
                    for category_item in category_items:
                        category = category_item.text.strip()
                        category = category.replace('\'', '\\\'').replace(',', '').replace('#', '').replace('\n',
                                                                                                            '').strip()
                        self.category_db.save(category)
                        category_id = self.category_db.get_category_id(category)
                        category_ids.append(str(category_id))
                        category_str += category
                        if category_index != len(category_items) - 1:
                            category_str += ','
                        category_index += 1
                    category_id_str = ','.join(category_ids)
                    description = xiao_shuo_detail_soup.select('section.book-summary content')[0].text
                    print('title : ', title, ', description : ', description)
                    self.novel_db.save(title, cover, description, 1, category_id_str, category_str, str(author_id),
                                       author, 0, '')
                    novel_id = self.novel_db.get_novel_id(title)
                    asset_key = title + '|' + author
                    self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, str(author_id))
                    volume_uri = xiao_shuo_detail_soup.select('div.module-merge .book-status')[0].get('href')
                    volume_url = self.domain + volume_uri
                    print(volume_url)
                    xiao_shuo_volume_response = requests.get(volume_url)
                    xiao_shuo_volume_response_text = xiao_shuo_volume_response.text
                    xiao_shuo_volume_soup = bs4.BeautifulSoup(xiao_shuo_volume_response_text, 'html.parser')
                    volume_items = xiao_shuo_volume_soup.select('div.catalog-volume')
                    volume_index = 0
                    for volume_item in volume_items:
                        volume_index += 1
                        volume_name = volume_item.find('h3').text.replace('\'', '\\\'')
                        self.novel_volume_db.save(novel_id, volume_name, volume_index)
                        novel_volume_id = self.novel_volume_db.get_novel_volume_id(novel_id, volume_name)
                        chapter_items = volume_item.select('.chapter-li-a')
                        chapter_index = self.novel_chapter_db.get_seq_no_by_novel_volume_id(novel_id, novel_volume_id)
                        for chapter_item in chapter_items:
                            chapter_index += 1
                            chapter_name = chapter_item.text.replace('\'', '\\\'')
                            count = self.novel_chapter_db.count_by_novel_volume_id(novel_id, novel_volume_id,
                                                                                   chapter_name)
                            self.novel_chapter_db.save_by_novel_volume_id(novel_id, novel_volume_id, chapter_name,
                                                                          chapter_index)

                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            if count == 0 and novel_chapter_id is not None:
                                self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                                self.novel_db.upgrade(novel_id)
                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            chapter_uri: str = chapter_item.get('href')
                            if not chapter_uri.endswith('.html'):
                                print('volume name : ', volume_name, ', chapter uri : ', chapter_uri)
                                continue
                            chapter_url = self.domain + chapter_uri
                            print(chapter_url)
                            xiao_shuo_chapter_response = requests.get(chapter_url, headers={
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                                'Accept-Language': 'zh-CN,zh;q=0.9',
                            })
                            xiao_shuo_chapter_response_text = xiao_shuo_chapter_response.text
                            xiao_shuo_chapter_soup = bs4.BeautifulSoup(xiao_shuo_chapter_response_text, 'html.parser')
                            img_tags = xiao_shuo_chapter_soup.find_all('img')
                            page_index = 0
                            if len(img_tags) != 0:
                                for img in img_tags:
                                    path = img.get('data-src')
                                    print(path)
                                    page_index += 1
                                    novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                        novel_id, novel_volume_id, chapter_name)
                                    page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        file_name = self.file_item_handler.download(path, headers={
                                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                                            'Referer': self.domain,
                                        })
                                        if file_name is not None:
                                            path = self.file_item_handler.upload(bucket.INSET, file_name,
                                                                                 file_type.IMAGE_JPEG)
                                        print(path)
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path,
                                                                        page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                            content_items = xiao_shuo_chapter_soup.select('div#acontentz')
                            if len(content_items) > 0:
                                content_items = content_items[0]
                            content = ''
                            for content_item in content_items.select('p, br'):
                                tag: str = content_item.prettify()
                                text = content_item.text
                                if len(text) != 0:
                                    if 'br' in tag:
                                        content += '\n'
                                    else:
                                        content += content_item.text + '\n'
                            content = replace_secret_text(content)
                            if len(content) == 0:
                                continue
                            page_index += 1
                            page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                          page_index)
                            if page_count == 0:
                                file_name = self.file_item_handler.write_content(content)
                                path = None
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.NOVEL, file_name,
                                                                         file_type.TEXT_PLAIN)
                                print(path)
                                if path is not None:
                                    self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, page_index)
                                    self.novel_subscribe_db.upgrade(novel_id)
                    self.redis_util.delete(NOVEL_DETAIL + str(novel_id))
        except Exception as e:
            print(e)


def replace_secret_text(content):
    if len(content) == 0:
        return ''
    result = ''
    for i in range(len(content)):
        before_char = content[i]
        replacement = before_char
        for key in SECRET_MAP:
            if before_char == key:
                replacement = SECRET_MAP[key]
                break
        result += replacement
    return result


SECRET_MAP = {
    "\u201c": "\u300c",
    "\u201d": "\u300d",
    "\u2018": "\u300e",
    "\u2019": "\u300f",
    "\ue82c": "\u7684",
    "\ue836": "\u4e00",
    "\ue852": "\u662f",
    "\ue850": "\u4e86",
    "\ue832": "\u6211",
    "\ue812": "\u4e0d",
    "\ue833": "\u4eba",
    "\ue849": "\u5728",
    "\ue821": "\u4ed6",
    "\ue810": "\u6709",
    "\ue84c": "\u8fd9",
    "\ue815": "\u4e2a",
    "\ue842": "\u4e0a",
    "\ue82e": "\u4eec",
    "\ue817": "\u6765",
    "\ue835": "\u5230",
    "\ue837": "\u65f6",
    "\ue82d": "\u5927",
    "\ue859": "\u5730",
    "\ue85c": "\u4e3a",
    "\ue82f": "\u5b50",
    "\ue84d": "\u4e2d",
    "\ue854": "\u4f60",
    "\ue81e": "\u8bf4",
    "\ue853": "\u751f",
    "\ue80f": "\u56fd",
    "\ue80e": "\u5e74",
    "\ue813": "\u7740",
    "\ue802": "\u5c31",
    "\ue81a": "\u90a3",
    "\ue83b": "\u548c",
    "\ue851": "\u8981",
    "\ue82a": "\u5979",
    "\ue838": "\u51fa",
    "\ue808": "\u4e5f",
    "\ue83a": "\u5f97",
    "\ue814": "\u91cc",
    "\ue857": "\u540e",
    "\ue855": "\u81ea",
    "\ue800": "\u4ee5",
    "\ue81b": "\u4f1a",
    "\ue85f": "\u5bb6",
    "\ue816": "\u53ef",
    "\ue83e": "\u4e0b",
    "\ue84f": "\u800c",
    "\ue80b": "\u8fc7",
    "\ue828": "\u5929",
    "\ue843": "\u53bb",
    "\ue806": "\u80fd",
    "\ue81f": "\u5bf9",
    "\ue834": "\u5c0f",
    "\ue81c": "\u591a",
    "\ue848": "\u7136",
    "\ue830": "\u4e8e",
    "\ue84b": "\u5fc3",
    "\ue84a": "\u5b66",
    "\ue85d": "\u4e48",
    "\ue861": "\u4e4b",
    "\ue809": "\u90fd",
    "\ue80c": "\u597d",
    "\ue84e": "\u770b",
    "\ue858": "\u8d77",
    "\ue840": "\u53d1",
    "\ue85b": "\u5f53",
    "\ue863": "\u6ca1",
    "\ue839": "\u6210",
    "\ue827": "\u53ea",
    "\ue841": "\u5982",
    "\ue805": "\u4e8b",
    "\ue845": "\u628a",
    "\ue820": "\u8fd8",
    "\ue83c": "\u7528",
    "\ue847": "\u7b2c",
    "\ue819": "\u6837",
    "\ue82b": "\u9053",
    "\ue80a": "\u60f3",
    "\ue822": "\u4f5c",
    "\ue85e": "\u79cd",
    "\ue801": "\u5f00",
    "\ue856": "\u7f8e",
    "\ue811": "\u4e73",
    "\ue860": "\u9634",
    "\ue80d": "\u6db2",
    "\ue83f": "\u830e",
    "\ue803": "\u6b32",
    "\ue804": "\u547b",
    "\ue825": "\u8089",
    "\ue846": "\u4ea4",
    "\ue85a": "\u6027",
    "\ue831": "\u80f8",
    "\ue81d": "\u79c1",
    "\ue826": "\u7a74",
    "\ue818": "\u6deb",
    "\ue823": "\u81c0",
    "\ue829": "\u8214",
    "\ue807": "\u5c04",
    "\ue862": "\u8131",
    "\ue83d": "\u88f8",
    "\ue824": "\u9a9a",
    "\ue844": "\u5507"
}
