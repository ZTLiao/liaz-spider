import time
from datetime import datetime, timedelta

import bs4
import requests

from constants import file_type, bucket
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.region_db import RegionDb


class DongManLaSpider:
    def __init__(self, page_type=0):
        self.domain = 'https://www.dongman.la'
        self.page_type = page_type
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.region_db = RegionDb()
        self.comic_db = ComicDb()
        self.comic_chapter_db = ComicChapterDb()
        self.comic_chapter_item_db = ComicChapterItemDb()
        self.asset_db = AssetDb()
        self.comic_subscribe_db = ComicSubscribeDb()
        self.file_item_handler = FileItemHandler()

    def parse(self):
        page_name = 'finish'
        if self.page_type == '0':
            page_name = 'finish'
        elif self.page_type == '1':
            page_name = 'serial'
        i = 0
        is_end = False
        while True:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            try:
                man_hua_url = self.domain + '/manhua/' + page_name + '/' + str(i) + '.html'
                print(man_hua_url)
                man_hua_response = requests.get(man_hua_url)
                man_hua_response_text = man_hua_response.text
                man_hua_soup = bs4.BeautifulSoup(man_hua_response_text, 'lxml')
                for man_han_item in man_hua_soup.select('div.cy_list_mh'):
                    if len(man_han_item.text.strip()) == 0:
                        is_end = True
                        break
                    for ul_item in man_han_item.find_all('ul'):
                        a_item = ul_item.select('a.pic')[0]
                        detail_url = self.domain + a_item.get('href')
                        print(detail_url)
                        self.get_detail(detail_url)
            except Exception as e:
                print(e)

    def get_detail(self, detail_url):
        try:
            detail_response = requests.get(detail_url)
            detail_response_text = detail_response.text
            detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
            for man_hua_info_item in detail_soup.select('div.cy_main .cy_info .cy_intro_l'):
                title = man_hua_info_item.select('.cy_title .detail-info-title')[0].text
                region = man_hua_info_item.select('.cy_xinxi span')[0].text.split('：')[1]
                self.region_db.save(region)
                region_id = self.region_db.get_region_id(region)
                cover_img_item = man_hua_info_item.select('.cy_info_cover img')[0]
                cover = cover_img_item.get('src')
                comic_id = self.comic_db.get_comic_id(title)
                if comic_id is None:
                    file_name = self.file_item_handler.download(cover)
                    if file_name is not None:
                        cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                              file_type.IMAGE_JPEG)
                    print(cover)
                    if cover is None:
                        cover = ''
                author_item = man_hua_info_item.select('.cy_xinxixi .detail-info-author')
                author_ids = []
                authors = []
                if len(author_item) == 1:
                    author_list = author_item[0].text.replace('作者：', '').strip().split('\n')
                    for author in author_list:
                        if len(author) > 0:
                            authors.append(author)
                else:
                    for a_item in author_item.find_all('a'):
                        author_list = a_item.text.replace('作者：', '').strip().split('\n')
                        for author in author_list:
                            if len(author) > 0:
                                authors.append(author)
                author_str = ''
                author_index = 0
                for author in authors:
                    author = author.replace('\'', '\\\'')
                    self.author_db.save(author)
                    author_id = self.author_db.get_author_id(author)
                    author_ids.append(str(author_id))
                    author_str += author
                    if author_index != len(authors) - 1:
                        author_str += ','
                    author_index += 1
                author_id_str = ','.join(author_ids)
                category_item = man_hua_info_item.select('.cy_xinxixi span')[1]
                category_ids = []
                categories = []
                if len(category_item) == 1:
                    category = category_item.text.replace('类别：', '').replace('，', '').strip()
                    if len(category) > 0:
                        for item in category.split(','):
                            categories.append(item)
                else:
                    for a_item in category_item.select('a'):
                        category = a_item.text.replace('类别：', '').replace('，', '').strip()
                        if len(category) > 0:
                            for item in category.split(','):
                                categories.append(item)
                category_str = ''
                category_index = 0
                for category in categories:
                    category = category.replace('\'', '\\\'')
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
                    category_ids.append(str(category_id))
                    category_str += category
                    if category_index != len(categories) - 1:
                        category_str += ','
                    category_index += 1
                category_id_str = ','.join(category_ids)
                description_item = man_hua_info_item.select('div.cy_xinxi p')[0]
                description = description_item.text
                li_items = detail_soup.select('div.cy_main .cy_zhangjie .cy_plist li')
                if len(li_items) == 0:
                    print('zhang jie is empty.')
                else:
                    flag = 0
                    if self.page_type == '1':
                        flag = 1
                    self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, region_id, region)
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    last_item = li_items[0]
                    chapter_name = last_item.find('p').text
                    count = self.comic_chapter_db.count(comic_id, chapter_name)
                    if count != 0:
                        print('comic_id : ', comic_id, ', chapter_name : ', chapter_name, ' is exist.')
                        continue
                    for li_item in reversed(li_items):
                        chapter_index += 1
                        page_url = li_item.find('a').get('href')
                        print(page_url)
                        chapter_name = li_item.find('p').text
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        page_response = requests.get(page_url + 'all.html')
                        page_response_text = page_response.text
                        page_soup = bs4.BeautifulSoup(page_response_text, 'lxml')
                        page_index = 0
                        for lazy_box_item in page_soup.select('div.chapter-images .imgListBox .lazyBox'):
                            page_index += 1
                            page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                          page_index)
                            if page_count == 0:
                                path = lazy_box_item.find('img').get('data-src')
                                print(path)
                                if len(path.replace('https://img.dongman.la', '')) == 0:
                                    continue
                                file_name = self.file_item_handler.download(path)
                                if file_name is not None:
                                    path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                         file_type.IMAGE_JPEG)
                                print(path)
                                self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                page_index)
                                self.comic_subscribe_db.upgrade(comic_id)
        except Exception as e:
            print(e)

    def job(self):
        try:
            now = datetime.now()
            yesterday = (now - timedelta(days=1)).strftime("%m-%d")
            man_hua_url = self.domain
            print(man_hua_url)
            man_hua_response = requests.get(man_hua_url)
            man_hua_response_text = man_hua_response.text
            man_hua_soup = bs4.BeautifulSoup(man_hua_response_text, 'lxml')
            new_list_item = man_hua_soup.select('div.cy_content .cy_main .cy_new_list')[0]
            for man_han_item in new_list_item.select('li'):
                date = man_han_item.find('dfn').text
                if yesterday != date:
                    print('now : ', now, 'date : ', date)
                    continue
                a_item = man_han_item.find_all('a')[0]
                detail_url = a_item.get('href')
                print(detail_url)
                self.get_detail(detail_url)
        except Exception as e:
            print(e)
