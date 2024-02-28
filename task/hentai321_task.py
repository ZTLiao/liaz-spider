from spiders.hentai321_spider import HenTai321Spider


def execute():
    print('==== hentai321 comic task start ====')
    try:
        HenTai321Spider().job()
    except Exception as e:
        print(e)
    print('==== fhentai321 comic task end ====')
