import system.global_vars
import pymysql


class RegionDb:
    def __init__(self):
        self.__mysql = system.global_vars.application.get_mysql()

    def count(self, region_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select count(1) from region where region_name = \'' + region_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result

    def save(self, region_name):
        count = self.count(region_name)
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
                'insert into region(region_name, seq_no, status, created_at, updated_at) values(\'' + region_name + '\', 0, 1, now(3), now(3))')
            conn.commit()
            cursor.close()
            conn.close()

    def get_region_id(self, region_name):
        conn = pymysql.connect(
            host=self.__mysql.host,
            port=int(self.__mysql.port),
            user=self.__mysql.username,
            password=self.__mysql.password,
            db=self.__mysql.db,
            charset='utf8')
        cursor = conn.cursor()
        cursor.execute('select region_id from region where region_name = \'' + region_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is None:
            result = 0
        return result
