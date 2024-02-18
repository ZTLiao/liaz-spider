from spiders.copymanga_spider import CopyMangaSpider


def execute():
    print('==== copy manga task start ====')
    try:
        CopyMangaSpider().parse()
    except Exception as e:
        print(e)
    print('==== copy manga task end ====')
