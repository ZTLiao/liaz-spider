import json
from datetime import datetime

import execjs
import requests
import zhconv
import system.global_vars

from config.redis_config import RedisConfig
from constants import bucket, file_type
from constants.redis_key import COMIC_DETAIL
from handler.file_item_handler import FileItemHandler
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.comic_volume_db import ComicVolumeDb
from storage.region_db import RegionDb
from utils.redis_util import RedisUtil


class CopyMangaSpider:
    def __init__(self):
        self.domain = 'https://www.mangacopy.com'
        self.category_db = CategoryDb()
        self.author_db = AuthorDb()
        self.region_db = RegionDb()
        self.comic_db = ComicDb()
        self.comic_volume_db = ComicVolumeDb()
        self.comic_chapter_db = ComicChapterDb()
        self.comic_chapter_item_db = ComicChapterItemDb()
        self.asset_db = AssetDb()
        self.comic_subscribe_db = ComicSubscribeDb()
        self.file_item_handler = FileItemHandler()
        redis: RedisConfig = system.global_vars.systemConfig.get_redis()
        self.redis_util = RedisUtil(redis.host, redis.port, redis.db, redis.password)

    def parse(self):
        try:
            now = datetime.now().strftime("%Y-%m-%d")
            index = 0
            while True:
                index += 1
                man_hua_url = self.domain + '/api/v3/comics'
                man_hua_response = requests.get(man_hua_url, headers={
                    'Referer': 'https://mangacopy.com/',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                                  'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }, params={
                    'free_type': 1,
                    'limit': 21,
                    'offset': (index - 1) * 21,
                    'type': '$$DEFAULT$$',
                    'ordering': '-datetime_updated',
                    '_update': 'true',
                })
                man_hua_response_text = man_hua_response.text
                print(man_hua_response_text)
                man_hua_response = json.loads(man_hua_response_text)
                if man_hua_response['code'] != 200:
                    print('man hua response is error.')
                    return
                results = man_hua_response['results']
                man_hua_list = results['list']
                for man_hua_item in man_hua_list:
                    path_word = man_hua_item['path_word']
                    date = man_hua_item['datetime_updated']
                    if now != date:
                        print('comic date : ', date)
                        return
                    detail_url = self.domain + '/api/v3/comic2/' + path_word
                    man_hua_detail_response = requests.get(detail_url, headers={
                        'Referer': self.domain,
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                      'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'webp': '1',
                        'region': '1',
                        'platform': '1',
                        'version': '2022.10.20',
                        'accept': 'application/json',
                        'content-encoding': 'gzip, compress, br',
                    }, data={
                        'platform': 1,
                    })
                    man_hua_detail_response_text = man_hua_detail_response.text
                    man_hua_detail_response = json.loads(man_hua_detail_response_text)
                    if man_hua_detail_response['code'] != 200:
                        print('man hua detail response is error.')
                        return
                    man_hua_detail = man_hua_detail_response['results']['comic']
                    title = traditional_to_simplified(man_hua_detail['name'])
                    cover = man_hua_detail['cover']
                    print(cover)
                    comic_id = self.comic_db.get_comic_id(title)
                    if comic_id is None or comic_id == 0:
                        file_name = self.file_item_handler.download(cover, headers={
                            'Referer': self.domain,
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                          'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        })
                        if file_name is not None:
                            cover = self.file_item_handler.upload(bucket.COVER, file_name,
                                                                  file_type.IMAGE_JPEG)
                        print(cover)
                        if cover is None:
                            cover = ''
                    authors = man_hua_detail['author']
                    author_ids = []
                    author_str = ''
                    author_index = 0
                    for author_item in authors:
                        author = traditional_to_simplified(author_item['name'])
                        author = author.replace('\'', '\\\'')
                        self.author_db.save(author)
                        author_id = self.author_db.get_author_id(author)
                        author_ids.append(str(author_id))
                        author_str += author
                        if author_index != len(authors) - 1:
                            author_str += ','
                        author_index += 1
                    author_id_str = ','.join(author_ids)
                    categories = man_hua_detail['theme']
                    category_str = ''
                    category_id_str = ''
                    if len(categories) != 0:
                        category_ids = []
                        index = 0
                        for category_item in categories:
                            category = traditional_to_simplified(category_item['name'])
                            category = category.replace('\'', '\\\'')
                            self.category_db.save(category)
                            category_id = self.category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                    region = traditional_to_simplified(man_hua_detail['region']['display'])
                    self.region_db.save(region)
                    region_id = self.region_db.get_region_id(region)
                    description = traditional_to_simplified(man_hua_detail['brief'])
                    status = man_hua_detail['status']['display']
                    flag = 0
                    if status == '連載中':
                        flag = 1
                    self.comic_db.save(title, cover, description, flag, category_id_str, category_str,
                                       author_id_str,
                                       author_str, region_id, region)
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    volume_chapter_url = self.domain + '/comicdetail/' + path_word + '/chapters'
                    print(volume_chapter_url)
                    man_hua_volume_chapter_response = requests.get(volume_chapter_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    })
                    man_hua_volume_chapter_response_text = man_hua_volume_chapter_response.text
                    man_hua_volume_chapter_response = json.loads(man_hua_volume_chapter_response_text)
                    if man_hua_volume_chapter_response['code'] != 200:
                        print('man hua volume chapter response is error.')
                        return
                    encrypt_chapters = man_hua_volume_chapter_response['results']
                    build_groups = aes_decrypt(encrypt_chapters)
                    print(build_groups)
                    build_groups = json.loads(build_groups)
                    chapters = []
                    groups = build_groups['groups']
                    for key in groups:
                        chapters += groups[key]['chapters']
                    volumes = build_groups['build']['type']
                    volume_index = 0
                    for volume in volumes:
                        volume_index += 1
                        type_id = volume['id']
                        volume_name = volume['name']
                        volume_chapters = [chapter for chapter in chapters if chapter['type'] == type_id]
                        if len(volume_chapters) == 0:
                            print('volume name is empty.')
                            continue
                        self.comic_volume_db.save(comic_id, volume_name, volume_index)
                        comic_volume_id = self.comic_volume_db.get_comic_volume_id(comic_id, volume_name)
                        chapter_index = self.comic_chapter_db.get_seq_no_by_comic_volume_id(comic_id, comic_volume_id)
                        is_comic_chapter_exists = False
                        for chapter in volume_chapters:
                            chapter_index += 1
                            chapter_name = chapter['name']
                            count = self.comic_chapter_db.count_by_comic_volume_id(comic_id, comic_volume_id,
                                                                                   chapter_name)
                            if count == 0:
                                self.comic_chapter_db.save_by_comic_volume_id(comic_id, comic_volume_id,
                                                                              chapter_name,
                                                                              chapter_index)
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
                            chapter_url = self.domain + '/api/v3/comic/' + path_word + '/chapter2/' + chapter['id']
                            print(chapter_url)
                            man_hua_chapter_response = requests.get(chapter_url, headers={
                                'method': 'GET',
                                'path': '/api/v3/comic/' + path_word + '/chapter2/' + chapter[
                                    'id'] + '?platform=3&_update=true',
                                'authority': self.domain.replace('https://', ''),
                                'Referer': self.domain,
                                'User-Agent': 'Kotlin/1.9.10 (kotlin:io)',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                'webp': '0',
                                'region': '0',
                                'platform': '1',
                                'version': '2022.10.20',
                                'accept': 'application/json',
                                'content-encoding': 'gzip, compress, br',
                                'Authorization': 'Token '
                            }, params={
                                'platform': 3,
                                '_update': 'true',
                            })
                            man_hua_chapter_response = man_hua_chapter_response.json()
                            print(man_hua_chapter_response)
                            if man_hua_chapter_response['code'] != 200:
                                print('man hua chapter response is error.')
                                return
                            contents = man_hua_chapter_response['results']['chapter']['contents']
                            print(contents)
                            page_index = 0
                            for content in contents:
                                page_index += 1
                                path = content['url']
                                page_count = self.comic_chapter_item_db.count(comic_chapter_id, comic_id,
                                                                              page_index)
                                if page_count == 0:
                                    print(path)
                                    file_name = self.file_item_handler.download(path, headers={
                                        'Referer': self.domain,
                                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                                      'KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                                        'Accept-Encoding': 'gzip, deflate, br',
                                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
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
                    self.redis_util.delete(COMIC_DETAIL + str(comic_id))
        except Exception as e:
            print(e)


def aes_decrypt(content_key: str):
    ctx = execjs.compile("""
    function AESDecrypt(contentKey) {
        const CryptoJS = require("crypto-js");
        const a = contentKey.substring(0x0, 0x10);
        const b = contentKey.substring(0x10, contentKey.length);
        const c = CryptoJS.enc.Utf8.parse('xxxmanga.woo.key');
        const d = CryptoJS.enc.Utf8.parse(a);
        const e = CryptoJS.enc.Hex.parse(b);
        const f = CryptoJS.enc.Base64.stringify(e);
        return CryptoJS.AES.decrypt(f, c, {
            iv: d,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7,
        }).toString(CryptoJS.enc.Utf8).toString();
    }
    """)
    return ctx.call('AESDecrypt', content_key)


def traditional_to_simplified(text):
    # 调用convert函数将繁体字转换为简体字
    simplified_text = zhconv.convert(text, 'zh-hans')
    return simplified_text
