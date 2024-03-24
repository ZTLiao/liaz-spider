import system.global_vars
import pymysql


class ComicSubscribeDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

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
            'update comic_subscribe set is_upgrade = 1, updated_at = now(3) where comic_id = \'' + str(comic_id) + '\'')
        conn.commit()
        cursor.close()
        conn.close()

    def get_subscribe_page(self, page_num: int, page_size: int):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'select distinct c.title as title from comic_subscribe as cs left join comic as c on c.comic_id = '
            ' cs.comic_id '
            ' where (flag & 1) != 0 order by cs.comic_subscribe_id limit ' + str(
                (page_num - 1) * page_size) + ', ' + str(page_size))
        results = cursor.fetchall()
        fields = [field[0] for field in cursor.description]
        result = [dict(zip(fields, result)) for result in results]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = []
        return result
