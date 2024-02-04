import system.global_vars
import pymysql


class NovelChapterItemDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, novel_chapter_id, novel_id, seq_no):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter_item where novel_chapter_id = \'' + str(
                novel_chapter_id) + '\' and novel_id = \'' + str(novel_id) + '\' and seq_no = \'' + str(seq_no) + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, novel_chapter_id, novel_id, path, seq_no):
        if path is None:
            print('novel_chapter_id : ', novel_chapter_id, ', novel_id : ', novel_id, ', seq_no : ', seq_no)
            return
        count = self.count(novel_chapter_id, novel_id, seq_no)
        if count == 0:
            conn = pymysql.connect(
                host=self.__mysql.host,
                port=int(self.__mysql.port),
                user=self.__mysql.username,
                password=self.__mysql.password,
                db=self.__mysql.db,
                charset='utf8')
            cursor = conn.cursor()
            cursor.execute(
                'insert into novel_chapter_item(novel_chapter_id, novel_id, path, seq_no, created_at, updated_at) values(\'' + str(
                    novel_chapter_id) + '\', \'' + str(novel_id) + '\', \'' + path + '\', \'' + str(
                    seq_no) + '\', now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()
