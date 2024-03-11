from spiders.manhuadb_spider import ManHuaDbSpider


def execute():
    print('==== manhuadb comic task start ====')
    try:
        ManHuaDbSpider().parse()
    except Exception as e:
        print(e)
    print('==== manhuadb comic task end ====')
