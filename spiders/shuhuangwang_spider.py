import time

import bs4
import requests
import system.global_vars

from config.redis_config import RedisConfig
from constants import file_type, bucket
from constants.redis_key import NOVEL_DETAIL
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb
from storage.novel_subscribe_db import NovelSubscribeDb
from utils.redis_util import RedisUtil


class ShuHuangWangSpider:
    def __init__(self, page_type=0):
        self.domain = 'https://www.fanghuoni.net'
        self.page_type = page_type
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.novel_db = NovelDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.asset_db = AssetDb()
        self.novel_subscribe_db = NovelSubscribeDb()
        self.file_item_handler = FileItemHandler()
        redis: RedisConfig = system.global_vars.systemConfig.get_redis()
        self.redis_util = RedisUtil(redis.host, redis.port, redis.db, redis.password)

    def parse(self):
        page_name = 'sort_0_0_0_OK'
        if self.page_type == '0':
            page_name = 'sort_0_0_0_OK'
        elif self.page_type == '1':
            page_name = 'sort_0_0_0_P'
        i = 0
        is_end = False
        while True:
            if is_end:
                print('xiao shuo is empty.')
                break
            i += 1
            try:
                serial_url = self.domain + '/' + page_name + '.html?page=' + str(i)
                print(serial_url)
                serial_response = requests.get(serial_url)
                serial_response_text = serial_response.text
                print(serial_response_text)
                serial_soup = bs4.BeautifulSoup(serial_response_text, 'lxml')
                for news_content_item in serial_soup.select('div#newscontent'):
                    a_items = news_content_item.select('.l li .s2 a')
                    li_items = news_content_item.select('.r .pagination li')
                    a_href = li_items[len(li_items) - 1].select('a')[0].get('href')
                    print(a_href)
                    if i == int(a_href.replace('?page=', '')):
                        is_end = True
                        break
                    for a_item in a_items:
                        detail_url = self.domain + a_item.get('href')
                        self.get_detail(detail_url)
                        detail_response = requests.get(detail_url)
                        detail_response_text = detail_response.text
                        detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
                        option_items = detail_soup.select('.listpage .middle option')
                        for j in range(1, len(option_items) - 1):
                            self.get_detail(self.domain + option_items[j].get('value'))
            except Exception as e:
                print(e)

    def get_detail(self, detail_url):
        index = 0
        while True:
            detail_url = detail_url + '?page=' + str(index)
            print(detail_url)
            try:
                detail_response = requests.get(detail_url)
                detail_response_text = detail_response.text
                detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
                detail_item = detail_soup.select('#maininfo')
                if len(detail_item) == 0:
                    print('detail_item : ', detail_item)
                    break
                for main_info_item in detail_item:
                    title = main_info_item.select('#info h1')[0].text.strip()
                    author = main_info_item.select('#info p')[0].text.replace('作    者：', '').strip()
                    category = main_info_item.select('#info p')[1].text.replace('类 别： ', '').strip()
                    description = main_info_item.select('#intro')[0].text.strip()
                    cover_img_item = detail_soup.select('#sidebar #fmimg img')[0]
                    cover = self.domain + cover_img_item.get('data-original')
                    novel_id = self.novel_db.get_novel_id(title)
                    if novel_id is None or novel_id == 0:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
                    chapter_item = detail_soup.select('div.box_con #list #bxxfn')
                    if len(chapter_item) > 1:
                        chapter_item = chapter_item[1]
                    a_items = chapter_item.select('dd a')
                    if len(a_items) == 0:
                        print('zhang jie is empty.')
                    else:
                        flag = 0
                        if self.page_type == '1':
                            flag = 1
                        self.novel_db.save(title, cover, description, flag, str(category_id), category, str(author_id),
                                           author, 0, '')
                        novel_id = self.novel_db.get_novel_id(title)
                        asset_key = title + '|' + author
                        self.asset_db.save(asset_key, 2, title, cover, novel_id, str(category_id), str(author_id))
                        chapter_index = self.novel_chapter_db.get_seq_no(novel_id)
                        last_item = a_items[len(a_items) - 1]
                        chapter_name = last_item.text
                        count = self.novel_chapter_db.count(novel_id, chapter_name)
                        if count != 0:
                            print('novel_id : ', novel_id, ', chapter_name : ', chapter_name, ' is exist.')
                            break
                        for a_chapter_item in a_items:
                            chapter_index += 1
                            chapter_name = a_chapter_item.text
                            count = self.novel_chapter_db.count(novel_id, chapter_name)
                            if count == 0:
                                self.novel_chapter_db.save(novel_id, chapter_name, chapter_index)
                                novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                                self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                            count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id, 1)
                            if count == 0:
                                page_url = self.domain + a_chapter_item.get('href')
                                print(page_url)
                                page_response = requests.get(page_url)
                                page_response_text = page_response.text
                                page_soup = bs4.BeautifulSoup(page_response_text, 'lxml')
                                content_item = page_soup.select('#content')
                                content = str(content_item[0]).replace('<div class="read_txt" id="content">',
                                                                       '').replace(
                                    '</div>', '').replace('<br/>', '\n')
                                print(content)
                                file_name = self.file_item_handler.write_content(content)
                                path = None
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.NOVEL, file_name, file_type.TEXT_PLAIN)
                                    time.sleep(1)
                                print(path)
                                if path is not None:
                                    self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, 1)
                                    self.novel_subscribe_db.upgrade(novel_id)
                    self.redis_util.delete(NOVEL_DETAIL + novel_id)
            except Exception as e:
                print(e)
            index += 1
