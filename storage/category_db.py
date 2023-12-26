import system.global_vars


class CategoryDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

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

    def get_category_id(self, category_name):
        cursor = self.conn.cursor()
        cursor.execute('select category_id from category where category_name = \'' + category_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        return result
