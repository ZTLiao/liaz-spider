import system.global_vars
import pymysql


class NovelSubscribeDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def upgrade(self, novel_id):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            'update novel_subscribe set is_upgrade = 1, updated_at = now(3) where novel_id = \'' + str(novel_id) + '\'')
        conn.commit()
        cursor.close()
        conn.close()
