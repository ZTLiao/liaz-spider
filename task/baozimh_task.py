from spiders.baozimh_spider import BaoZiMhSpider


def execute():
    print('==== cartoon mad task start ====')
    try:
        BaoZiMhSpider().parse()
    except Exception as e:
        print(e)
    print('==== cartoon mad task end ====')
