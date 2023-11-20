from client.connection.SnowGraphConnection import SnowGraphConnection
import datetime as dt


class Commons:
    CONNECTION: SnowGraphConnection = None
    BYTECODE = []
    @staticmethod
    def put_connection(conn: SnowGraphConnection):
        Commons.CONNECTION = conn

    @staticmethod
    def get_connection() -> SnowGraphConnection:
        return Commons.CONNECTION

    @staticmethod
    def put_bytecode(val):
        Commons.BYTECODE.append(val)

    @staticmethod
    def get_bytecode():
        return Commons.BYTECODE

    @staticmethod
    def convert_time(time: dt.datetime):
        return time.strftime("%Y-%m-%d %H:%M:%S")
