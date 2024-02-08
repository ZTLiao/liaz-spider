from spiders.cartoonmad_spider import CartoonMadSpider


def execute():
    print('==== cartoon mad task start ====')
    try:
        CartoonMadSpider().parse()
    except Exception as e:
        print(e)
    print('==== cartoon mad task end ====')
