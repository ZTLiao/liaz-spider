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
        cursor.execute('update comic_subscribe set is_upgrade = 1, updated_at = now(3) where comic_id = \'' + str(comic_id) + '\'')
        conn.commit()
        cursor.close()
        conn.close()
