import system.global_vars


class NovelSubscribeDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def upgrade(self, novel_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'update novel_subscribe set is_upgrade = 1, updated_at = now(3) where novel_id = \'' + str(novel_id) + '\'')
        self.conn.commit()