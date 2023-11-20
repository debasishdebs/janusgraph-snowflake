import utils.common_resources as common


class SQLQueryExecutor:
    def __init__(self, sql):
        self.CONNECTION = None
        self.SQL = sql
        self.initialize_connection()

    def initialize_connection(self):
        connection = common.Commons.get_connection()
        self.CONNECTION = connection.SNOWFLAKE_ENGINE.connect()
        return self

    def execute(self):
        res = self.CONNECTION.execute(self.SQL)
        data = []
        # cols = res.keys()
        # print(f"The cols are {cols} of type {type(cols)}")
        for row in res:
            data.append(row)
        return data
