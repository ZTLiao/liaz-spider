import pymysql

import system.global_vars


class CategoryDb:
    def __init__(self):
        mysql_config = system.global_vars.systemConfig.get_mysql()
        self.conn = pymysql.connect(
            host=mysql_config.host,
            port=int(mysql_config.port),
            user=mysql_config.username,
            password=mysql_config.password,
            db=mysql_config.db,
            charset='utf8')

    def count(self, category_name):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from category where category_name = \'' + category_name + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, category_name):
        count = self.count(category_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into category(category_code, category_name, seq_no, status, created_at, updated_at) values(\'' + category_name + '\', \'' + category_name + '\', 0, 1, now(3), now(3))')
            self.conn.commit()

    def close(self):
        self.conn.close()
