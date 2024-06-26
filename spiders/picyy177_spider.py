import time
from datetime import datetime

import requests
import bs4

import system.global_vars
import undetected_chromedriver as uc

from config.redis_config import RedisConfig
from constants import status
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.comic_volume_db import ComicVolumeDb
from storage.region_db import RegionDb
from utils.redis_util import RedisUtil


class PicYY177Spider:
    def __init__(self):
        self.domain = 'https://www.177picyy.com'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.region_db = RegionDb()
        self.comic_db = ComicDb()
        self.comic_volume_db = ComicVolumeDb()
        self.comic_chapter_db = ComicChapterDb()
        self.comic_chapter_item_db = ComicChapterItemDb()
        self.asset_db = AssetDb()
        self.comic_subscribe_db = ComicSubscribeDb()
        self.file_item_handler = FileItemHandler()
        redis: RedisConfig = system.global_vars.systemConfig.get_redis()
        self.redis_util = RedisUtil(redis.host, redis.port, redis.db, redis.password)

    def parse(self):
        try:
            now = datetime.now().strftime("%m/%d")
            browser = None
            try:
                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-extensions')
                options.add_argument('--headless')
                options.add_argument('--remote-debugging-port=9222')
                browser = uc.Chrome(options=options, version_main=122)
                index = 0
                while True:
                    index += 1
                    man_hua_url = self.domain + '/html/category/tt/page/' + str(index) + '/'
                    browser.get(man_hua_url)
                    man_hua_content = browser.page_source
                    man_hua_soup = bs4.BeautifulSoup(man_hua_content, 'html.parser')
                    man_hua_items = man_hua_soup.select('div.picture-box h2.grid-title a')
                    date_items = man_hua_soup.select('div.picture-box span.grid-inf span.date')
                    if len(man_hua_items) == 0:
                        print('man hua is empty.')
                        break
                    for i in range(0, len(man_hua_items)):
                        try:
                            if len(date_items) >= i:
                                date_item = date_items[i]
                                date = date_item.text.strip()
                                if now != date:
                                    print('now : ', now, ', date : ', date)
                                    return
                            if system.global_vars.application.get_close_status() == status.YES:
                                print('177 picyy is close.')
                                return
                            man_hua_item = man_hua_items[i]
                            detail_url = man_hua_item.get('href')
                            browser.get(detail_url)
                            man_hua_detail_content = browser.page_source
                            man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_content, 'html.parser')
                            title_item = man_hua_detail_soup.select('main#main h1')[0]
                            title = title_item.text.replace('\'', '\\\'')
                            print(title)
                            description = title
                            author = '佚名'
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            category = '禁漫'
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            img_items = man_hua_detail_soup.select('div.entry-content div.single-content noscript img')
                            if len(img_items) == 0:
                                print('img is empty.')
                                continue
                            cover = img_items[0].get('src')
                            print(cover)
                            flag = 16
                            self.comic_db.save(title, cover, description, flag, str(category_id), category,
                                               str(author_id),
                                               author, 0, '')
                            comic_id = self.comic_db.get_comic_id(title)
                            asset_key = title + '|' + author
                            self.asset_db.save(asset_key, 1, title, cover, comic_id, str(category_id), str(author_id))
                            chapter_name = '全卷'
                            count = self.comic_chapter_db.count(comic_id, chapter_name)
                            if count == 0:
                                self.comic_chapter_db.save(comic_id, chapter_name, 1)
                                comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                              chapter_name)
                                self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            page_index = 0
                            for img_item in img_items:
                                page_index += 1
                                path = img_item.get('src')
                                print(path)
                                self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path, page_index)
                            page_items = man_hua_detail_soup.select('div.entry-content div.page-links a')
                            if len(page_items) > 1:
                                for i in range(1, len(page_items)):
                                    page_item = page_items[i]
                                    page_index += 1
                                    page_url = page_item.get('href')
                                    browser.get(page_url)
                                    man_hua_page_content = browser.page_source
                                    man_hua_page_soup = bs4.BeautifulSoup(man_hua_page_content, 'html.parser')
                                    path_items = man_hua_page_soup.select(
                                        'div.entry-content div.single-content noscript img')
                                    for path_item in path_items:
                                        page_index += 1
                                        path = path_item.get('src')
                                        print(path)
                                        self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path, page_index)
                                    time.sleep(3)
                            self.comic_subscribe_db.upgrade(comic_id)
                        except Exception as e:
                            print(e)
            except Exception as e:
                print(e)
            finally:
                if browser is not None:
                    browser.quit()
        except Exception as e:
            print(e)
