import system.global_vars


class NovelVolumeDb:

    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, novel_id, volume_name):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from novel_volume where novel_id = \'' + str(
            novel_id) + '\' and volume_name = \'' + volume_name + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def save(self, novel_id, volume_name, seq_no):
        count = self.count(novel_id, volume_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel_volume(novel_id, volume_name, seq_no, status, created_at, updated_at) values(\'' + str(
                    novel_id) + '\', \'' + volume_name + '\', \'' + str(seq_no) + '\', 1, now(3), now(3))')
            self.conn.commit()

    def get_novel_volume_id(self, novel_id, volume_name):
        cursor = self.conn.cursor()
        cursor.execute('select novel_volume_id from novel_volume where novel_id = \'' + str(
            novel_id) + '\' and volume_name = \'' + volume_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        return result
