from spiders.baozimh_spider import BaoZiMhSpider


def execute():
    print('==== bao zi mh task start ====')
    try:
        BaoZiMhSpider().parse()
    except Exception as e:
        print(e)
    print('==== bao zi mh task end ====')
