from spiders.dongmanzhijia_spider import DongManZhiJiaSpider


def execute_comic():
    print('==== dong man zhi jia comic task start ====')
    DongManZhiJiaSpider().comic_job()
    print('==== dong man zhi jia comic task end ====')


def execute_novel():
    print('==== dong man zhi jia novel task start ====')
    DongManZhiJiaSpider().novel_job()
    print('==== dong man zhi jia novel task end ====')
