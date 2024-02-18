import requests
import bs4

from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb
from storage.novel_subscribe_db import NovelSubscribeDb


class BiliNovelSpider:
    def __init__(self):
        self.domain = 'https://www.bilinovel.com'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.novel_db = NovelDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.asset_db = AssetDb()
        self.novel_subscribe_db = NovelSubscribeDb()
        self.file_item_handler = FileItemHandler()

    def parse(self):
        try:
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
                    print(xiao_shuo_detail_response_text)
                    xiao_shuo_detail_soup = bs4.BeautifulSoup(xiao_shuo_detail_response_text, 'html.parser')
        except Exception as e:
            print(e)
