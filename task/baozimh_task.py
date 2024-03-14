from spiders.cn_baozimh_spider import CnBaoZiMhSpider


def execute():
    print('==== bao zi mh task start ====')
    try:
        CnBaoZiMhSpider().parse()
    except Exception as e:
        print(e)
    print('==== bao zi mh task end ====')
