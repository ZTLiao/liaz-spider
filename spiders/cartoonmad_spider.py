import requests
import bs4
import zhconv
import system.global_vars

import system
from config.redis_config import RedisConfig
from constants import bucket, file_type
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


class CartoonMadSpider:
    def __init__(self):
        self.domain = 'https://www.cartoonmad.com'
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
                man_hua_url = self.domain + '/comic99.0' + str(index) + '.html'
                man_hua_response = requests.get(man_hua_url)
                man_hua_response.encoding = man_hua_response.apparent_encoding
                man_hua_response_text = man_hua_response.text
                man_hua_soup = bs4.BeautifulSoup(man_hua_response_text, 'lxml')
                man_hua_items = man_hua_soup.select('tr td a.a1')
                if len(man_hua_items) == 0:
                    print('man hua is empty.')
                    break
                for man_hua_item in man_hua_items:
                    detail_uri = man_hua_item.get('href')
                    title = traditional_to_simplified(man_hua_item.text)
                    print('detail_uri : ', detail_uri, ', title : ', title)
                    detail_url = self.domain + '/m/' + detail_uri
                    print(detail_url)
                    man_hua_detail_response = requests.get(detail_url)
                    man_hua_detail_response.encoding = man_hua_detail_response.apparent_encoding
                    man_hua_detail_response_text = man_hua_detail_response.text
                    man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_response_text, 'lxml')
                    img_item = man_hua_detail_soup.select('table td[rowspan="8"] img')
                    img_uri = img_item[0].get('src')
                    cover = self.domain + img_uri
                    print(cover)
                    comic_id = self.comic_db.get_comic_id(title)
                    if comic_id is None or comic_id == 0:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    detail_item = man_hua_detail_soup.select('table td[height="24"]')
                    category_item = detail_item[0].select('td[width="50%"] a')
                    category = traditional_to_simplified(category_item[0].text)
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
                    author_item = detail_item[1]
                    authors = author_item.text.replace('作者：', '').strip().split(',')
                    author_ids = []
                    author_str = ''
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
                    author_id_str = ','.join(author_ids)
                    description_item = man_hua_detail_soup.select('table[cellspacing="8"] td[style="font-size:11pt;"]')
                    description = description_item[0].text.strip()
                    self.comic_db.save(title, cover, description, 1, str(category_id), category,
                                       author_id_str,
                                       author_str, 0, '')
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, str(category_id), author_id_str)
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    chapter_items = man_hua_detail_soup.select('table tr[align="center"] td a')
                    for chapter_item in chapter_items:
                        chapter_index += 1
                        chapter_name = traditional_to_simplified(chapter_item.text.strip())
                        if len(chapter_name) == 0:
                            print('chapter_name is empty.')
                            break
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count != 0:
                            print('comic_id : ', comic_id, ', chapter_name : ', chapter_name, ' is exist.')
                            break
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        chapter_uri = chapter_item.get('href')
                        if chapter_uri.startswith('http'):
                            print('chapter_uri : ', chapter_uri)
                            break
                        chapter_url = self.domain + chapter_uri
                        print(chapter_url)
                        chapter_response = requests.get(chapter_url)
                        chapter_response_text = chapter_response.text
                        page_index = 1
                        chapter_soup = bs4.BeautifulSoup(chapter_response_text, 'lxml')
                        path = 'https:' + chapter_soup.select('table td[align="center"] a img')[0].get('src')
                        page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                      page_index)
                        print(path)
                        if page_count == 0:
                            file_name = self.file_item_handler.download(path)
                            if file_name is not None:
                                path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                     file_type.IMAGE_JPEG)
                            print(path)
                            self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                            page_index)
                            self.comic_subscribe_db.upgrade(comic_id)
                        a_items = chapter_soup.select('table td[height="36"] a')
                        a_uri = str(a_items[len(a_items) - 1].get('href'))
                        while True:
                            if (not a_uri.startswith('http')) and a_uri.endswith('.html'):
                                img_url = self.domain + '/m/comic/' + a_uri
                                print(img_url)
                                img_response = requests.get(img_url)
                                img_response_text = img_response.text
                                page_index += 1
                                img_soup = bs4.BeautifulSoup(img_response_text, 'lxml')
                                path = 'https:' + img_soup.select('table td[align="center"] a img')[0].get('src')
                                page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                              page_index)
                                print(path)
                                if page_count == 0:
                                    file_name = self.file_item_handler.download(path)
                                    if file_name is not None:
                                        path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                             file_type.IMAGE_JPEG)
                                    print(path)
                                    self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                    page_index)
                                    self.comic_subscribe_db.upgrade(comic_id)
                                a_items = img_soup.select('table td[height="36"] a')
                                a_uri = str(a_items[len(a_items) - 1].get('href'))
                            else:
                                break
                    self.redis_util.delete(COMIC_DETAIL + comic_id)
        except Exception as e:
            print(e)


def traditional_to_simplified(text):
    # 调用convert函数将繁体字转换为简体字
    simplified_text = zhconv.convert(text, 'zh-hans')
    return simplified_text
