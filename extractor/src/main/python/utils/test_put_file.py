from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine


if __name__ == '__main__':
    user = "Debasish"
    password = "Work@456"

    account = "ik55883.east-us-2.azure"
    user = user
    pwd = password
    watehouse = "COMPUTE_WH"
    database = "snowflake_graph_test"
    schema = "graph_test"
    host = "azure"

    # snowflake connection options
    options = {
        "sfUrl": "https://ik55883.east-us-2.azure.snowflakecomputing.com/",
        "sfAccount": "ik55883",
        "sfUser": user,
        "sfPassword": password,
        "sfDatabase": database,
        "sfSchema": schema,
        "sfWarehouse": watehouse
    }

    conn = URL(
        account=account,
        user=user,
        password=pwd,
        database=database,
        schema=schema,
        warehouse=watehouse
    )

    engine = create_engine(conn)

    sql = "put file://D:\\temp\\msexchange_160277_sstech_8851_421793937683_0_0.csv @snowgraph_stage"
    engine.execute(sql)
