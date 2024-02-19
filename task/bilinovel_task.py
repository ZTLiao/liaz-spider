from spiders.bilinovel_spider import BiliNovelSpider


def execute():
    print('==== bili novel task start ====')
    try:
        BiliNovelSpider().parse()
    except Exception as e:
        print(e)
    print('==== bili novel task end ====')
