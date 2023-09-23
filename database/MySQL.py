import mysql.connector


class MySQL:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()

    def add(self, nick: str, date_update: int):
        sql = 'INSERT INTO instagram_accounts(login, date_update) '
        'VALUES(%s, %s)'
        val = (nick, date_update)

        self.cursor.execute(sql, val)
        self.db.commit()

    def update(self, nick: str, date_update: int):
        sql = 'UPDATE instagram_accounts SET date_update = %s WHERE login = %s'
        val = (date_update, nick)

        self.cursor.execute(sql, val)
        self.db.commit()

    def existence(self, nick: str) -> bool:
        sql = 'SELECT login FROM instagram_accounts WHERE login = %s'
        val = (nick,)

        self.cursor.execute(sql, val)
        data = self.cursor.fetchone()
        self.db.commit()

        if data is None:
            return False
        else:
            return True

    def oldest_account(self) -> tuple:
        sql = 'SELECT login FROM instagram_accounts WHERE date_update = '
        '(SELECT MIN(date_update) FROM instagram_accounts) LIMIT 1'

        self.cursor.execute(sql)

        return self.cursor.fetchone()
