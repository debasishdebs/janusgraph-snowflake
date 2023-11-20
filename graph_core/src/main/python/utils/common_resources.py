from utils.SnowGraphConnection import SnowGraphConnection


class Commons:
    CONNECTION: SnowGraphConnection = None
    PROPERTIES: dict = {}

    @staticmethod
    def put_connection(conn: SnowGraphConnection):
        print("Putting connection ", conn)
        Commons.CONNECTION = conn

    @staticmethod
    def get_connection() -> SnowGraphConnection:
        return Commons.CONNECTION

    @staticmethod
    def put_properties(prop: dict):
        print("Putting connection ", prop)
        Commons.PROPERTIES = prop

    @staticmethod
    def get_properties() -> dict:
        return Commons.PROPERTIES

    MASTER_TABLE: str = None
    EDGES_TABLE: str = None
