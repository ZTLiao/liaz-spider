import requests
import bs4
import zhconv
import system.global_vars
import uuid
import os

from PIL import Image

from config.redis_config import RedisConfig
from constants import bucket, file_type, status
from constants.redis_key import COMIC_DETAIL
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.region_db import RegionDb
from utils.redis_util import RedisUtil


class BaoZiMhSpider:
    def __init__(self):
        self.domain = 'https://baozimh.org'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.region_db = RegionDb()
        self.comic_db = ComicDb()
        self.comic_chapter_db = ComicChapterDb()
        self.comic_chapter_item_db = ComicChapterItemDb()
        self.asset_db = AssetDb()
        self.comic_subscribe_db = ComicSubscribeDb()
        self.file_item_handler = FileItemHandler()
        redis: RedisConfig = system.global_vars.systemConfig.get_redis()
        self.redis_util = RedisUtil(redis.host, redis.port, redis.db, redis.password)

    def parse(self):
        try:
            index = 0
            while True:
                index += 1
                man_hua_url = self.domain + '/dayup/page/' + str(index)
                print(man_hua_url)
                man_hua_response = requests.get(man_hua_url)
                man_hua_response_text = man_hua_response.text
                man_hua_soup = bs4.BeautifulSoup(man_hua_response_text, 'lxml')
                man_hua_items = man_hua_soup.select('div.grid-cols-3 .pb-2')
                if len(man_hua_items) == 0:
                    print('man hua is empty.')
                    break
                for man_hua_item in man_hua_items:
                    detail_uri = man_hua_item.find_all('a')[0].get('href')
                    detail_url = self.domain + detail_uri
                    print(detail_url)
                    man_hua_detail_response = requests.get(detail_url)
                    man_hua_detail_response.encoding = man_hua_detail_response.apparent_encoding
                    man_hua_detail_response_text = man_hua_detail_response.text
                    man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_response_text, 'lxml')
                    title_item = man_hua_detail_soup.select('div.gap-unit-xs h1')[0]
                    title = title_item.text.replace('連載中', '').strip()
                    img_item = man_hua_detail_soup.select('img.object-cover')[0]
                    cover = img_item.get('src')
                    print(cover)
                    comic_id = self.comic_db.get_comic_id(title)
                    if comic_id is None or comic_id == 0:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            file_name = convert_webp_to_jpg(file_name)
                            if file_name is not None:
                                cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    author_item = man_hua_detail_soup.find('span', string='作者：')
                    author_text = author_item.find_next('a').text.strip()
                    author_ids = []
                    author_str = ''
                    author_id_str = ''
                    if author_text is not None and len(author_text) != 0:
                        authors = author_text.strip().split(',')
                        author_index = 0
                        for author in authors:
                            author = author.replace('\'', '\\\'')
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if author_index != len(authors) - 1:
                                author_str += ','
                            author_index += 1
                        if len(author_ids) != 0:
                            author_id_str = ','.join(author_ids)
                    category_items = man_hua_detail_soup.select('div.text-sm .p-1')
                    category_ids = []
                    category_str = ''
                    category_index = 0
                    for category_item in category_items:
                        category = category_item.text.strip()
                        category = category.replace('\'', '\\\'').replace(',', '').strip()
                        self.category_db.save(category)
                        category_id = self.category_db.get_category_id(category)
                        category_ids.append(str(category_id))
                        category_str += category
                        if category_index != len(category_items) - 1:
                            category_str += ','
                        category_index += 1
                    category_items = man_hua_detail_soup.select('.py-1 span.rounded-lg')
                    if len(category_items) != 0:
                        category_str += ','
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
                    description_item = man_hua_detail_soup.select('p.my-unit-md')
                    description = description_item[0].text.strip()
                    self.comic_db.save(title, cover, description, 1, category_id_str, category_str,
                                       author_id_str,
                                       author_str, 0, '')
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    chapter_url = self.domain + '/chapterlist' + detail_uri.replace('/manga', '')
                    print(chapter_url)
                    chapter_response = requests.get(chapter_url)
                    chapter_response.encoding = chapter_response.apparent_encoding
                    chapter_response_text = chapter_response.text
                    chapter_soup = bs4.BeautifulSoup(chapter_response_text, 'lxml')
                    chapter_items = chapter_soup.select('div.chapteritem')
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    for chapter_item in chapter_items:
                        if system.global_vars.application.get_close_status() == status.YES:
                            print('bao zi man hua is close.')
                            return
                        chapter_index += 1
                        chapter_name = chapter_item.select('span.chaptertitle')[0].text.strip()
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        chapter_uri = chapter_item.select('a')[0].get('href')
                        chapter_url = self.domain + chapter_uri
                        chapter_response = requests.get(chapter_url)
                        chapter_response.encoding = chapter_response.apparent_encoding
                        chapter_response_text = chapter_response.text
                        chapter_soup = bs4.BeautifulSoup(chapter_response_text, 'lxml')
                        img_items = chapter_soup.select('div.h-full img[data-sizes="auto"]')
                        page_index = 0
                        for img_item in img_items:
                            path = img_item.get('src')
                            if str(path).endswith('.svg'):
                                path = img_item.get('data-src')
                            print(path)
                            if path is None:
                                continue
                            page_index += 1
                            page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                          page_index)
                            if page_count == 0:
                                file_name = self.file_item_handler.download(path)
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                         file_type.IMAGE_JPEG)
                                print(path)
                                self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                page_index)
                                self.comic_subscribe_db.upgrade(comic_id)
                    self.redis_util.delete(COMIC_DETAIL + str(comic_id))
        except Exception as e:
            print(e)


def traditional_to_simplified(text):
    # 调用convert函数将繁体字转换为简体字
    simplified_text = zhconv.convert(text, 'zh-hans')
    return simplified_text


def convert_webp_to_jpg(webp_file):
    jpg_file = str(uuid.uuid4())
    try:
        with Image.open(webp_file) as img:
            img.convert('RGB').save(jpg_file, 'JPEG')
        os.remove(webp_file)
        return jpg_file
    except Exception as e:
        print(e)
        return webp_file
