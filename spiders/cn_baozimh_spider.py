import time

import requests
import bs4
import system.global_vars

from config.redis_config import RedisConfig
from constants import bucket, file_type, status
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


class CnBaoZiMhSpider:
    def __init__(self):
        self.domain = 'https://cn.baozimh.com'
        self.cover_domain = 'https://static-tw.baozimh.com/cover'
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
        index = 0
        try:
            man_hua_url = self.domain + '/api/bzmhq/amp_comic_list?type=all&region=cn&state=serial&filter=*&page=' + str(
                index) + '&limit=36&language=cn&__amp_source_origin=https%3A%2F%2Fcn.baozimh.com'
            while True:
                index += 1
                print(man_hua_url)
                man_hua_response = requests.get(man_hua_url, headers={
                    'Accept': 'application/json',
                    'Amp-Same-Origin': 'true',
                    'Referer': self.domain + '/classify',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                })
                man_hua_response_json = man_hua_response.json()
                print(man_hua_response_json)
                man_hua_items = man_hua_response_json['items']
                for man_hua_item in man_hua_items:
                    title = man_hua_item['name']
                    author = man_hua_item['author']
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    cover = self.cover_domain + '/' + man_hua_item['topic_img']
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
                    categories = man_hua_item['type_names']
                    category_str = ''
                    category_id_str = ''
                    if len(categories) != 0:
                        category_ids = []
                        index = 0
                        for category in categories:
                            category = category.replace('\'', '\\\'')
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                    region = man_hua_item['region_name']
                    self.region_db.save(region)
                    region_id = self.region_db.get_region_id(region)
                    detail_uri = man_hua_item['comic_id']
                    detail_url = self.domain + '/comic/' + detail_uri
                    print(detail_url)
                    man_hua_detail_response = requests.get(detail_url, headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Amp-Same-Origin': 'true',
                        'Referer': self.domain + '/classify',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    })
                    man_hua_detail_response_text = man_hua_detail_response.text
                    man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_response_text, 'html.parser')
                    description = man_hua_detail_soup.select('div.comics-detail p.comics-detail__desc')[0].text
                    self.comic_db.save(title, cover, description, 1, category_id_str, category_str, str(author_id),
                                       author, region_id, region)
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, str(author_id))
                    chapter_items = man_hua_detail_soup.select(
                        'div#chapter-items div.comics-chapters a.comics-chapters__item')
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    for chapter_item in chapter_items:
                        if system.global_vars.application.get_close_status() == status.YES:
                            print('ch bao zi mh is close.')
                            return
                        chapter_name = chapter_item.find_all('span')[0].text
                        print(chapter_name)
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        chapter_uri = chapter_item.get('href')
                        chapter_url = self.domain + chapter_uri
                        print(chapter_url)
                        man_hua_chapter_response = requests.get(chapter_url, headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'Amp-Same-Origin': 'true',
                            'Referer': self.domain + '/classify',
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                        })
                        man_hua_chapter_response_text = man_hua_chapter_response.text
                        man_hua_chapter_soup = bs4.BeautifulSoup(man_hua_chapter_response_text, 'html.parser')
                        img_items = man_hua_chapter_soup.select('ul.comic-contain img')
                        page_index = 0
                        for img_item in img_items:
                            path = img_item.get('src')
                            page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                          page_index)
                            if page_count == 0:
                                print(path)
                                file_name = self.file_item_handler.download(path, headers={
                                    'Referer': self.domain,
                                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                                  'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                })
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                         file_type.IMAGE_JPEG)
                                print(path)
                                self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                page_index)
                                self.comic_subscribe_db.upgrade(comic_id)
                                page_index += 1
                        chapter_index += 1
                        time.sleep(2)
                    chapter_items = man_hua_detail_soup.select(
                        'div#chapters_other_list div.comics-chapters a.comics-chapters__item')
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    for chapter_item in chapter_items:
                        if system.global_vars.application.get_close_status() == status.YES:
                            print('ch bao zi mh is close.')
                            return
                        chapter_name = chapter_item.find_all('span')[0].text
                        print(chapter_name)
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        chapter_uri = chapter_item.get('href')
                        chapter_url = self.domain + chapter_uri
                        print(chapter_url)
                        man_hua_chapter_response = requests.get(chapter_url, headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'Amp-Same-Origin': 'true',
                            'Referer': self.domain + '/classify',
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                        })
                        man_hua_chapter_response_text = man_hua_chapter_response.text
                        man_hua_chapter_soup = bs4.BeautifulSoup(man_hua_chapter_response_text, 'html.parser')
                        img_items = man_hua_chapter_soup.select('ul.comic-contain img')
                        page_index = 0
                        for img_item in img_items:
                            path = img_item.get('src')
                            page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                          page_index)
                            if page_count == 0:
                                print(path)
                                file_name = self.file_item_handler.download(path, headers={
                                    'Referer': self.domain,
                                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                                  'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                })
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                         file_type.IMAGE_JPEG)
                                print(path)
                                self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                page_index)
                                self.comic_subscribe_db.upgrade(comic_id)
                                page_index += 1
                        chapter_index += 1
                        time.sleep(2)
                man_hua_url = man_hua_response_json['next']
        except Exception as e:
            print(e)
