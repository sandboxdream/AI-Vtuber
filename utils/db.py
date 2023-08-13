import sqlite3
import threading
from queue import Queue
from datetime import datetime


class SQLiteDB:
    def __init__(self, db_file, max_connections=5):
        self.db_file = db_file
        self.connection_pool = self._create_connection_pool(max_connections)

    def _create_connection_pool(self, max_connections):
        connections = Queue(max_connections)
        for _ in range(max_connections):
            conn = sqlite3.connect(self.db_file)
            connections.put(conn)
        return connections

    def _get_connection(self):
        return self.connection_pool.get()

    def _release_connection(self, conn):
        self.connection_pool.put(conn)

    def execute(self, query, args=None):
        conn = sqlite3.connect(self.db_file)  # 创建新的连接对象
        cursor = conn.cursor()

        try:
            if args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            conn.commit()
        finally:
            conn.close()

    def fetch_all(self, query, args=None):
        conn = sqlite3.connect(self.db_file)  # 创建新的连接对象
        cursor = conn.cursor()

        try:
            if args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()
    # def __init__(self, db_file, max_connections=5):
    #     self.db_file = db_file
    #     self.connection_pool = self._create_connection_pool(max_connections)
    #     self.db_lock = threading.Lock()

    # def _create_connection_pool(self, max_connections):
    #     connections = Queue(max_connections)
    #     for _ in range(max_connections):
    #         conn = sqlite3.connect(self.db_file)
    #         connections.put(conn)
    #     return connections

    # def _get_connection(self):
    #     return self.connection_pool.get()

    # def _release_connection(self, conn):
    #     self.connection_pool.put(conn)

    # def execute(self, query, args=None):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()

    #     try:
    #         with self.db_lock:
    #             if args:
    #                 cursor.execute(query, args)
    #             else:
    #                 cursor.execute(query)
    #             conn.commit()
    #     finally:
    #         self._release_connection(conn)

    # def fetch_all(self, query, args=None):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()

    #     try:
    #         with self.db_lock:
    #             if args:
    #                 cursor.execute(query, args)
    #             else:
    #                 cursor.execute(query)
    #             return cursor.fetchall()
    #     finally:
    #         self._release_connection(conn)


if __name__ == "__main__":
    db = SQLiteDB('data/test.db')

    # 创建表
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS danmu (
        username TEXT,
        content TEXT,
        ts DATETIME
    )
    '''
    db.execute(create_table_sql)

    # 插入数据
    insert_data_sql = '''
    INSERT INTO danmu (username, content, ts) VALUES (?, ?, ?)
    '''
    db.execute(insert_data_sql, ('user1', 'test1', datetime.now()))

    # 查询数据
    select_data_sql = '''
    SELECT * FROM danmu
    '''
    data = db.fetch_all(select_data_sql)
    print(data)
