import bs4
import requests

from handler.resource_handler import ResourceHandler, download, write_note
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb


class ShuHuangWangSpider:
    def __init__(self, resource_url, username, password, page_type):
        self.domain = 'https://www.fanghuoni.net'
        self.resource_url = resource_url
        self.username = username
        self.password = password
        self.page_type = page_type
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.novel_db = NovelDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.resource_handler = ResourceHandler(self.resource_url, self.username, self.password)

    def parse(self):
        page_name = 'sort_0_0_0_OK'
        if self.page_type == '0':
            page_name = 'sort_0_0_0_OK'
        elif self.page_type == '1':
            page_name = 'sort_0_0_0_P'
        i = 0
        is_end = False
        while i == 0:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            try:
                serial_url = self.domain + '/' + page_name + '.html?page=' + str(i)
                print(serial_url)
                serial_response = requests.get(serial_url)
                serial_response_text = serial_response.text
                serial_soup = bs4.BeautifulSoup(serial_response_text, 'lxml')
                for news_content_item in serial_soup.select('div#newscontent'):
                    a_items = news_content_item.select('.l li .s2 a')
                    li_items = news_content_item.select('.r .pagination li')
                    a_href = li_items[len(li_items) - 1].select('a')[0].get('href')
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
                        for i in range(1, len(option_items) - 1):
                            self.get_detail(self.domain + option_items[i].get('value'))
            except Exception as e:
                print(e)

    def get_detail(self, detail_url):
        print(detail_url)
        try:
            detail_response = requests.get(detail_url)
            detail_response_text = detail_response.text
            detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
            for main_info_item in detail_soup.select('#maininfo'):
                title = main_info_item.select('#info h1')[0].text.strip()
                author = main_info_item.select('#info p')[0].text.replace('作    者：', '').strip()
                category = main_info_item.select('#info p')[1].text.replace('类 别： ', '').strip()
                description = main_info_item.select('#intro')[0].text.strip()
                cover_img_item = detail_soup.select('#sidebar #fmimg img')[0]
                cover = self.domain + cover_img_item.get('data-original')
                novel_id = self.novel_db.get_novel_id(title)
                if novel_id is None:
                    file_name = download(cover)
                    if file_name is not None:
                        cover = self.resource_handler.upload('cover', file_name)
                    print(cover)
                    if cover is None:
                        cover = ''
                self.author_db.save(author)
                author_id = self.author_db.get_author_id(author)
                self.category_db.save(category)
                category_id = self.category_db.get_category_id(category)
                a_items = detail_soup.select('div.box_con #list dd a')
                if len(a_items) == 0:
                    print('zhang jie is empty.')
                else:
                    flag = 0
                    if self.page_type == '1':
                        flag = 1
                    self.novel_db.save(title, cover, description, flag, str(category_id), category, str(author_id),
                                       author, 0, '')
                    novel_id = self.novel_db.get_novel_id(title)
                    chapter_index = self.novel_chapter_db.get_seq_no(novel_id)
                    for a_chapter_item in a_items:
                        chapter_index += 1
                        chapter_name = a_chapter_item.text
                        count = self.novel_chapter_db.count(novel_id, chapter_name)
                        if count == 0:
                            self.novel_chapter_db.save(novel_id, chapter_name, chapter_index)
                        novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                        count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id, 1)
                        if count == 0:
                            page_url = self.domain + a_chapter_item.get('href')
                            print(page_url)
                            page_response = requests.get(page_url)
                            page_response_text = page_response.text
                            page_soup = bs4.BeautifulSoup(page_response_text, 'lxml')
                            content_item = page_soup.select('#content')
                            content = content_item[0].text
                            file_name = write_note(content)
                            path = None
                            if file_name is not None:
                                path = self.resource_handler.upload('novel', file_name)
                            print(path)
                            if path is not None:
                                self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, 1)
        except Exception as e:
            print(e)

