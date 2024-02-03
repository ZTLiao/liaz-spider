from spiders.dongmanzhijia_spider import DongManZhiJiaSpider


def execute_comic():
    print('==== dong man zhi jia comic task start ====')
    try:
        DongManZhiJiaSpider().comic_job()
    except Exception as e:
        print(e)
    print('==== dong man zhi jia comic task end ====')


def execute_novel():
    print('==== dong man zhi jia novel task start ====')
    try:
        DongManZhiJiaSpider().novel_job()
    except Exception as e:
        print(e)
    print('==== dong man zhi jia novel task end ====')
