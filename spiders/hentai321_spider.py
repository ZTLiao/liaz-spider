import time

import requests
import bs4
import system.global_vars

from config.redis_config import RedisConfig
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


class HenTai321Spider:
    def __init__(self, page_type=1):
        self.domain = 'https://hentai321.top'
        self.page_type = page_type
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
            index = 0
            while True:
                index += 1
                man_hua_url = self.domain + '?language/chinese/' + str(index)
                print(man_hua_url)
                man_hua_response = requests.get(man_hua_url)
                man_hua_response_text = man_hua_response.text
                man_hua_soup = bs4.BeautifulSoup(man_hua_response_text, 'html.parser')
                man_hua_items = man_hua_soup.select('div.doujin a')
                if len(man_hua_items) == 0:
                    print('man hua is empty.')
                    break
                for man_hua_item in man_hua_items:
                    detail_uri = man_hua_item.get('href')
                    detail_url = self.domain + detail_uri
                    print(detail_url)
                    man_hua_detail_response = requests.get(detail_url)
                    man_hua_detail_response_text = man_hua_detail_response.text
                    man_hua_detail_soup = bs4.BeautifulSoup(man_hua_detail_response_text, 'html.parser')
                    cover_item = man_hua_detail_soup.select('div#main-cover img')[0]
                    cover = cover_item.get('src')
                    print(cover)
                    title_item = man_hua_detail_soup.select('div#main-info h1')[0]
                    title = title_item.text.replace('\'', '\\\'')
                    print(title)
                    description = title
                    author = '佚名'
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    category = '禁漫'
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
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
                    img_items = man_hua_detail_soup.select('div.single-thumb noscript img')
                    page_index = 0
                    for img_item in img_items:
                        page_index += 1
                        path = img_item.get('src')
                        print(path)
                        self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path, page_index)
                        self.comic_subscribe_db.upgrade(comic_id)
                    time.sleep(3)
        except Exception as e:
            print(e)
