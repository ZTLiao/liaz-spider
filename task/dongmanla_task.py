from spiders.dongmanla_spider import DongManLaSpider
import schedule


class DongManLaTask:
    def __init__(self):
        self.__dongManLaSpider = DongManLaSpider()
        schedule.every().day.at('20:00').do(self.execute)

    def execute(self):
        print('==== dong man la task start ====')
        self.__dongManLaSpider.job()
        print('==== dong man la task end ====')
