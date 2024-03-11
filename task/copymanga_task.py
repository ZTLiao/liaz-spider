from spiders.copymanga_spider import CopyMangaSpider


def execute():
    print('==== copy manga task start ====')
    try:
        CopyMangaSpider().job()
    except Exception as e:
        print(e)
    print('==== copy manga task end ====')


def upgrade_job():
    print('==== copy manga upgrade job task start ====')
    try:
        CopyMangaSpider().upgrade_job()
    except Exception as e:
        print(e)
    print('==== copy manga upgrade job task end ====')
