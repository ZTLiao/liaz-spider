import base64
import os.path
import re
import time
from io import BytesIO

import bs4
from PIL import Image
from selenium import webdriver

from constants import bucket, file_type
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.region_db import RegionDb


class ColaMangaSpider:
    def __init__(self, page_type=0):
        self.domain = 'https://www.colamanga.com'
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
        page_name = '2'
        if self.page_type == '0':
            page_name = '2'
        elif self.page_type == '1':
            page_name = '1'
        try:
            index = 0
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--headless')
            options.add_argument('--remote-debugging-port=9222')
            browser = webdriver.Chrome(options=options)
            while True:
                index += 1
                man_hua_url = self.domain + '/show?orderBy=update&status=' + page_name + '&page=' + str(index)
                print(man_hua_url)
                browser.get(man_hua_url)
                man_hua_content = browser.page_source
                man_hua_soup = bs4.BeautifulSoup(man_hua_content, 'lxml')
                li_items = man_hua_soup.select('li.fed-list-item')
                if len(li_items) == 0:
                    break
                for li_item in li_items:
                    detail_uri = li_item.find_all('a')[0].get('href')
                    print(detail_uri)
                    detail_url = self.domain + detail_uri
                    browser.get(detail_url)
                    detail_content = browser.page_source
                    man_hua_detail_soup = bs4.BeautifulSoup(detail_content, 'html.parser')
                    title = man_hua_detail_soup.select('div h1')[0].text
                    cover = man_hua_detail_soup.select('a.fed-list-pics')[0].get('data-original')
                    print(cover)
                    comic_id = self.comic_db.get_comic_id(title)
                    cookies = browser.get_cookies()
                    cookie = ''
                    index = 0
                    for c in cookies:
                        cookie += c['name'] + '=' + c['value']
                        if index != len(cookies) - 1:
                            cookie += ';'
                        index += 1
                    print(cookie)
                    file_name = self.file_item_handler.download(cover, headers={
                        'authority': 'res.colamanga.com',
                        'method': 'GET',
                        'path': cover.replace('https://res.colamanga.com', ''),
                        'scheme': 'https',
                        'Referer': self.domain + detail_uri,
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        'Cookie': '_va=13;__cf__bkm=fAoEV4kNh8nX20jA5dVeI47wipTm4dJiCkakbKGAjA1Vh/T3ERhPcr9nJUO53MZI',
                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'If-Modified-Since': 'Fri, 26 Aug 2022 16:19:40 GMT',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"macOS"',
                        'Sec-Fetch-Dest': 'image',
                        'Sec-Fetch-Mode': 'no-cors',
                        'Sec-Fetch-Site': 'same-site',
                    })
                    if comic_id is None or comic_id == 0:
                        file_name = self.file_item_handler.download(cover, headers={
                            'Referer': self.domain + detail_uri,
                        })
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    status_item = man_hua_detail_soup.find('span', string='状态')
                    status = status_item.find_next('a').text
                    print(status)
                    flag = 0
                    if status == '连载中':
                        flag = 1
                    author_item = man_hua_detail_soup.find('span', string='作者')
                    author_text = author_item.find_next('a').text
                    if len(author_text.strip()) == 0:
                        author_text = '佚名'
                    authors = author_text.strip().split(',')
                    author_ids = []
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
                    category_items = man_hua_detail_soup.find('span', string='类别').find_next('a')
                    category_ids = []
                    category_str = ''
                    category_index = 0
                    for category_item in category_items:
                        category = category_item.text
                        category = category.replace('\'', '\\\'')
                        self.category_db.save(category)
                        category_id = self.category_db.get_category_id(category)
                        category_ids.append(str(category_id))
                        category_str += category
                        if category_index != len(category_items) - 1:
                            category_str += ','
                        category_index += 1
                    category_id_str = ','.join(category_ids)
                    description_item = man_hua_detail_soup.find('span', string='简介')
                    description = description_item.find_parent('div').text.replace('简介', '').strip()
                    self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, 0, '')
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                    chapter_items = man_hua_detail_soup.select('a.fed-btns-info')
                    for chapter_item in reversed(chapter_items):
                        detail_uri = str(chapter_item.get('href'))
                        if not detail_uri.endswith('.html'):
                            continue
                        chapter_index += 1
                        chapter_name = chapter_item.text.strip()
                        count = self.comic_chapter_db.count(comic_id, chapter_name)
                        if count == 0:
                            self.comic_chapter_db.save(comic_id, chapter_name, chapter_index)
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                          chapter_name)
                            self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                        else:
                            print('comic_id : ', comic_id, ', chapter_name : ', chapter_name, ', chapter_index : ',
                                  chapter_index)
                            break
                        comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id(comic_id,
                                                                                      chapter_name)
                        chapter_url = self.domain + detail_uri
                        print(chapter_url)
                        browser.get(chapter_url)
                        chapter_content = browser.page_source
                        man_hua_chapter_soup = bs4.BeautifulSoup(chapter_content, 'lxml')
                        img_items = man_hua_chapter_soup.select('div.mh_comicpic img')
                        for i in range(0, len(img_items)):
                            img_item = img_items[i]
                            path = img_item.get('src')
                            is_click = False
                            while path is None:
                                print('index : ', i, ' 重新执行.')
                                if not is_click:
                                    is_click = True
                                    span_script = 'var newSpan = document.createElement("span"); newSpan.setAttribute("onclick", "__cr.reloadPic(this,' + str(
                                        i + 1) + ')"); newSpan.setAttribute("id", "newSpan' + str(
                                        i + 1) + '"); document.body.appendChild(newSpan); '
                                    browser.execute_script(span_script)
                                span_script = 'let newSpan = document.getElementById("newSpan' + str(
                                    i + 1) + '"); let clickEvent = new MouseEvent("click", {"view": window, "bubbles": true, "cancelable": false}); newSpan.dispatchEvent(clickEvent);'
                                browser.execute_script(span_script)
                                time.sleep(1)
                                chapter_content = browser.page_source
                                man_hua_chapter_soup = bs4.BeautifulSoup(chapter_content, 'lxml')
                                img_item = man_hua_chapter_soup.select('div.mh_comicpic img')[i]
                                path = img_item.get('src')
                            print(path)
                            if path is not None and len(path) != 0:
                                path_array = path.split('/')
                                file_name = path_array[len(path_array) - 1]
                                js = "let c = document.createElement('canvas');let ctx = c.getContext('2d');" \
                                     "let img = document.querySelectorAll('div.mh_comicpic img')[" + str(i) + "];" \
                                                                                                              "c.height=img.naturalHeight;c.width=img.naturalWidth;" \
                                                                                                              "ctx.drawImage(img, 0, 0,img.naturalWidth, img.naturalHeight);" \
                                                                                                              "let base64String = c.toDataURL(); return base64String;"
                                base64_str = browser.execute_script(js)
                                if len(base64_str) > 0:
                                    img = base64_to_image(base64_str)
                                    if img is not None:
                                        img.save(file_name + '.png')
                        chapter_content = browser.page_source
                        man_hua_chapter_soup = bs4.BeautifulSoup(chapter_content, 'lxml')
                        img_items = man_hua_chapter_soup.select('div.mh_comicpic img')
                        for i in range(0, len(img_items)):
                            img_item = img_items[i]
                            path = img_item.get('src')
                            page_index = i + 1
                            print(path)
                            if path is not None and len(path) != 0:
                                path = path.split('blob:')[1]
                                page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                              page_index)
                                if page_count == 0:
                                    path_array = path.split('/')
                                    file_name = path_array[len(path_array) - 1]
                                    file_name = file_name + '.png'
                                    if not os.path.exists(file_name):
                                        print('file_name : ', file_name, ' is not exist.')
                                        continue
                                    path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                         file_type.IMAGE_JPEG)
                                    print(path)
                                    self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                    page_index)
                                    self.comic_subscribe_db.upgrade(comic_id)
            browser.quit()
        except Exception as e:
            print(e)


def base64_to_image(base64_str):
    if len(base64_str) == 0:
        return None
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img
