import system.global_vars


class FileItemDb:

    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def list(self, page_num: int, page_size: int):
        result = None
        cursor = self.conn.cursor()
        cursor.execute(
            'select path from file_item order by file_id limit ' + str((page_num - 1) * page_size) + ', ' + str(
                page_size))
        results = cursor.fetchall()
        if results is not None:
            fields = [field[0] for field in cursor.description]
            result = [dict(zip(fields, result)) for result in results]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, bucket_name, object_name, size, path, unique_id, suffix, file_type):
        cursor = self.conn.cursor()
        cursor.execute(
            'insert into file_item(bucket_name, object_name, size, path, unique_id, suffix, file_type, created_at, updated_at) values(\'' + bucket_name + '\', \'' + object_name + '\', \'' + str(
                size) + '\', \'' + path + '\', \'' + unique_id + '\', \'' + suffix + '\', \'' + file_type + '\', now(3), now(3))')
        self.conn.commit()
