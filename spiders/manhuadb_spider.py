import base64
import json
import time

import system.global_vars
import bs4
import undetected_chromedriver as uc

from config.redis_config import RedisConfig
from constants import status
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


class ManHuaDbSpider:
    def __init__(self):
        self.domain = 'https://www.manhuadb.com'
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
            browser = None
            try:
                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-extensions')
                options.add_argument('--headless')
                options.add_argument('--remote-debugging-port=9222')
                browser = uc.Chrome(options=options)
                while index <= 500:
                    index += 1
                    man_hua_url = self.domain + '/manhua/list-page-' + str(index) + '.html'
                    print(man_hua_url)
                    browser.get(man_hua_url)
                    man_hua_content = browser.page_source
                    print(man_hua_content)
                    man_hua_soup = bs4.BeautifulSoup(man_hua_content, 'html.parser')
                    man_hua_items = man_hua_soup.select('div.comic-book-unit')
                    for man_hua_item in man_hua_items:
                        a_item = man_hua_item.select('h2.h3 a')[0]
                        title = a_item.text
                        cover = man_hua_item.find('img').get('data-original')
                        print(cover)
                        detail_uri = a_item.get('href')
                        detail_url = self.domain + detail_uri
                        print(detail_url)
                        time.sleep(2)
                        browser.get(detail_url)
                        man_hua_detail_content = browser.page_source
                        man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_content, 'html.parser')
                        author_items = man_hua_detail_soup.select('div.comic-info .creators a')
                        author_ids = []
                        author_str = ''
                        author_index = 0
                        for author_item in author_items:
                            author = author_item.text
                            author = author.replace('\'', '\\\'')
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if author_index != len(author_items) - 1:
                                author_str += ','
                            author_index += 1
                        author_id_str = ','.join(author_ids)
                        category_items = man_hua_detail_soup.select('div.comic-info .tags a')
                        category_str = ''
                        category_id_str = ''
                        if len(category_items) != 0:
                            category_ids = []
                            index = 0
                            for category_item in category_items:
                                category = category_item.text
                                category = category.replace('\'', '\\\'')
                                self.category_db.save(category)
                                category_id = self.category_db.get_category_id(category)
                                category_ids.append(str(category_id))
                                category_str += category
                                if index != len(category_items) - 1:
                                    category_str += ','
                                index += 1
                            category_id_str = ','.join(category_ids)
                        description_item = man_hua_detail_soup.select('div.comic-info .comic_story')[0]
                        description = description_item.text
                        print(description)
                        flag = 1
                        if '已完结' in category_str:
                            flag = 0
                        self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                           author_id_str,
                                           author_str, 0, '')
                        comic_id = self.comic_db.get_comic_id(title)
                        asset_key = title + '|' + author_str
                        self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                        chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                        chapter_items = man_hua_detail_soup.select('div#comic-book-list .sort_div a')
                        print(chapter_items)
                        for chapter_item in chapter_items:
                            if system.global_vars.application.get_close_status() == status.YES:
                                print('man hua db is close.')
                                return
                            chapter_index += 1
                            chapter_name = chapter_item.text
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
                            browser.get(chapter_url)
                            man_hua_chapter_content = browser.page_source
                            man_hua_chapter_soup = bs4.BeautifulSoup(man_hua_chapter_content, 'html.parser')
                            img_data_item = man_hua_chapter_soup.select('div.vg-r-data')[0]
                            img_domain = img_data_item.get('data-host')
                            img_prefix = img_data_item.get('data-img_pre')
                            print('img_domain : ', img_domain, ', img_prefix : ', img_prefix)
                            script_items = man_hua_chapter_soup.select('script')
                            for script_item in script_items:
                                script_content = script_item.text
                                if len(script_content) == 0 or 'img_data' not in script_content:
                                    continue
                                encrypt_data = script_content.replace('var img_data =', '').replace('\'', '').replace(
                                    ';',
                                    '')
                                img_data = json.loads(base64.b64decode(encrypt_data))
                                print(img_data)
                                for img_item in img_data:
                                    page_index = img_item['p']
                                    path = img_domain + img_prefix + img_item['img']
                                    page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        print(path)
                                        self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                        page_index)
                                        self.comic_subscribe_db.upgrade(comic_id)
                        self.redis_util.delete(COMIC_DETAIL + str(comic_id))
                        time.sleep(2)
            except Exception as e:
                print(e)
            finally:
                if browser is not None:
                    browser.quit()
        except Exception as e:
            print(e)
