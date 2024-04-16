from spiders.acgnbus_spider import AcgNBusSpider


def execute():
    print('==== acgnbus comic task start ====')
    try:
        AcgNBusSpider().job()
    except Exception as e:
        print(e)
    print('==== acgnbus comic task end ====')
