from spiders.fanqie_spider import FanQieSpider


def execute():
    print('==== fan qie novel task start ====')
    try:
        FanQieSpider().job()
    except Exception as e:
        print(e)
    print('==== fan qie novel task end ====')
