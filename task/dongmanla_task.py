from spiders.dongmanla_spider import DongManLaSpider


def execute():
    print('==== dong man la task start ====')
    try:
        DongManLaSpider().job()
    except Exception as e:
        print(e)
    print('==== dong man la task end ====')
