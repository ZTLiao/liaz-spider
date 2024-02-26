import system.global_vars
import pymysql


class ComicChapterItemDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, comic_chapter_id, comic_id, seq_no):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select count(1) from comic_chapter_item where comic_chapter_id = \'' + str(
                comic_chapter_id) + '\' and comic_id = \'' + str(comic_id) + '\' and seq_no = \'' + str(seq_no) + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, comic_chapter_id, comic_id, path, seq_no):
        if path is None:
            print('comic_chapter_id : ', comic_chapter_id, ', comic_id : ', comic_id, ', seq_no : ', seq_no)
            return
        count = self.count(comic_chapter_id, comic_id, seq_no)
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
                'insert into comic_chapter_item(comic_chapter_id, comic_id, path, seq_no, created_at, updated_at) values(\'' + str(
                    comic_chapter_id) + '\', \'' + str(comic_id) + '\', \'' + path + '\', \'' + str(
                    seq_no) + '\', now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_chapter_seq_nos(self, comic_chapter_id, comic_id):
        result = None
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select seq_no from comic_chapter_item where comic_chapter_id = \'' + str(
            comic_chapter_id) + '\' and comic_id = \'' + str(comic_id) + '\' order by comic_chapter_item_id')
        results = cursor.fetchall()
        if results is not None:
            result = [result[0] for result in results]
        conn.commit()
        cursor.close()
        conn.close()
        return result

    def get_comic_chapter_item_ids(self, comic_chapter_id, comic_id):
        result = None
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select comic_chapter_item_id from comic_chapter_item where comic_chapter_id = \'' + str(
            comic_chapter_id) + '\' and comic_id = \'' + str(comic_id) + '\' order by comic_chapter_item_id')
        results = cursor.fetchall()
        if results is not None:
            result = [result[0] for result in results]
        conn.commit()
        cursor.close()
        conn.close()
        return result

    def update_seq_no(self, comic_chapter_item_id, seq_no):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'update comic_chapter_item set updated_at = now(3), seq_no = \'' + str(
                seq_no) + '\' where comic_chapter_item_id = \'' + str(comic_chapter_item_id) + '\'')
        conn.commit()
        cursor.close()
        conn.close()
