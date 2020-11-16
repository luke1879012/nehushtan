#  Copyright (c) 2020. The Source Data Mining Group, Technology & Product Department, Leqee Ltd.

# VERSION 1.11.1, 2020-11-16
# WARNING: DO NOT MODIFY THIS FILE, JUST FOLLOW THE SHOVEL STANDARD!


from typing import Callable

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from nehushtan.mysql import constant


class MySQLKit:
    """
    MySQL 连接基础工具类，封装了 PYMYSQL 库的实例。
    Shovel 项目相关的所有 MySQL 连接应当使用此方法进行。
    """

    _mysql_config: dict
    _auto_commit_default: bool
    _connection: Connection or None

    def __init__(self, mysql_config: dict):
        """
        获取一个字典并根据此字典包含配置立即建立一个新的数据库连接。
        PYMYSQL 默认不自动递交。在实际场景中，建议设置成默认自动递交并仅在需要时手动开启事务。
        :param mysql_config: 字典，样本参见配置文件标准示例中 `mysql_database`.`sample` 项
        """
        self._mysql_config = mysql_config
        self._auto_commit_default = self._mysql_config.get('auto_commit', False)
        self._connection = None
        if len(self._mysql_config.items()) > 0:
            self.connect()

    # @staticmethod
    # def make_instance_from_config(target: str):
    #     """
    #     根据配置文件中 `mysql_database`.`[target]` 项来生成本类实例。
    #     :param target: 配置文件中标示的数据库连接名
    #     :return: 本类实例
    #     """
    #     config = ShovelHelper.read_config_for_mysql(target, {})
    #     return MySQLKit(config)

    @staticmethod
    def make_instance_from_pymysql_connection(connection: Connection):
        """
        根据一个已经存在的 PYMYSQL 连接，构建一个本类实例。
        这样建立的实例里的配置字典为空，而自动提交参数根据入参连接的实际情况获取。
        :param connection:
        :return: 本类实例
        """
        kit = MySQLKit({})
        kit._connection = connection
        kit._auto_commit_default = connection.get_autocommit()
        return kit

    def get_raw_connection(self) -> Connection:
        """
        :return: 封装的 PYMYSQL 原生 CONNECTION 实例
        """
        return self._connection

    def connect(self) -> "MySQLKit":
        """
        It may raise Exception if connection failed, as I viewed the document
        :return: MySQLKit the instance itself
        """

        self.disconnect()

        self._auto_commit_default = self._mysql_config.get('auto_commit', False)
        self._connection = pymysql.connect(
            host=self._mysql_config.get('host', ''),  # '172.16.1.52',
            port=int(self._mysql_config.get('port', '3306')),  # 3306,
            user=self._mysql_config.get('user', ''),
            password=self._mysql_config.get('password', ''),
            db=self._mysql_config.get('db', ''),
            charset=self._mysql_config.get('charset', ''),
            autocommit=self._auto_commit_default,
        )
        return self

    def disconnect(self) -> "MySQLKit":
        if self._connection is not None:
            self._connection.close()
        self._connection = None
        return self

    def raw_get_computed_sql(self, sql: str, args=None) -> str:
        """
        使用 PYMYSQL 原生的方法获取构建的 SQL 语句用于预览
        :param sql: SQL 模板
        :param args: 参数
        :return: 生成的 SQL 语句
        """
        cursor = self._connection.cursor()
        sql = cursor.mogrify(sql, args)
        cursor.close()
        return sql

    def raw_query_for_all_tuple_rows(self, sql: str, args=None) -> tuple:
        """
        查询一个SQL并获取包含所有结果行的元组，其中的每行也封装成一个元组
        :param sql:
        :param args:
        :return:
        """
        cursor = self._connection.cursor()
        cursor.execute(sql, args)
        rows_tuple = cursor.fetchall()
        cursor.close()
        return rows_tuple

    def raw_query_for_all_dict_rows(self, sql: str, args=None) -> tuple:
        """
        查询一个SQL并获取包含所有结果行的元组，其中的每行封装成一个字典
        :param sql:
        :param args:
        :return:
        """
        cursor = self._connection.cursor(DictCursor)
        cursor.execute(sql, args)
        rows_tuple = cursor.fetchall()
        cursor.close()
        return rows_tuple

    def raw_query_to_modify_one(self, sql: str, args=None, commit_immediately: bool = None):
        """
        执行一个非读SQL并返回影响行数
        :param sql:
        :param args:
        :param commit_immediately:
        :return:
        """
        cursor = self._connection.cursor()
        afx = cursor.execute(sql, args)
        if commit_immediately is None:
            commit_immediately = self._auto_commit_default
        if commit_immediately:
            self._connection.commit()
        cursor.close()
        return afx

    def raw_query_to_insert_one(self, sql: str, args=None, commit_immediately: bool = None):
        """
        执行一条插入语句并获取最后更新的行的ID
        :param sql:
        :param args:
        :param commit_immediately:
        :return:
        """
        cursor = self._connection.cursor()
        cursor.execute(sql, args)
        last_row_id = cursor.lastrowid
        if commit_immediately is None:
            commit_immediately = self._auto_commit_default
        if commit_immediately:
            self._connection.commit()
        cursor.close()
        return last_row_id

    def raw_query_to_modify_many(self, sql: str, args=None, commit_immediately: bool = None):
        """
        执行原生的SQL批量变更并获取影响行数
        :param sql:
        :param args:
        :param commit_immediately:
        :return:
        """
        cursor = self._connection.cursor()
        afx = cursor.executemany(sql, args)
        if commit_immediately is None:
            commit_immediately = self._auto_commit_default
        if commit_immediately:
            self._connection.commit()
        cursor.close()
        return afx

    def raw_query_to_insert_many(self, sql: str, args=None, commit_immediately: bool = None):
        """
        执行原生的SQL批量插入并获取最后更新行的ID
        :param sql:
        :param args:
        :param commit_immediately:
        :return:
        """
        cursor = self._connection.cursor()
        cursor.executemany(sql, args)
        last_row_id = cursor.lastrowid
        if commit_immediately is None:
            commit_immediately = self._auto_commit_default
        if commit_immediately:
            self._connection.commit()
        cursor.close()
        return last_row_id

    def raw_execute_transaction(self, transaction_callable: Callable[["MySQLKit"], any]):
        """
        一个封装的方法，用于快速包装事务。
        :param transaction_callable: 事务处理具体代码所在的闭包，可以使用lambda表达式或者def方法，参数为本类实例，并返回结果
        :return: 返回闭包的返回值
        """
        self._connection.begin()
        try:
            result = transaction_callable(self)
            print('to commit', result)
            self._connection.commit()
            return result
        except Exception as e:
            print('to rollback')
            self._connection.rollback()
            raise e

    def quote(self, value):
        """
        将任意入参进行转义以防范注入。
        如果连接关闭，则使用脱机转义。
        数字、空值、布尔值不加引号，其他都作为字符串加外部引号可用于字符串拼接。
        如果入参为元组或者列表，也以同样形式返回转义所有元素的新实例。
        :param value:
        :return:
        """
        if self._connection is None:
            return self.quote_offline(value)
        if type(value) == list:
            x = []
            for item in value:
                x.append(self.quote(item))
            return x
        elif type(value) == tuple:
            x = []
            for item in value:
                x.append(self.quote(item))
            return tuple(x)
        elif type(value) == int or type(value) == float:
            return value
        elif value is None:
            return constant.MYSQL_CONDITION_CONST_NULL
        elif value is True:
            return constant.MYSQL_CONDITION_CONST_TRUE
        elif value is False:
            return constant.MYSQL_CONDITION_CONST_FALSE
        elif type(value) == str:
            escaped = self._connection.escape_string(value)
            return f"'{escaped}'"
        else:
            return self.quote(value.__str__())

    @staticmethod
    def quote_offline(value):
        """
        脱机转义
        :param value:
        :return:
        """
        if type(value) == list:
            x = []
            for item in value:
                x.append(MySQLKit.quote_offline(item))
            return x
        elif type(value) == tuple:
            x = []
            for item in value:
                x.append(MySQLKit.quote_offline(item))
            return tuple(x)
        elif type(value) == int or type(value) == float:
            return f'{value}'
        elif type(value) == str:
            return MySQLKit.quote_string_offline(value)
        elif value is None:
            return constant.MYSQL_CONDITION_CONST_NULL
        elif value is True:
            return constant.MYSQL_CONDITION_CONST_TRUE
        elif value is False:
            return constant.MYSQL_CONDITION_CONST_FALSE
        else:
            return MySQLKit.quote_string_offline(value.__str__())

    @staticmethod
    def quote_string_offline(value: str) -> str:
        """
        脱机转义字符串。
        :param value:
        :return: 包含了外层引号
        """
        d = {
            '\\': '\\\\',
            '\0': '\\0',
            '\n': '\\n',
            '\r': '\\r',
            "'": "\\'",
            '"': '\\"',
            '\x1a': '\\Z',
        }
        s = value
        for k, v in d.items():
            s = s.replace(k, v)

        return f"'{s}'"
