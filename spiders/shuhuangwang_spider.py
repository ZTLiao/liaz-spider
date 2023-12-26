import bs4
import requests


class ShuHuangWangSpider:
    def __init__(self):
        self.domain = 'https://www.fanghuoni.net'
        self.resource_url = 'http://8.134.215.58'
        self.username = 'liaozetao'
        self.password = 'e10adc3949ba59abbe56e057f20f883e'

    def parse(self):
        i = 0
        is_end = False
        while i == 0:
            if is_end:
                print('man hua is empty.')
                break
            i += 1
            serial_url = self.domain + '/sort_0_0_0_P.html?page=' + str(i)
            print(serial_url)
            serial_response = requests.get(serial_url)
            serial_response_text = serial_response.text
            serial_soup = bs4.BeautifulSoup(serial_response_text, 'lxml')
            for news_content_item in serial_soup.select('div#newscontent'):
                a_items = news_content_item.select('.l li .s2 a')
                for a_item in a_items:
                    detail_url = self.domain + a_item.get('href')
                    print(detail_url)
                    detail_response = requests.get(detail_url)
                    detail_response_text = detail_response.text
                    detail_soup = bs4.BeautifulSoup(detail_response_text, 'lxml')
