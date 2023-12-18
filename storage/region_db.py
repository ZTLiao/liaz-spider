import system.global_vars


class RegionDb:
    def __init__(self):
        self.conn = system.global_vars.application.get_mysql()

    def count(self, region_name):
        cursor = self.conn.cursor()
        cursor.execute('select count(1) from region where region_name = \'' + region_name + '\'')
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result
