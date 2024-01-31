import time
from datetime import datetime

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from asn1crypto import keys, core

import base64

import requests

from constants import bucket, file_type
from handler.file_item_handler import FileItemHandler
from interfaces import comic_pb2
from storage.asset_db import AssetDb
from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_chapter_item_db import ComicChapterItemDb
from storage.comic_db import ComicDb
from storage.comic_subscribe_db import ComicSubscribeDb
from storage.region_db import RegionDb

random_generator = Random.new().read

PRIVATE_KEY = 'MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAK8nNR1lTnIfIes6oRWJNj3mB6OssDGx0uGMpgpbVCpf6+VwnuI2stmhZNoQcM417Iz7WqlPzbUmu9R4dEKmLGEEqOhOdVaeh9Xk2IPPjqIu5TbkLZRxkY3dJM1htbz57d/roesJLkZXqssfG5EJauNc+RcABTfLb4IiFjSMlTsnAgMBAAECgYEAiz/pi2hKOJKlvcTL4jpHJGjn8+lL3wZX+LeAHkXDoTjHa47g0knYYQteCbv+YwMeAGupBWiLy5RyyhXFoGNKbbnvftMYK56hH+iqxjtDLnjSDKWnhcB7089sNKaEM9Ilil6uxWMrMMBH9v2PLdYsqMBHqPutKu/SigeGPeiB7VECQQDizVlNv67go99QAIv2n/ga4e0wLizVuaNBXE88AdOnaZ0LOTeniVEqvPtgUk63zbjl0P/pzQzyjitwe6HoCAIpAkEAxbOtnCm1uKEp5HsNaXEJTwE7WQf7PrLD4+BpGtNKkgja6f6F4ld4QZ2TQ6qvsCizSGJrjOpNdjVGJ7bgYMcczwJBALvJWPLmDi7ToFfGTB0EsNHZVKE66kZ/8Stx+ezueke4S556XplqOflQBjbnj2PigwBN/0afT+QZUOBOjWzoDJkCQClzo+oDQMvGVs9GEajS/32mJ3hiWQZrWvEzgzYRqSf3XVcEe7PaXSd8z3y3lACeeACsShqQoc8wGlaHXIJOHTcCQQCZw5127ZGs8ZDTSrogrH73Kw/HvX55wGAeirKYcv28eauveCG7iyFR0PFB/P/EDZnyb+ifvyEFlucPUI0+Y87F'


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
        self.uid = 100091600

    def comic_job(self):
        now = datetime.now().strftime("%Y-%m-%d")
        i = 0
        is_end = False
        while True:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            man_hua_url = self.domain + '/comic/update/list/100/' + str(i) + '?channel=android&timestamp=' + str(
                int(time.time())) + '&uid=' + str(self.uid)
            print(man_hua_url)
            man_hua_response = requests.get(man_hua_url)
            man_hua_response_text = man_hua_response.text
            comic_update_list_response = comic_pb2.ComicUpdateListResponseProto()
            comic_update_list_response.ParseFromString(rsa_decrypt(man_hua_response_text, PRIVATE_KEY))
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
                comic_id = value.comicId
                try:
                    comic_detail_url = self.domain + '/comic/detail/' + str(
                        comic_id) + '?channel=android&timestamp=' + str(
                        int(time.time())) + '&uid=' + str(self.uid)
                    print(comic_detail_url)
                    comic_detail_response = requests.get(comic_detail_url)
                    comic_detail_response_text = comic_detail_response.text
                    comic_detail_response = comic_pb2.ComicDetailResponseProto()
                    comic_detail_response.ParseFromString(rsa_decrypt(comic_detail_response_text, PRIVATE_KEY))
                    comic_detail = comic_detail_response.data
                    print(comic_detail)
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
                    self.comic_db.save(title, cover, description, 1, category_id_str, category_str,
                                       author_id_str,
                                       author_str, 0, '')
                    comic_id = self.comic_db.get_comic_id(title)
                    asset_key = title + '|' + author_str
                    self.asset_db.save(asset_key, 1, title, cover, comic_id, category_id_str, author_id_str)
                    chapter_index = self.comic_chapter_db.get_seq_no(comic_id)
                except Exception as e:
                    print(e)


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
