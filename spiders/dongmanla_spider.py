import bs4
import requests

from storage.category_db import CategoryDb


class DongManLaSpider:
    def __init__(self):
        self.domain = 'https://www.dongman.la'

    def parse(self):
        i = 277
        is_end = False
        while True:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            url = self.domain + '/manhua/serial/' + str(i) + '.html'
            print(url)
            response = requests.get(url)
            response_text = response.text
            print(response_text)
            soup = bs4.BeautifulSoup(response_text, 'lxml')
            category_db = CategoryDb()
            for man_han in soup.select('div.cy_list_mh'):
                print(len(man_han.text.strip()))
                if len(man_han.text.strip()) == 0:
                    is_end = True
                    break
                for ul_item in man_han.find_all('ul'):
                    categories_item = ul_item.select('li.biaoqian')[0]
                    categories = categories_item.text.split('：')[1]
                    for category_name in categories.split(','):
                        pass

