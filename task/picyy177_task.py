from spiders.picyy177_spider import PicYY177Spider


def execute():
    print('==== 177picyy comic task start ====')
    try:
        PicYY177Spider().parse()
    except Exception as e:
        print(e)
    print('==== 177picyy comic task end ====')
