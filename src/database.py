import sqlite3


class UsersTableGet():
    async def ID(self, telegram_id: int):
        """
        TODO
        """
        connect = sqlite3.connect('db/users.db')
        cursor = connect.cursor()

        insert_values = [telegram_id]

        cursor.execute(
            '''
            SELECT ID
            FROM users
            WHERE telegram_id = ?
            ''', insert_values)

        r_data = cursor.fetchone()

        if r_data:
            return r_data[0]

        return None


class UsersTable:
    get = UsersTableGet()

    async def add(self, telegram_id: int):
        connect = sqlite3.connect('db/users.db')
        cursor = connect.cursor()

        insert_values = [
            telegram_id]

        cursor.execute(
            '''
            INSERT INTO users(
                telegram_id)
            VALUES(
                ?)
            ''', insert_values)

        connect.commit()

        return True

    async def create(self):
        """
        Use this method to create a users table
        if it does not exist.
        """
        connect = sqlite3.connect('db/users.db')
        cursor = connect.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS
            users(
                ID INTEGER PRIMARY KEY,
                telegram_id INTEGER)
            ''')

        return True


class Database():
    """
    Base database class
    """
    users = UsersTable()

    async def create(self):
        """
        Use this method to create all non-existent
        tables in the database.
        """

        await Database.users.create()
