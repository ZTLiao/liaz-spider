import system.global_vars
import pymysql


class ComicVolumeDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, comic_id, volume_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select count(1) from comic_volume where comic_id = \'' + str(
            comic_id) + '\' and volume_name = \'' + volume_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, comic_id, volume_name, seq_no):
        count = self.count(comic_id, volume_name)
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
                'insert into comic_volume(comic_id, volume_name, seq_no, status, created_at, updated_at) values(\'' + str(
                    comic_id) + '\', \'' + volume_name + '\', \'' + str(seq_no) + '\', 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_comic_volume_id(self, comic_id, volume_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select comic_volume_id from comic_volume where comic_id = \'' + str(
            comic_id) + '\' and volume_name = \'' + volume_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result
