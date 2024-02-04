import system.global_vars


class NovelChapterDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, novel_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def save(self, novel_id, chapter_name, seq_no):
        count = self.count(novel_id, chapter_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel_chapter(novel_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    novel_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(seq_no) + '\', 1, now(3), now(3))')
            self.conn.commit()

    def get_novel_chapter_id(self, novel_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute('select novel_chapter_id from novel_chapter where novel_id = \'' + str(
            novel_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def get_seq_no(self, novel_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'select seq_no from novel_chapter where novel_id = \'' + str(novel_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def count_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'select count(1) from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and novel_volume_id = \'' + str(
                novel_volume_id) + '\' and chapter_name = \'' + chapter_name + '\'')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def save_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name, seq_no):
        count = self.count_by_novel_volume_id(novel_id, novel_volume_id, chapter_name)
        if count == 0:
            cursor = self.conn.cursor()
            cursor.execute(
                'insert into novel_chapter(novel_id, novel_volume_id, chapter_name, chapter_type, page_num, seq_no, status, created_at, updated_at) values(\'' + str(
                    novel_id) + '\', \'' + str(
                    novel_volume_id) + '\', \'' + chapter_name + '\', 0, 0, \'' + str(
                    seq_no) + '\', 1, now(3), now(3))')
            self.conn.commit()

    def get_novel_chapter_id_by_novel_volume_id(self, novel_id, novel_volume_id, chapter_name):
        cursor = self.conn.cursor()
        cursor.execute('select novel_chapter_id from novel_chapter where novel_id = \'' + str(
            novel_id) + '\' and novel_volume_id = \'' + str(
            novel_volume_id) + '\' and chapter_name = \'' + chapter_name + '\' limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result

    def get_seq_no_by_novel_volume_id(self, novel_id, novel_volume_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'select seq_no from novel_chapter where novel_id = \'' + str(
                novel_id) + '\' and novel_volume_id = \'' + str(
                novel_volume_id) + '\' order by seq_no desc limit 1')
        result = cursor.fetchone()
        if result is not None:
            result = result[0]
        self.conn.commit()
        cursor.close()
        if result is None:
            result = 0
        return result
