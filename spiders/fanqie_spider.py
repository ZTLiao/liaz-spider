from datetime import datetime

import requests
import bs4
import json
import re
import time
import system.global_vars

from config.redis_config import RedisConfig
from constants import bucket, file_type, status
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

ua = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0.0.0 "
    "Safari/537.36"
)


class FanQieSpider:
    def __init__(self):
        self.domain = 'https://fanqienovel.com'
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
        now = datetime.now().strftime("%Y-%m-%d")
        index = 0
        headers = {
            "User-Agent": ua
        }
        proxies = {
            "http": None,
            "https": None
        }
        while True:
            xiao_shuo_url = self.domain + '/api/author/library/book_list/v0/?page_count=18&page_index=' + str(
                index) + '&gender=-1&category_id=-1&creation_status=-1&word_count=-1&book_type=-1&sort=0'
            print(xiao_shuo_url)
            xiao_shuo_response = requests.get(xiao_shuo_url)
            xiao_shuo_response_text = xiao_shuo_response.text
            book_list_response = json.loads(xiao_shuo_response_text)
            book_list = book_list_response['data']['book_list']
            for book in book_list:
                book_id = book['book_id']
                xiao_shuo_detail_url = self.domain + '/page/' + str(book_id)
                print(xiao_shuo_detail_url)
                xiao_shuo_detail_response = requests.get(xiao_shuo_detail_url, headers=headers, timeout=20,
                                                         proxies=proxies)
                xiao_shuo_detail_response_text = xiao_shuo_detail_response.text
                xiao_shuo_detail_soup = bs4.BeautifulSoup(xiao_shuo_detail_response_text, "html.parser")
                title = xiao_shuo_detail_soup.find("h1").text
                title = rename(title)
                info = xiao_shuo_detail_soup.find("div", class_="page-header-info").get_text()
                description = xiao_shuo_detail_soup.find("div", class_="page-abstract-content").get_text()
                script_tag = xiao_shuo_detail_soup.find('script', type='application/ld+json')
                json_data = json.loads(script_tag.string)
                images_data = json_data.get('image', [])
                cover = images_data[0]
                novel_id = self.novel_db.get_novel_id(title)
                if novel_id is None or novel_id == 0:
                    file_name = self.file_item_handler.download(cover)
                    if file_name is not None:
                        cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                    print(cover)
                    if cover is None:
                        cover = ''
                author = xiao_shuo_detail_soup.find('span', class_='author-name-text').get_text()
                self.author_db.save(author)
                author_id = self.author_db.get_author_id(author)
                category_items = xiao_shuo_detail_soup.find_all('span', class_='info-label-grey')
                category_ids = []
                category_str = ''
                category_index = 0
                for category_item in category_items:
                    category = category_item.text.strip()
                    category = category.replace('\'', '\\\'').replace(',', '').replace('#', '').replace('\n',
                                                                                                        '').strip()
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
                    category_ids.append(str(category_id))
                    category_str += category
                    if category_index != len(category_items) - 1:
                        category_str += ','
                    category_index += 1
                category_id_str = ','.join(category_ids)
                print('title : ', title, ', info : ', info, ', description : ', description)
                self.novel_db.save(title, cover, description, 1, category_id_str, category_str, str(author_id),
                                   author, 0, '')
                novel_id = self.novel_db.get_novel_id(title)
                asset_key = title + '|' + author
                self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, str(author_id))
                chapter_index = self.novel_chapter_db.get_seq_no(novel_id)
                chapters = xiao_shuo_detail_soup.find_all("div", class_="chapter-item")
                for i, chapter in enumerate(chapters):
                    if system.global_vars.application.get_close_status() == status.YES:
                        print('fan qie is close.')
                        return
                    time.sleep(0.25)
                    chapter_index += 1
                    chapter_name = chapter.find("a").get_text()
                    chapter_name = rename(chapter_name)
                    count = self.novel_chapter_db.count(novel_id, chapter_name)
                    if count != 0:
                        print('novel_id : ', novel_id, ', chapter_name : ', chapter_name, ' is exist.')
                        break
                    if count == 0:
                        self.novel_chapter_db.save(novel_id, chapter_name, chapter_index)
                        novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                        self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                    novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                    chapter_url = chapter.find("a")["href"]
                    chapter_id = re.search(r"/reader/(\d+)", chapter_url).group(1)
                    api_url = (f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&"
                               f"parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id="
                               f"{chapter_id}&item_id={chapter_id}")
                    chapter_content = None
                    retry_count = 1
                    while retry_count < 4:
                        try:
                            api_response = requests.get(api_url, headers=headers, timeout=5, proxies=proxies)
                            api_data = api_response.json()
                        except Exception as e:
                            print(e)
                            if retry_count == 1:
                                print(f"第 ({retry_count}/3) 次重试获取章节内容")
                            retry_count += 1
                            continue
                        if "data" in api_data and "content" in api_data["data"]:
                            chapter_content = api_data["data"]["content"]
                            break
                        else:
                            if retry_count == 1:
                                print(f"{chapter_name} 获取失败，正在尝试重试...")
                            print(f"第 ({retry_count}/3) 次重试获取章节内容")
                            retry_count += 1
                    if retry_count == 4:
                        print(f"无法获取章节内容: {chapter_name}，跳过。")
                        continue
                    chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)
                    chapter_text = re.sub(r"<p>", "\n", chapter_text)
                    chapter_text = re.sub(r"</?\w+>", "", chapter_text)
                    chapter_text = fix_publisher(chapter_text)
                    content = ''
                    if chapter_text is None:
                        continue
                    content += f"\n\n\n{chapter_name}\n{chapter_text}"
                    print(f"已获取 {chapter_name}")
                    count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id, 1)
                    if count == 0:
                        content = str(content).replace('<div class="read_txt" id="content">',
                                                       '').replace(
                            '</div>', '').replace('<br/>', '\n')
                        print(content)
                        file_name = self.file_item_handler.write_content(content)
                        path = None
                        if file_name is not None:
                            path = self.file_item_handler.upload(bucket.NOVEL, file_name, file_type.TEXT_PLAIN)
                        print(path)
                        if path is not None:
                            self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, 1)
                            self.novel_subscribe_db.upgrade(novel_id)
                self.redis_util.delete(NOVEL_DETAIL + str(novel_id))
            index += 1

    def job(self):
        now = datetime.now().strftime("%Y-%m-%d")
        index = 0
        headers = {
            "User-Agent": ua
        }
        proxies = {
            "http": None,
            "https": None
        }
        while True:
            xiao_shuo_url = self.domain + '/api/author/library/book_list/v0/?page_count=18&page_index=' + str(
                index) + '&gender=-1&category_id=-1&creation_status=-1&word_count=-1&book_type=-1&sort=0'
            print(xiao_shuo_url)
            xiao_shuo_response = requests.get(xiao_shuo_url)
            xiao_shuo_response_text = xiao_shuo_response.text
            book_list_response = json.loads(xiao_shuo_response_text)
            book_list = book_list_response['data']['book_list']
            for book in book_list:
                book_id = book['book_id']
                last_chapter_time = book['last_chapter_time']
                if last_chapter_time is not None:
                    date = datetime.fromtimestamp(int(last_chapter_time)).strftime('%Y-%m-%d')
                    if now != date:
                        print('novel date : ', date)
                        return
                xiao_shuo_detail_url = self.domain + '/page/' + str(book_id)
                print(xiao_shuo_detail_url)
                xiao_shuo_detail_response = requests.get(xiao_shuo_detail_url, headers=headers, timeout=20,
                                                         proxies=proxies)
                xiao_shuo_detail_response_text = xiao_shuo_detail_response.text
                xiao_shuo_detail_soup = bs4.BeautifulSoup(xiao_shuo_detail_response_text, "html.parser")
                title = xiao_shuo_detail_soup.find("h1").text
                title = rename(title)
                info = xiao_shuo_detail_soup.find("div", class_="page-header-info").get_text()
                description = xiao_shuo_detail_soup.find("div", class_="page-abstract-content").get_text()
                script_tag = xiao_shuo_detail_soup.find('script', type='application/ld+json')
                json_data = json.loads(script_tag.string)
                images_data = json_data.get('image', [])
                cover = images_data[0]
                novel_id = self.novel_db.get_novel_id(title)
                if novel_id is None or novel_id == 0:
                    file_name = self.file_item_handler.download(cover)
                    if file_name is not None:
                        cover = self.file_item_handler.upload(bucket.COVER, file_name, file_type.IMAGE_JPEG)
                    print(cover)
                    if cover is None:
                        cover = ''
                author = xiao_shuo_detail_soup.find('span', class_='author-name-text').get_text()
                self.author_db.save(author)
                author_id = self.author_db.get_author_id(author)
                category_items = xiao_shuo_detail_soup.find_all('span', class_='info-label-grey')
                category_ids = []
                category_str = ''
                category_index = 0
                for category_item in category_items:
                    category = category_item.text.strip()
                    category = category.replace('\'', '\\\'').replace(',', '').replace('#', '').replace('\n',
                                                                                                        '').strip()
                    self.category_db.save(category)
                    category_id = self.category_db.get_category_id(category)
                    category_ids.append(str(category_id))
                    category_str += category
                    if category_index != len(category_items) - 1:
                        category_str += ','
                    category_index += 1
                category_id_str = ','.join(category_ids)
                print('title : ', title, ', info : ', info, ', description : ', description)
                self.novel_db.save(title, cover, description, 1, category_id_str, category_str, str(author_id),
                                   author, 0, '')
                novel_id = self.novel_db.get_novel_id(title)
                asset_key = title + '|' + author
                self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, str(author_id))
                chapter_index = self.novel_chapter_db.get_seq_no(novel_id)
                chapters = xiao_shuo_detail_soup.find_all("div", class_="chapter-item")
                for i, chapter in enumerate(chapters):
                    if system.global_vars.application.get_close_status() == status.YES:
                        print('fan qie is close.')
                        return
                    time.sleep(0.25)
                    chapter_index += 1
                    chapter_name = chapter.find("a").get_text()
                    chapter_name = rename(chapter_name)
                    count = self.novel_chapter_db.count(novel_id, chapter_name)
                    if count != 0:
                        print('novel_id : ', novel_id, ', chapter_name : ', chapter_name, ' is exist.')
                        break
                    if count == 0:
                        self.novel_chapter_db.save(novel_id, chapter_name, chapter_index)
                        novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                        self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                    novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id(novel_id, chapter_name)
                    chapter_url = chapter.find("a")["href"]
                    chapter_id = re.search(r"/reader/(\d+)", chapter_url).group(1)
                    api_url = (f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&"
                               f"parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id="
                               f"{chapter_id}&item_id={chapter_id}")
                    chapter_content = None
                    retry_count = 1
                    while retry_count < 4:
                        try:
                            api_response = requests.get(api_url, headers=headers, timeout=5, proxies=proxies)
                            api_data = api_response.json()
                        except Exception as e:
                            print(e)
                            if retry_count == 1:
                                print(f"第 ({retry_count}/3) 次重试获取章节内容")
                            retry_count += 1
                            continue
                        if "data" in api_data and "content" in api_data["data"]:
                            chapter_content = api_data["data"]["content"]
                            break
                        else:
                            if retry_count == 1:
                                print(f"{chapter_name} 获取失败，正在尝试重试...")
                            print(f"第 ({retry_count}/3) 次重试获取章节内容")
                            retry_count += 1
                    if retry_count == 4:
                        print(f"无法获取章节内容: {chapter_name}，跳过。")
                        continue
                    chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)
                    chapter_text = re.sub(r"<p>", "\n", chapter_text)
                    chapter_text = re.sub(r"</?\w+>", "", chapter_text)
                    chapter_text = fix_publisher(chapter_text)
                    content = ''
                    if chapter_text is None:
                        continue
                    content += f"\n\n\n{chapter_name}\n{chapter_text}"
                    print(f"已获取 {chapter_name}")
                    count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id, 1)
                    if count == 0:
                        content = str(content).replace('<div class="read_txt" id="content">',
                                                       '').replace(
                            '</div>', '').replace('<br/>', '\n')
                        print(content)
                        file_name = self.file_item_handler.write_content(content)
                        path = None
                        if file_name is not None:
                            path = self.file_item_handler.upload(bucket.NOVEL, file_name, file_type.TEXT_PLAIN)
                        print(path)
                        if path is not None:
                            self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, 1)
                            self.novel_subscribe_db.upgrade(novel_id)
                self.redis_util.delete(NOVEL_DETAIL + str(novel_id))
            index += 1


def rename(name):
    illegal_characters_pattern = r'[\/:*?"<>|]'
    replacement_dict = {
        '/': '／',
        ':': '：',
        '*': '＊',
        '?': '？',
        '"': '“',
        '<': '＜',
        '>': '＞',
        '|': '｜'
    }
    sanitized_path = re.sub(illegal_characters_pattern, lambda x: replacement_dict[x.group(0)], name)
    return sanitized_path


def fix_publisher(text):
    text = re.sub(r'<p class=".*?">', '', text)
    text = re.sub(r'<!--\?xml.*?>', '', text)
    text = re.sub(r'<link .*?/>', '', text)
    text = re.sub(r'<meta .*?/>', '', text)
    text = re.sub(r'<h1 .*?>', '', text)
    text = re.sub(r'<br/>', '', text)
    text = re.sub(r'<!DOCTYPE html .*?>', '', text)
    text = re.sub(r'<span .*?>', '', text)
    text = re.sub(r'<html .*?>', '', text)
    return text
