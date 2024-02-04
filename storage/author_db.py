import system.global_vars


class AuthorDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, author_name):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from author where author_name = \'' + author_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def save(self, author_name):
        count = self.count(author_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into author(author_name, seq_no, status, created_at, updated_at) values(\'' + author_name + '\', 0, 1, now(3), now(3))')
            self.conn.commit()

    def get_author_id(self, author_name):
        cursor = self.conn.cursor()
        cursor.execute('select author_id from author where author_name = \'' + author_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result
