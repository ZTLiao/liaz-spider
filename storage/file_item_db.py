import system.global_vars


class FileItemDb:

    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def list(self, page_num: int, page_size: int):
        result = None
        cursor = self.conn.cursor()
        cursor.execute('select path from file_item order by file_id limit ' + str((page_num - 1) * page_size) + ', ' + str(page_size))
        results = cursor.fetchall()
        if results is not None:
            fields = [field[0] for field in cursor.description]
            result = [dict(zip(fields, result)) for result in results]
        self.conn.commit()
        cursor.close()
        return result

