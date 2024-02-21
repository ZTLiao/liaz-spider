import time
import system.global_vars
import undetected_chromedriver as uc

from config.redis_config import RedisConfig
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
        self.domain = 'https://www.manhuadb.net'
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
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--remote-debugging-port=9222')
        browser = uc.Chrome(options=options)
        while True:
            index += 1
            man_hua_url = self.domain + '/manhua/list-page-' + str(index) + '.html'
            print(man_hua_url)
            browser.get(man_hua_url)
            man_hua_content = browser.page_source
            print(man_hua_content)
            time.sleep(1000)
