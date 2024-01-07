import system.global_vars


class ComicSubscribeDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def upgrade(self, comic_id):
        cursor = self.conn.cursor()
        cursor.execute('update comic_subscribe set is_upgrade = 1, updated_at = now(3) where comic_id = \'' + str(comic_id) + '\'')
        self.conn.commit()
