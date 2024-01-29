import requests

from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.region_db import RegionDb


class DongManZhiJiaSpider:
    def __init__(self):
        self.domain = 'https://v4api.idmzj.com'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.region_db = RegionDb()
        self.comic_db = ComicDb()
        self.comic_chapter_db = ComicChapterDb()
        self.comic_chapter_item_db = ComicChapterItemDb()
        self.asset_db = AssetDb()
        self.comic_subscribe_db = ComicSubscribeDb()
        self.file_item_handler = FileItemHandler()

    def comic_job(self):
        i = 0
        is_end = False
        while True:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            man_hua_url = self.domain + '/comic/update/list/100/' + str(i)
            print(man_hua_url)
            man_hua_response = requests.get(man_hua_url)
            man_hua_response_text = man_hua_response.text
            print(man_hua_response_text)
