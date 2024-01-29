from spiders.dongmanla_spider import DongManLaSpider


def execute():
    print('==== dong man la task start ====')
    DongManLaSpider().job()
    print('==== dong man la task end ====')
