import system.global_vars
import pymysql


class ComicDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, title):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select count(1) from comic where title = \'' + title + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, title, cover, description, flag, category_ids, categories, author_ids,
             authors, region_id, region):
        count = self.count(title)
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
                'insert into comic(title, cover, description, first_letter, direction, flag, category_ids, categories, author_ids, authors, region_id, region, chapter_num, start_time, end_time, subscribe_num, hit_num, status, created_at, updated_at) values(\'' + title + '\', \'' + cover + '\', \'' + description + '\', \'\', 0, \'' + str(
                    flag) + '\', \'' + category_ids + '\', \'' + categories + '\', \'' + author_ids + '\', \'' + authors + '\', \'' + str(
                    region_id) + '\', \'' + region + '\', 0, now(3), now(3), 0, 0, 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_comic_id(self, title):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select comic_id from comic where title = \'' + title + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def upgrade(self, comic_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'update comic set end_time = now(3) where comic_id = \'' + str(comic_id) + '\'')
        conn.commit()
        cursor.close()
        conn.close()
