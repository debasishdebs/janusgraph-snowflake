from pyspark.sql import SparkSession
import os
import json
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

user = "Debasish"
password = "Work@456"

account = "ik55883.east-us-2.azure"
user = user
pwd = password
watehouse = "COMPUTE_WH"
database = "snowflake_graph_test"
schema = "graph_test"
host = "azure"

conn = URL(
    account=account,
    user=user,
    password=pwd,
    database=database,
    schema=schema,
    warehouse=watehouse
)

engine = create_engine(conn)


def main():
    # os.environ["HADOOP_HOME"] = "C:\\hadoop-2.6.0"
    # spark = SparkSession \
    #     .builder \
    #     .getOrCreate()
    # sc = spark.sparkContext
    # sc.setLogLevel("INFO")
    # print("Testing simple count")
    # print(spark.range(100).count())
    graph = json.load(open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\"
                           "snowflake-graphdb\\graphtransformer\\src\\main\\resources\\dumps\\160156_sstech_4400.441773891449_graph.json"))
    print(graph.keys())
    data = []
    for node in graph["nodes"]:
        node_n = node
        node_n["caseId"] = "160156_sstech_4400.441773891449_graph"
        node_n["elem_type"] = "node"
        data.append(node_n)

    for edge in graph["edges"]:
        edge_n = edge
        edge["caseId"] = "160156_sstech_4400.441773891449_graph"
        edge["elem_type"] = "edge"
        data.append(edge_n)

    result = [json.dumps(x) for x in data]
    # result = "\n".join(result)
    fname = "D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\" \
            "graphtransformer\\src\\main\\resources\\dumps\\staging.to.load"

    f = open(fname, "w+")
    for r in result:
        f.write(r + "\n")
    f.close()

    sql = "PUT file://C:\\Users\\DebasishKanhar\\Documents\\staging.to.load @graph_stage_02;"
    engine.execute(sql)
    # PUT file://D:\Projects\Projects\Freelancing\Elysium Analytics\graphdb-in-snowflake\snowflake-graphdb\graphtransformer\src\main\resources\dumps\staging.to.load @graph_stage_01;
    print("put to stage")

    # json.dump(result, open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\"
    #                            "snowflake-graphdb\\graphtransformer\\src\\main\\resources\\dumps\\staging.to.load", "w+"))


def main1():
    from pyspark.sql.functions import udf, monotonically_increasing_id, array
    import pyspark.sql.functions as F
    from pyspark.sql.types import ArrayType, StringType
    from utils.use_databricks import apply_node_transformation_to_records, apply_edge_transformation_to_records, options

    case_id = '160156_sstech_4400.441773891449'

    f = open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\main\\resources\\dumps\\dummy.json")
    data = json.load(f)

    spark = SparkSession \
        .builder.appName("test"). \
        config("spark.app.id", 123). \
        config("spark.driver.memory", "15g"). \
        getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")
    print("Created spark session")

    sdf = spark.createDataFrame(data, ["data", "ds", "case_id"])
    sdf = sdf.repartition(100)
    print("Create spark dataframe and repartition")

    nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
    edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))
    print("Created udfs and mapped")

    nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds", "case_id")))
    edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds", "case_id")))
    print("Transformed to generate nodes and edges")

    nodes_sdf = nodes_sdf.select("*").withColumn("id", monotonically_increasing_id())
    edges_sdf = edges_sdf.select("*").withColumn("id", monotonically_increasing_id())
    print("Created row id column")

    merged = nodes_sdf.select("ds", "nodes", "id", "case_id"). \
        join(edges_sdf.select("edges", "id"), nodes_sdf.id == edges_sdf.id). \
        select("ds", "nodes", "edges", "case_id")
    print("Merged nodes and edges df")

    merged = merged.withColumn("node_size", F.size(merged.nodes)).withColumn("edge_size", F.size(merged.edges))
    print("Created element size columns")

    valid_sdf = merged.filter((merged.node_size >= 1) | (merged.edge_size >= 1))
    print("Filtered rows with size > 0")

    print(f"Size of df before explosion {valid_sdf.count()}")

    valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")).select("nodes_exploded", "edges_exploded", "case_id", "ds")
    print("Exploded the dataframe by splitting nodes and edges into multiple rows")
    print(f"Old col names {valid_sdf.schema.names}")
    valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"))
    valid_sdf = valid_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    valid_sdf = valid_sdf.select("nodes", "edges", "case_id", "ds", "processing_dttm")

    print(f"New col names {valid_sdf.schema.names}")
    print("Renamed column names")
    print(f"Size of df after explosion {valid_sdf.count()}")

    options['sfSchema'] = 'tempData'
    output_table = 'transformed_graph_data'
    print(f"Writing data to snowflake table {case_id} under DB: {options['sfDatabase']} and schema: {options['sfSchema']}")

    valid_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
    print("Write to table " + output_table)


if __name__ == '__main__':
    import datetime as dt
    st = dt.datetime.now()
    main1()
    print(f"Total execution time {dt.datetime.now()-st}")
