import requests

from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb
from storage.novel_subscribe_db import NovelSubscribeDb


class QiMaoSpider:
    def __init__(self):
        self.domain = 'https://www.qimao.com'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.novel_db = NovelDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.asset_db = AssetDb()
        self.novel_subscribe_db = NovelSubscribeDb()
        self.file_item_handler = FileItemHandler()

    def parse(self):
        index = 0
        while True:
            index += 1
            xiao_shuo_url = self.domain + '/shuku/a-a-a-a-a-a-a-update_time-' + str(index) + '/'
            print(xiao_shuo_url)
            xiao_shuo_response = requests.get(xiao_shuo_url)
            xiao_shuo_response_text = xiao_shuo_response.text
            print(xiao_shuo_response_text)
