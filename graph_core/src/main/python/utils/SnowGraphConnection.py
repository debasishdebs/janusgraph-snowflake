from utils.utils import Utilities
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SnowGraphConnection:
    SNOWFLAKE_ENGINE = None
    SNOWFLAKE_SESSION = None

    def __init__(self, credentials_dict: dict):
        print("Initializing snowgraph connection with ", credentials_dict)
        self.SNOWFLAKE_CONNECTION = credentials_dict

    def create_snowflake_engine(self):
        conn = URL(
            account=self.SNOWFLAKE_CONNECTION["account"],
            user=self.SNOWFLAKE_CONNECTION["user"],
            password=self.SNOWFLAKE_CONNECTION["password"],
            database=self.SNOWFLAKE_CONNECTION["database"],
            schema=self.SNOWFLAKE_CONNECTION["schema"],
            warehouse=self.SNOWFLAKE_CONNECTION["warehouse"]
        )

        print(self.SNOWFLAKE_CONNECTION)
        self.SNOWFLAKE_ENGINE = create_engine(conn)
        print(self.SNOWFLAKE_ENGINE)
        return self

    def create_snowflake_session(self):
        session = sessionmaker(bind=self.SNOWFLAKE_ENGINE)
        self.SNOWFLAKE_SESSION = session
        return self

    def initialize_tables(self):
        import utils.common_resources as common

        nodes = self.SNOWFLAKE_CONNECTION["nodes_tbl"]
        edges = self.SNOWFLAKE_CONNECTION["edges_tbl"]
        common.Commons.MASTER_TABLE = nodes
        common.Commons.EDGES_TABLE = edges
        return self

    def initialize_snowflake(self):
        self.create_snowflake_engine()
        self.create_snowflake_session()
        self.initialize_tables()
        return self

    def get_connection(self):
        return self.SNOWFLAKE_ENGINE.get_connection()
