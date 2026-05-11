import pymysql
from sqlalchemy import create_engine, text
from utils.env import Environment
import logging


class DatabaseHelper:
    """
    数据库操作助手类
    支持MySQL、PostgreSQL等数据库
    """

    def __init__(self):
        self.env = Environment()
        self.db_type = self.env.get_db_type()
        self.host = self.env.get_db_host()
        self.port = self.env.get_db_port()
        self.username = self.env.get_db_username()
        self.password = self.env.get_db_password()
        self.database = self.env.get_db_name()
        self.connection = None
        self.engine = None

    def connect(self):
        """
        建立数据库连接
        """
        try:
            if self.db_type == 'mysql':
                self.connection = pymysql.connect(
                    host=self.host,
                    port=int(self.port),
                    user=self.username,
                    password=self.password,
                    database=self.database,
                    charset='utf8mb4'
                )
            elif self.db_type == 'postgresql':
                # PostgreSQL连接示例
                connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                self.engine = create_engine(connection_string)
            else:
                # 默认使用SQLAlchemy
                connection_string = f"{self.db_type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                self.engine = create_engine(connection_string)
                
            logging.info("数据库连接成功")
            return True
        except Exception as e:
            logging.error(f"数据库连接失败: {e}")
            return False

    def disconnect(self):
        """
        关闭数据库连接
        """
        try:
            if self.connection:
                self.connection.close()
            if self.engine:
                self.engine.dispose()
            logging.info("数据库连接已关闭")
        except Exception as e:
            logging.error(f"关闭数据库连接时出错: {e}")

    def execute_query(self, sql, params=None):
        """
        执行查询语句
        :param sql: SQL查询语句
        :param params: 查询参数
        :return: 查询结果
        """
        try:
            if self.db_type == 'mysql' and self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    result = cursor.fetchall()
                    return result
            elif self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text(sql), params or [])
                    return result.fetchall()
            else:
                raise Exception("数据库未连接")
        except Exception as e:
            logging.error(f"执行查询失败: {e}")
            return None

    def execute_update(self, sql, params=None):
        """
        执行更新语句（INSERT、UPDATE、DELETE）
        :param sql: SQL更新语句
        :param params: 更新参数
        :return: 影响行数
        """
        try:
            if self.db_type == 'mysql' and self.connection:
                with self.connection.cursor() as cursor:
                    affected_rows = cursor.execute(sql, params)
                    self.connection.commit()
                    return affected_rows
            elif self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text(sql), params or [])
                    conn.commit()
                    return result.rowcount
            else:
                raise Exception("数据库未连接")
        except Exception as e:
            logging.error(f"执行更新失败: {e}")
            if self.connection:
                self.connection.rollback()
            return -1

    def get_table_data(self, table_name, condition=None):
        """
        获取表数据
        :param table_name: 表名
        :param condition: 查询条件
        :return: 查询结果
        """
        sql = f"SELECT * FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        return self.execute_query(sql)


if __name__ == "__main__":
    # 测试代码
    db = DatabaseHelper()
    if db.connect():
        print("数据库连接成功")
        # 示例查询
        # result = db.execute_query("SELECT * FROM users LIMIT 5")
        # print(result)
        db.disconnect()