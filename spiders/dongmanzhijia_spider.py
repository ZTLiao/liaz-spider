import hashlib
import json
import re
import time
from html import unescape

import bs4
from datetime import datetime

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from asn1crypto import keys, core

import base64

import requests

from constants import bucket, file_type
from handler.file_item_handler import FileItemHandler
from interfaces import dongmanzhijia_comic_pb2, dongmanzhijia_novel_pb2
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.comic_volume_db import ComicVolumeDb
from storage.novel_chapter_db import NovelChapterDb
from storage.novel_chapter_item_db import NovelChapterItemDb
from storage.novel_db import NovelDb
from storage.novel_subscribe_db import NovelSubscribeDb
from storage.novel_volume_db import NovelVolumeDb
from storage.region_db import RegionDb

random_generator = Random.new().read

PRIVATE_KEY = 'MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAK8nNR1lTnIfIes6oRWJNj3mB6OssDGx0uGMpgpbVCpf6+VwnuI2stmhZNoQcM417Iz7WqlPzbUmu9R4dEKmLGEEqOhOdVaeh9Xk2IPPjqIu5TbkLZRxkY3dJM1htbz57d/roesJLkZXqssfG5EJauNc+RcABTfLb4IiFjSMlTsnAgMBAAECgYEAiz/pi2hKOJKlvcTL4jpHJGjn8+lL3wZX+LeAHkXDoTjHa47g0knYYQteCbv+YwMeAGupBWiLy5RyyhXFoGNKbbnvftMYK56hH+iqxjtDLnjSDKWnhcB7089sNKaEM9Ilil6uxWMrMMBH9v2PLdYsqMBHqPutKu/SigeGPeiB7VECQQDizVlNv67go99QAIv2n/ga4e0wLizVuaNBXE88AdOnaZ0LOTeniVEqvPtgUk63zbjl0P/pzQzyjitwe6HoCAIpAkEAxbOtnCm1uKEp5HsNaXEJTwE7WQf7PrLD4+BpGtNKkgja6f6F4ld4QZ2TQ6qvsCizSGJrjOpNdjVGJ7bgYMcczwJBALvJWPLmDi7ToFfGTB0EsNHZVKE66kZ/8Stx+ezueke4S556XplqOflQBjbnj2PigwBN/0afT+QZUOBOjWzoDJkCQClzo+oDQMvGVs9GEajS/32mJ3hiWQZrWvEzgzYRqSf3XVcEe7PaXSd8z3y3lACeeACsShqQoc8wGlaHXIJOHTcCQQCZw5127ZGs8ZDTSrogrH73Kw/HvX55wGAeirKYcv28eauveCG7iyFR0PFB/P/EDZnyb+ifvyEFlucPUI0+Y87F'


class DongManZhiJiaSpider:
    def __init__(self, page_type=0):
        self.domain_v3 = 'https://nnv3api.idmzj.com'
        self.domain_v4 = 'https://v4api.idmzj.com'
        self.domain_novel = 'http://jurisdiction.idmzj.com'
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
        self.novel_db = NovelDb()
        self.novel_volume_db = NovelVolumeDb()
        self.novel_chapter_db = NovelChapterDb()
        self.novel_chapter_item_db = NovelChapterItemDb()
        self.novel_subscribe_db = NovelSubscribeDb()
        self.file_item_handler = FileItemHandler()
        self.uid = 100091600

    def parse(self):
        if self.page_type == '0':
            self.parse_comic()
        elif self.page_type == '1':
            self.parse_novel()

    def parse_comic(self):
        i = 0
        while True:
            i += 1
            try:
                man_hua_url = self.domain_v4 + '/comic/update/list/100/' + str(i) + '?channel=android&timestamp=' + str(
                    int(time.time())) + '&uid=' + str(self.uid)
                print(man_hua_url)
                man_hua_response = requests.get(man_hua_url)
                man_hua_response_text = man_hua_response.text
                comic_update_list_response = dongmanzhijia_comic_pb2.ComicUpdateListResponseProto()
                comic_update_list_response.ParseFromString(rsa_decrypt(man_hua_response_text, PRIVATE_KEY))
                print(comic_update_list_response)
                if comic_update_list_response.errno != 0:
                    continue
                comic_update_list = comic_update_list_response.data
                if len(comic_update_list) == 0:
                    print('comic is empty.')
                    break
                for value in comic_update_list:
                    title = value.title
                    comic_id = self.comic_db.get_comic_id(title)
                    last_update_chapter_name = value.lastUpdateChapterName
                    if len(last_update_chapter_name) == 0:
                        continue
                    count = self.comic_chapter_db.count(comic_id, last_update_chapter_name)
                    if count != 0:
                        print('comic title : ', title, ', last update chapter name : ', last_update_chapter_name)
                        continue
                    comic_id = value.comicId
                    try:
                        comic_detail_url = self.domain_v4 + '/comic/detail/' + str(
                            comic_id) + '?channel=android&timestamp=' + str(
                            int(time.time())) + '&uid=' + str(self.uid)
                        print(comic_detail_url)
                        comic_detail_response = requests.get(comic_detail_url)
                        comic_detail_response_text = comic_detail_response.text
                        comic_detail_response = dongmanzhijia_comic_pb2.ComicDetailResponseProto()
                        comic_detail_response.ParseFromString(rsa_decrypt(comic_detail_response_text, PRIVATE_KEY))
                        print(comic_detail_response)
                        if comic_detail_response.errno != 0:
                            continue
                        comic_detail = comic_detail_response.data
                        cover = comic_detail.cover
                        title = comic_detail.title
                        comic_id = self.comic_db.get_comic_id(title)
                        if comic_id is None:
                            file_name = self.file_item_handler.download(cover)
                            if file_name is not None:
                                cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                      file_type.IMAGE_JPEG)
                            print(cover)
                            if cover is None:
                                cover = ''
                        authors = comic_detail.authors
                        author_str = ''
                        author_id_str = ''
                        if len(authors) != 0:
                            author_ids = []
                            index = 0
                            for tag in authors:
                                author = tag.tagName
                                author = author.replace('\'', '\\\'')
                                self.author_db.save(author)
                                author_id = self.author_db.get_author_id(author)
                                author_ids.append(str(author_id))
                                author_str += author
                                if index != len(authors) - 1:
                                    author_str += ','
                                index += 1
                            author_id_str = ','.join(author_ids)
                        categories = comic_detail.types
                        category_str = ''
                        category_id_str = ''
                        if len(categories) != 0:
                            category_ids = []
                            index = 0
                            for tag in categories:
                                category = tag.tagName
                                category = category.replace('\'', '\\\'')
                                self.category_db.save(category)
                                category_id = self.category_db.get_category_id(category)
                                category_ids.append(str(category_id))
                                category_str += category
                                if index != len(categories) - 1:
                                    category_str += ','
                                index += 1
                            category_id_str = ','.join(category_ids)
                        description = comic_detail.description
                        status = comic_detail.status
                        flag = 0
                        if status == '连载中':
                            flag = 1
                        self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                           author_id_str,
                                           author_str, 0, '')
                        comic_id = self.comic_db.get_comic_id(title)
                        asset_key = title + '|' + author_str
                        self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                        volumes = comic_detail.chapters
                        volume_index = 0
                        for volume in volumes:
                            volume_index += 1
                            volume_name = volume.title
                            self.comic_volume_db.save(comic_id, volume_name, volume_index)
                            comic_volume_id = self.comic_volume_db.get_comic_volume_id(comic_id, volume_name)
                            chapters = volume.data
                            is_comic_chapter_exists = False
                            for chapter in reversed(chapters):
                                chapter_name = chapter.chapterTitle
                                seq_no = chapter.chapterOrder
                                count = self.comic_chapter_db.count_by_comic_volume_id(comic_id, comic_volume_id,
                                                                                       chapter_name)
                                if count == 0:
                                    self.comic_chapter_db.save_by_comic_volume_id(comic_id, comic_volume_id,
                                                                                  chapter_name,
                                                                                  seq_no)
                                    comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id_by_comic_volume_id(
                                        comic_id,
                                        comic_volume_id,
                                        chapter_name)
                                    if comic_chapter_id is not None:
                                        self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                                        self.comic_db.upgrade(comic_id)
                                else:
                                    is_comic_chapter_exists = True
                                    break
                                comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id_by_comic_volume_id(
                                    comic_id,
                                    comic_volume_id,
                                    chapter_name)
                                comic_chapter_url = self.domain_v4 + '/comic/chapter/' + str(
                                    comic_detail.id) + '/' + str(
                                    chapter.chapterId) + '?channel=android&timestamp=' + str(
                                    int(time.time())) + '&uid=' + str(self.uid)
                                print(comic_chapter_url)
                                comic_chapter_response = requests.get(comic_chapter_url)
                                comic_chapter_response_text = comic_chapter_response.text
                                comic_chapter_response = dongmanzhijia_comic_pb2.ComicChapterResponseProto()
                                comic_chapter_response.ParseFromString(
                                    rsa_decrypt(comic_chapter_response_text, PRIVATE_KEY))
                                print(comic_chapter_response)
                                if comic_chapter_response.errno != 0:
                                    continue
                                comic_chapter = comic_chapter_response.data
                                if comic_chapter is None:
                                    continue
                                page_url = comic_chapter.pageUrlHD
                                if len(page_url) != 0:
                                    page_url = comic_chapter.pageUrl
                                page_index = 0
                                for path in page_url:
                                    page_index += 1
                                    page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        print(path)
                                        file_name = self.file_item_handler.download(path, headers={
                                            'Referer': 'http://www.dmzj.com/',
                                        })
                                        if file_name is not None:
                                            path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                                 file_type.IMAGE_JPEG)
                                        print(path)
                                        self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                        page_index)
                                        self.comic_subscribe_db.upgrade(comic_id)
                            if is_comic_chapter_exists:
                                print('comic_id : ', comic_id, ', comic_volume_id : ', comic_volume_id, ' is exists.')
                                continue
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

    def comic_job(self):
        now = datetime.now().strftime("%Y-%m-%d")
        i = 0
        while True:
            i += 1
            man_hua_url = self.domain_v4 + '/comic/update/list/100/' + str(i) + '?channel=android&timestamp=' + str(
                int(time.time())) + '&uid=' + str(self.uid)
            print(man_hua_url)
            man_hua_response = requests.get(man_hua_url)
            man_hua_response_text = man_hua_response.text
            comic_update_list_response = dongmanzhijia_comic_pb2.ComicUpdateListResponseProto()
            comic_update_list_response.ParseFromString(rsa_decrypt(man_hua_response_text, PRIVATE_KEY))
            print(comic_update_list_response)
            if comic_update_list_response.errno != 0:
                continue
            comic_update_list = comic_update_list_response.data
            if len(comic_update_list) == 0:
                print('comic is empty.')
                break
            for value in comic_update_list:
                last_update_time = value.lastUpdatetime
                date = datetime.fromtimestamp(last_update_time).strftime('%Y-%m-%d')
                if now != date:
                    print('comic date : ', date)
                    return
                title = value.title
                comic_id = self.comic_db.get_comic_id(title)
                last_update_chapter_name = value.lastUpdateChapterName
                if len(last_update_chapter_name) == 0:
                    continue
                count = self.comic_chapter_db.count(comic_id, last_update_chapter_name)
                if count != 0:
                    print('comic title : ', title, ', last update chapter name : ', last_update_chapter_name)
                    return
                comic_id = value.comicId
                try:
                    comic_detail_url = self.domain_v4 + '/comic/detail/' + str(
                        comic_id) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    print(comic_detail_url)
                    comic_detail_response = requests.get(comic_detail_url)
                    comic_detail_response_text = comic_detail_response.text
                    comic_detail_response = dongmanzhijia_comic_pb2.ComicDetailResponseProto()
                    comic_detail_response.ParseFromString(rsa_decrypt(comic_detail_response_text, PRIVATE_KEY))
                    print(comic_detail_response)
                    if comic_detail_response.errno != 0:
                        continue
                    comic_detail = comic_detail_response.data
                    cover = comic_detail.cover
                    title = comic_detail.title
                    comic_id = self.comic_db.get_comic_id(title)
                    if comic_id is None:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    authors = comic_detail.authors
                    author_str = ''
                    author_id_str = ''
                    if len(authors) != 0:
                        author_ids = []
                        index = 0
                        for tag in authors:
                            author = tag.tagName
                            author = author.replace('\'', '\\\'')
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if index != len(authors) - 1:
                                author_str += ','
                            index += 1
                        author_id_str = ','.join(author_ids)
                    categories = comic_detail.types
                    category_str = ''
                    category_id_str = ''
                    if len(categories) != 0:
                        category_ids = []
                        index = 0
                        for tag in categories:
                            category = tag.tagName
                            category = category.replace('\'', '\\\'')
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                    description = comic_detail.description
                    status = comic_detail.status
                    flag = 0
                    if status == '连载中':
                        flag = 1
                    self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, 0, '')
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    volumes = comic_detail.chapters
                    volume_index = 0
                    for volume in reversed(volumes):
                        volume_index += 1
                        volume_name = volume.title
                        self.comic_volume_db.save(comic_id, volume_name, volume_index)
                        comic_volume_id = self.comic_volume_db.get_comic_volume_id(comic_id, volume_name)
                        chapters = volume.data
                        is_comic_chapter_exists = False
                        for chapter in reversed(chapters):
                            chapter_name = chapter.chapterTitle
                            seq_no = chapter.chapterOrder
                            count = self.comic_chapter_db.count_by_comic_volume_id(comic_id, comic_volume_id,
                                                                                   chapter_name)
                            if count == 0:
                                self.comic_chapter_db.save_by_comic_volume_id(comic_id, comic_volume_id, chapter_name,
                                                                              seq_no)
                                comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id_by_comic_volume_id(
                                    comic_id,
                                    comic_volume_id,
                                    chapter_name)
                                if comic_chapter_id is not None:
                                    self.asset_db.update(comic_id, 1, chapter_name, comic_chapter_id)
                                    self.comic_db.upgrade(comic_id)
                            else:
                                is_comic_chapter_exists = True
                                break
                            comic_chapter_id = self.comic_chapter_db.get_comic_chapter_id_by_comic_volume_id(comic_id,
                                                                                                             comic_volume_id,
                                                                                                             chapter_name)
                            comic_chapter_url = self.domain_v4 + '/comic/chapter/' + str(comic_detail.id) + '/' + str(
                                chapter.chapterId) + '?channel=android&timestamp=' + str(
                                int(time.time())) + '&uid=' + str(self.uid)
                            print(comic_chapter_url)
                            comic_chapter_response = requests.get(comic_chapter_url)
                            comic_chapter_response_text = comic_chapter_response.text
                            comic_chapter_response = dongmanzhijia_comic_pb2.ComicChapterResponseProto()
                            comic_chapter_response.ParseFromString(
                                rsa_decrypt(comic_chapter_response_text, PRIVATE_KEY))
                            print(comic_chapter_response)
                            if comic_chapter_response.errno != 0:
                                continue
                            comic_chapter = comic_chapter_response.data
                            if comic_chapter is None:
                                print('comic chapter is none.')
                                return
                            page_url = comic_chapter.pageUrlHD
                            if len(page_url) != 0:
                                page_url = comic_chapter.pageUrl
                            page_index = 0
                            for path in page_url:
                                page_index += 1
                                page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                              page_index)
                                if page_count == 0:
                                    print(path)
                                    file_name = self.file_item_handler.download(path, headers={
                                        'Referer': 'http://www.dmzj.com/',
                                    })
                                    if file_name is not None:
                                        path = self.file_item_handler.upload(bucket.COMIC, file_name,
                                                                             file_type.IMAGE_JPEG)
                                    print(path)
                                    self.comic_chapter_item_db.save(comic_chapter_id, comic_id, path,
                                                                    page_index)
                                    self.comic_subscribe_db.upgrade(comic_id)
                        if is_comic_chapter_exists:
                            print('comic_id : ', comic_id, ', comic_volume_id : ', comic_volume_id, ' is exists.')
                            continue
                except Exception as e:
                    print(e)

    def parse_novel(self):
        i = 0
        while True:
            xiao_shuo_url = self.domain_v3 + '/novel/recentUpdate/' + str(i) + '.json?channel=android&timestamp=' + str(
                int(time.time()))
            print(xiao_shuo_url)
            xiao_shuo_response = requests.get(xiao_shuo_url)
            xiao_shuo_response_text = xiao_shuo_response.text
            result = json.loads(xiao_shuo_response_text)
            if len(result) == 0:
                print('xiao shuo is empty.')
                break
            print(result)
            for novel_detail in result:
                try:
                    print(novel_detail)
                    novel_id = novel_detail['id']
                    novel_detail_url = self.domain_v4 + '/novel/detail/' + str(
                        novel_id) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    novel_detail_response = requests.get(novel_detail_url)
                    novel_detail_response_text = novel_detail_response.text
                    novel_detail_response = dongmanzhijia_novel_pb2.NovelDetailResponseProto()
                    novel_detail_response.ParseFromString(
                        rsa_decrypt(novel_detail_response_text, PRIVATE_KEY))
                    print(novel_detail_response)
                    if novel_detail_response.errno != 0:
                        continue
                    novel_detail = novel_detail_response.data
                    print(novel_detail)
                    cover = novel_detail.cover
                    title = novel_detail.name
                    region = novel_detail.zone
                    self.region_db.save(region)
                    region_id = self.region_db.get_region_id(region)
                    novel_id = self.novel_db.get_novel_id(title)
                    if novel_id is None:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    authors = novel_detail.authors
                    author_str = ''
                    author_id_str = ''
                    if len(authors) != 0:
                        author_ids = []
                        index = 0
                        for author in str(authors).split('/'):
                            author = author.replace('\'', '\\\'')
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if index != len(authors) - 1:
                                author_str += ','
                            index += 1
                        if author_str.endswith(','):
                            author_str = author_str[:-1]
                        author_id_str = ','.join(author_ids)
                    categories = novel_detail.types
                    category_str = ''
                    category_id_str = ''
                    if len(categories) != 0:
                        category_ids = []
                        index = 0
                        for category in str(categories).split('/'):
                            category = category.replace('\'', '').replace('[', '').replace(']', '')
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                    description = novel_detail.introduction
                    status = novel_detail.status
                    flag = 0
                    if status == '连载中':
                        flag = 1
                    self.novel_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, region_id, region)
                    novel_id = self.novel_db.get_novel_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, author_id_str)
                    novel_chapter_url = self.domain_v4 + '/novel/chapter/' + str(
                        novel_detail.novelId) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    print(novel_chapter_url)
                    novel_chapter_response = requests.get(novel_chapter_url)
                    novel_chapter_response_text = novel_chapter_response.text
                    novel_chapter_response = dongmanzhijia_novel_pb2.NovelChapterResponseProto()
                    novel_chapter_response.ParseFromString(
                        rsa_decrypt(novel_chapter_response_text, PRIVATE_KEY))
                    print(novel_chapter_response)
                    if novel_chapter_response.errno != 0:
                        continue
                    volumes = novel_chapter_response.data
                    volume_index = 0
                    for volume in volumes:
                        volume_index += 1
                        volume_name = volume.volumeName
                        self.novel_volume_db.save(novel_id, volume_name, volume_index)
                        novel_volume_id = self.novel_volume_db.get_novel_volume_id(novel_id, volume_name)
                        chapters = volume.chapters
                        for chapter in chapters:
                            chapter_name = chapter.chapterName
                            seq_no = chapter.chapterOrder
                            count = self.novel_chapter_db.count_by_novel_volume_id(novel_id, novel_volume_id,
                                                                                   chapter_name)
                            self.novel_chapter_db.save_by_novel_volume_id(novel_id, novel_volume_id, chapter_name,
                                                                          seq_no)

                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            if count == 0 and novel_chapter_id is not None:
                                self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                                self.novel_db.upgrade(novel_id)
                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            ts = str(int(time.time()))
                            path = '/lnovel/' + str(volume.volumeId) + '_' + str(chapter.chapterId) + '.txt'
                            key = 'IBAAKCAQEAsUAdKtXNt8cdrcTXLsaFKj9bSK1nEOAROGn2KJXlEVekcPssKUxSN8dsfba51kmHM'
                            key += path
                            key += ts
                            md5 = hashlib.md5()
                            md5.update(key.encode('utf8'))
                            key = md5.hexdigest().lower()
                            novel_chapter_url = self.domain_novel + path + '?t=' + ts + '&k=' + key
                            print(novel_chapter_url)
                            content_response = requests.get(novel_chapter_url)
                            content = content_response.text
                            if len(content) == 0:
                                continue
                            soup = bs4.BeautifulSoup(content, 'lxml')
                            img_tags = soup.find_all('img')
                            page_index = 0
                            if len(img_tags) != 0:
                                for img in img_tags:
                                    path = img.get('src')
                                    print(path)
                                    page_index += 1
                                    if novel_chapter_id is None:
                                        self.novel_chapter_db.save_by_novel_volume_id(novel_id, novel_volume_id,
                                                                                      chapter_name, seq_no)
                                    novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                        novel_id, novel_volume_id, chapter_name)
                                    page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        file_name = self.file_item_handler.download(path, headers={
                                            'Referer': 'http://www.dmzj.com/',
                                        })
                                        if file_name is not None:
                                            path = self.file_item_handler.upload(bucket.INSET, file_name,
                                                                                 file_type.IMAGE_JPEG)
                                        print(path)
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path,
                                                                        page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                            else:
                                page_index += 1
                                page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                              page_index)
                                if page_count == 0:
                                    content = unescape(content)
                                    content = re.sub(r"<div\b[^>]*>(.*?)</div>", "", content,
                                                     flags=re.IGNORECASE | re.DOTALL)
                                    content = content.replace('\r\n', '\n').replace("<br/>",
                                                                                    "\n").replace(
                                        '<br />',
                                        "\n").replace(
                                        '\n\n\n', "\n").replace('\n\n', "\n").replace('\n', "\n　　").replace(r"　　\s+", "　　")
                                    p = re.compile('<[^>]+>')
                                    content = p.sub('', content)
                                    file_name = self.file_item_handler.write_content(content)
                                    path = None
                                    if file_name is not None:
                                        path = self.file_item_handler.upload(bucket.NOVEL, file_name, file_type.TEXT_PLAIN)
                                        time.sleep(1)
                                    print(path)
                                    if path is not None:
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                except Exception as e:
                    print(e)
            i += 1

    def novel_job(self):
        now = datetime.now().strftime("%Y-%m-%d")
        i = 0
        while True:
            xiao_shuo_url = self.domain_v3 + '/novel/recentUpdate/' + str(i) + '.json?channel=android&timestamp=' + str(
                int(time.time()))
            print(xiao_shuo_url)
            xiao_shuo_response = requests.get(xiao_shuo_url)
            xiao_shuo_response_text = xiao_shuo_response.text
            result = json.loads(xiao_shuo_response_text)
            if len(result) == 0:
                print('xiao shuo is empty.')
                break
            print(result)
            for novel_detail in result:
                try:
                    print(novel_detail)
                    last_update_time = novel_detail['last_update_time']
                    date = datetime.fromtimestamp(last_update_time).strftime('%Y-%m-%d')
                    if now != date:
                        print('novel date : ', date)
                        return
                    title = novel_detail['name']
                    novel_id = self.novel_db.get_novel_id(title)
                    last_update_chapter_name = novel_detail['last_update_chapter_name']
                    if len(last_update_chapter_name) == 0:
                        continue
                    count = self.novel_chapter_db.count(novel_id, last_update_chapter_name)
                    if count != 0:
                        print('comic title : ', title, ', last update chapter name : ', last_update_chapter_name)
                        return
                    novel_id = novel_detail['id']
                    novel_detail_url = self.domain_v4 + '/novel/detail/' + str(
                        novel_id) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    novel_detail_response = requests.get(novel_detail_url)
                    novel_detail_response_text = novel_detail_response.text
                    novel_detail_response = dongmanzhijia_novel_pb2.NovelDetailResponseProto()
                    novel_detail_response.ParseFromString(
                        rsa_decrypt(novel_detail_response_text, PRIVATE_KEY))
                    print(novel_detail_response)
                    if novel_detail_response.errno != 0:
                        continue
                    novel_detail = novel_detail_response.data
                    print(novel_detail)
                    cover = novel_detail.cover
                    title = novel_detail.name
                    region = novel_detail.zone
                    self.region_db.save(region)
                    region_id = self.region_db.get_region_id(region)
                    novel_id = self.novel_db.get_novel_id(title)
                    if novel_id is None:
                        file_name = self.file_item_handler.download(cover)
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    authors = novel_detail.authors
                    author_str = ''
                    author_id_str = ''
                    if len(authors) != 0:
                        author_ids = []
                        index = 0
                        for author in str(authors).split('/'):
                            author = author.replace('\'', '\\\'')
                            self.author_db.save(author)
                            author_id = self.author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if index != len(authors) - 1:
                                author_str += ','
                            index += 1
                        if author_str.endswith(','):
                            author_str = author_str[:-1]
                        author_id_str = ','.join(author_ids)
                    categories = novel_detail.types
                    category_str = ''
                    category_id_str = ''
                    if len(categories) != 0:
                        category_ids = []
                        index = 0
                        for category in str(categories).split('/'):
                            category = category.replace('\'', '').replace('[', '').replace(']', '')
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                    description = novel_detail.introduction
                    status = novel_detail.status
                    flag = 0
                    if status == '连载中':
                        flag = 1
                    self.novel_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, region_id, region)
                    novel_id = self.novel_db.get_novel_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 2, title, cover, novel_id, category_id_str, author_id_str)
                    novel_chapter_url = self.domain_v4 + '/novel/chapter/' + str(
                        novel_detail.novelId) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    print(novel_chapter_url)
                    novel_chapter_response = requests.get(novel_chapter_url)
                    novel_chapter_response_text = novel_chapter_response.text
                    novel_chapter_response = dongmanzhijia_novel_pb2.NovelChapterResponseProto()
                    novel_chapter_response.ParseFromString(
                        rsa_decrypt(novel_chapter_response_text, PRIVATE_KEY))
                    print(novel_chapter_response)
                    if novel_chapter_response.errno != 0:
                        continue
                    volumes = novel_chapter_response.data
                    volume_index = 0
                    for volume in volumes:
                        volume_index += 1
                        volume_name = volume.volumeName
                        self.novel_volume_db.save(novel_id, volume_name, volume_index)
                        novel_volume_id = self.novel_volume_db.get_novel_volume_id(novel_id, volume_name)
                        chapters = volume.chapters
                        for chapter in chapters:
                            chapter_name = chapter.chapterName
                            seq_no = chapter.chapterOrder
                            count = self.novel_chapter_db.count_by_novel_volume_id(novel_id, novel_volume_id,
                                                                                   chapter_name)
                            self.novel_chapter_db.save_by_novel_volume_id(novel_id, novel_volume_id, chapter_name,
                                                                          seq_no)

                            novel_chapter_id = self.novel_chapter_db.get_novel_chapter_id_by_novel_volume_id(
                                novel_id,
                                novel_volume_id,
                                chapter_name)
                            if count == 0 and novel_chapter_id is not None:
                                self.asset_db.update(novel_id, 2, chapter_name, novel_chapter_id)
                                self.novel_db.upgrade(novel_id)
                            ts = str(int(time.time()))
                            path = '/lnovel/' + str(volume.volumeId) + '_' + str(chapter.chapterId) + '.txt'
                            key = 'IBAAKCAQEAsUAdKtXNt8cdrcTXLsaFKj9bSK1nEOAROGn2KJXlEVekcPssKUxSN8dsfba51kmHM'
                            key += path
                            key += ts
                            md5 = hashlib.md5()
                            md5.update(key.encode('utf8'))
                            key = md5.hexdigest().lower()
                            novel_chapter_url = self.domain_novel + path + '?t=' + ts + '&k=' + key
                            print(novel_chapter_url)
                            content_response = requests.get(novel_chapter_url)
                            content = content_response.text
                            if len(content) == 0:
                                continue
                            soup = bs4.BeautifulSoup(content, 'lxml')
                            img_tags = soup.find_all('img')
                            page_index = 0
                            if len(img_tags) != 0:
                                for img in img_tags:
                                    path = img.get('src')
                                    print(path)
                                    page_index += 1
                                    page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                                  page_index)
                                    if page_count == 0:
                                        file_name = self.file_item_handler.download(path, headers={
                                            'Referer': 'http://www.dmzj.com/',
                                        })
                                        if file_name is not None:
                                            path = self.file_item_handler.upload(bucket.INSET, file_name,
                                                                                 file_type.IMAGE_JPEG)
                                        print(path)
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path,
                                                                        page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                            else:
                                page_index += 1
                                page_count = self.novel_chapter_item_db.count(novel_chapter_id, novel_id,
                                                                              page_index)
                                if page_count == 0:
                                    content = unescape(content)
                                    content = re.sub(r"<div\b[^>]*>(.*?)</div>", "", content,
                                                     flags=re.IGNORECASE | re.DOTALL)
                                    content = content.replace('\r\n', '\n').replace("<br/>",
                                                                                    "\n").replace(
                                        '<br />',
                                        "\n").replace(
                                        '\n\n\n', "\n").replace('\n\n', "\n").replace('\n', "\n　　").replace(r"　　\s+", "　　")
                                    p = re.compile('<[^>]+>')
                                    content = p.sub('', content)
                                    file_name = self.file_item_handler.write_content(content)
                                    path = None
                                    if file_name is not None:
                                        path = self.file_item_handler.upload(bucket.NOVEL, file_name, file_type.TEXT_PLAIN)
                                        time.sleep(1)
                                    print(path)
                                    if path is not None:
                                        self.novel_chapter_item_db.save(novel_chapter_id, novel_id, path, page_index)
                                        self.novel_subscribe_db.upgrade(novel_id)
                except Exception as e:
                    print(e)
            i += 1


def rsa_decrypt(encrypted_text, key):
    rsa_key = private_key_from_string(key)
    cipher = PKCS1_v1_5.new(rsa_key)
    source_bytes = base64.b64decode(encrypted_text)
    input_length = len(source_bytes)
    k = rsa_key.size_in_bytes()
    output = bytes()
    input_offset = 0
    output_offset = 0
    while input_offset < input_length:
        chunk_size = k if (input_offset + k <= input_length) else input_length - input_offset
        b = source_bytes[input_offset:input_offset + chunk_size]
        o = cipher.decrypt(b, random_generator)
        output_offset += len(o)
        output += o
        input_offset += chunk_size
    result = (output if (len(output) == output_offset) else output[:output_offset])
    return result


def private_key_from_string(key):
    private_key_der = base64.b64decode(key)
    asn1_parser = core.Asn1Value.load(private_key_der)
    private_key = asn1_parser[2].native
    asn1_parser = keys.RSAPrivateKey.load(private_key)
    modulus = asn1_parser['modulus'].native
    public_exponent = asn1_parser['public_exponent'].native
    private_exponent = asn1_parser['private_exponent'].native
    p = asn1_parser['prime1'].native
    q = asn1_parser['prime2'].native
    return RSA.construct((modulus, public_exponent, private_exponent, p, q))
