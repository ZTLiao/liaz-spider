import bs4
import requests

from storage.author_db import AuthorDb
from storage.category_db import CategoryDb
from storage.comic_chapter_db import ComicChapterDb
from storage.comic_db import ComicDb


class DongManLaSpider:
    def __init__(self):
        self.domain = 'https://www.dongman.la'

    def parse(self):
        i = 0
        is_end = False
        while i == 0:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            serial_url = self.domain + '/manhua/serial/' + str(i) + '.html'
            print(serial_url)
            serial_response = requests.get(serial_url)
            serial_response_text = serial_response.text
            serial_soup = bs4.BeautifulSoup(serial_response_text, 'lxml')
            category_db = CategoryDb()
            author_db = AuthorDb()
            comic_db = ComicDb()
            comic_chapter_db = ComicChapterDb()
            for man_han_item in serial_soup.select('div.cy_list_mh'):
                if len(man_han_item.text.strip()) == 0:
                    is_end = True
                    break
                for ul_item in man_han_item.find_all('ul'):
                    a_item = ul_item.select('a.pic')[0]
                    detail_url = self.domain + a_item.get('href')
                    detail_response = requests.get(detail_url)
                    detail_response_text = detail_response.text
                    detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
                    for man_hua_info_item in detail_soup.select('div.cy_main .cy_info .cy_intro_l'):
                        title = man_hua_info_item.select('.cy_title .detail-info-title')[0].text
                        region = man_hua_info_item.select('.cy_xinxi span')[0].text.split('：')[1]
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
                        index = 0
                        for author in authors:
                            author = author.replace('\'', '\\\'')
                            author_db.save(author)
                            author_id = author_db.get_author_id(author)
                            author_ids.append(str(author_id))
                            author_str += author
                            if index != len(authors) - 1:
                                author_str += ','
                            index += 1
                        author_id_str = ','.join(author_ids)
                        category_item = man_hua_info_item.select('.cy_xinxixi span')[1]
                        category_ids = []
                        categories = []
                        if len(category_item) == 1:
                            category = category_item.text.replace('类别：', '').replace('，', '').strip()
                            if len(category) > 0:
                                categories.append(category)
                        else:
                            for a_item in category_item.select('a'):
                                category = a_item.text.replace('类别：', '').replace('，', '').strip()
                                if len(category) > 0:
                                    categories.append(category)

                        category_str = ''
                        index = 0
                        for category in categories:
                            category = category.replace('\'', '\\\'')
                            category_db.save(category)
                            category_id = category_db.get_category_id(category)
                            category_ids.append(str(category_id))
                            category_str += category
                            if index != len(categories) - 1:
                                category_str += ','
                            index += 1
                        category_id_str = ','.join(category_ids)
                        description_item = man_hua_info_item.select('div.cy_xinxi p')[0]
                        description = description_item.text
                        li_items = detail_soup.select('div.cy_main .cy_zhangjie .cy_plist li')
                        if len(li_items) == 0:
                            print('zhang jie is empty.')
                        else:
                            comic_db.save(title, '', description, category_id_str, category_str, author_id_str, author_str, region)
                            comic_id = comic_db.get_comic_id(title)
                            index = 0
                            for li_item in reversed(li_items):
                                chapter_name = li_item.find('p').text
                                count = comic_chapter_db.count(comic_id, chapter_name)
                                if count == 0:
                                    index += 1
                                    comic_chapter_db.save(comic_id, chapter_name, index)
                                comic_chapter_id = comic_chapter_db.get_comic_chapter_id(comic_id, chapter_name)
                                print(comic_chapter_id)


