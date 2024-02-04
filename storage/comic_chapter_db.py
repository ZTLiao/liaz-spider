import system.global_vars
import pymysql


class ComicChapterDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, comic_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from comic_chapter where comic_id = \'' + str(
                comic_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, comic_id, chapter_name, seq_no):
        count = self.count(comic_id, chapter_name)
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
                'insert into comic_chapter(comic_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    comic_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(seq_no) + '\', 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_comic_chapter_id(self, comic_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select comic_chapter_id from comic_chapter where comic_id = \'' + str(
            comic_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def get_comic_chapter_id_by_comic_volume_id(self, comic_id, comic_volume_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select comic_chapter_id from comic_chapter where comic_id = \'' + str(
            comic_id) + '\' and comic_volume_id = \'' + str(
            comic_volume_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def get_seq_no(self, comic_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select seq_no from comic_chapter where comic_id = \'' + str(comic_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save_by_comic_volume_id(self, comic_id, comic_volume_id, chapter_name, seq_no):
        count = self.count_by_comic_volume_id(comic_id, comic_volume_id, chapter_name)
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
                'insert into comic_chapter(comic_id, comic_volume_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    comic_id) + '\', \'' + str(comic_volume_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(
                    seq_no) + '\', 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def count_by_comic_volume_id(self, comic_id, comic_volume_id, chapter_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from comic_chapter where comic_id = \'' + str(
                comic_id) + '\' and comic_volume_id = \'' + str(
                comic_volume_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def get_seq_no_by_comic_volume_id(self, comic_id, comic_volume_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select seq_no from comic_chapter where comic_id = \'' + str(
                comic_id) + '\' and comic_volume_id = \'' + str(comic_volume_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result
