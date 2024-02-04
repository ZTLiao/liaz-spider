import system.global_vars
import pymysql


class NovelChapterDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, novel_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, novel_id, chapter_name, seq_no):
        count = self.count(novel_id, chapter_name)
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
                'insert into novel_chapter(novel_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    novel_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(seq_no) + '\', 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_novel_chapter_id(self, novel_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select novel_chapter_id from novel_chapter where novel_id = \'' + str(
            novel_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def get_seq_no(self, novel_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select seq_no from novel_chapter where novel_id = \'' + str(novel_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def count_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and novel_volume_id = \'' + str(
                novel_volume_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name, seq_no):
        count = self.count_by_novel_volume_id(novel_id, novel_volume_id, chapter_name)
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
                'insert into novel_chapter(novel_id, novel_volume_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    novel_id) + '\', \'' + str(
                    novel_volume_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(
                    seq_no) + '\', 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_novel_chapter_id_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select novel_chapter_id from novel_chapter where novel_id = \'' + str(
            novel_id) + '\' and novel_volume_id = \'' + str(
            novel_volume_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def get_seq_no_by_novel_volume_id(self, novel_id, novel_volume_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select seq_no from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and novel_volume_id = \'' + str(
                novel_volume_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result
