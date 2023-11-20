from pyspark.sql import *
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.functions import udf, array
from pyspark.sql.functions import lit, when, col, regexp_extract, arrays_zip, col, explode
import pyspark.sql.functions as F
import json
import pandas as pd
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from pyspark.sql.functions import monotonically_increasing_id
from functools import reduce

from process.IncomingDataToGraphTransformer import IncomingDataToGraphTransformer


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
datamappers = json.loads(pd.read_sql_table("datamappers", engine).to_json(orient='records'))
datamappers_dict = []
for dm in datamappers:
    dm_n = {"datamapper": json.loads(dm["datamapper"]), "nodes": json.loads(dm["nodes"]),
            "edges": json.loads(dm["edges"]), "analyze": json.loads(dm["analyze"]), "datasource": dm["datasource"]}
    datamappers_dict.append(dm_n)
# print(datamappers_dict)
# print(datamappers_dict[0], type(datamappers_dict[0]["datamapper"]))
# print(datamappers_dict[0].keys())
# print(len(datamappers_dict))
# exit(-1)


def create_spark_dataframe(data, cols, spark: SparkSession):
    return spark.createDataFrame(data, cols)


def create_spark_session():
    spark = SparkSession \
        .builder.appName("test").\
        config("spark.app.id", 123). \
        config("spark.driver.memory", "15g").\
        getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")
    # print(spark.range(100).count())
    return spark


def transform_spark_dataframe(sdf: DataFrame, spark: SparkSession):
    nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
    edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

    # datamappers = spark.read.format("net.snowflake.spark.snowflake").options(**options).option("dbtable", "datamappers").load()
    # print(sdf.printSchema())

    nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds", "case_id")))
    edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds", "case_id")))
    nodes_sdf = nodes_sdf.select("*").withColumn("id", monotonically_increasing_id())
    edges_sdf = edges_sdf.select("*").withColumn("id", monotonically_increasing_id())

    # print(nodes_sdf.show())
    # print(edges_sdf.show())

    merged = nodes_sdf.select("ds", "nodes", "id").join(edges_sdf.select("edges", "id"), nodes_sdf.id == edges_sdf.id).select("ds", "nodes", "edges")
    # print(merged.show())
    # print(f"Number of rows of dataframe before filter {merged.count()}")
    # merged_sdf = merged.withColumn("node_size", F.size(merged.nodes))
    # merged_sdf = merged_sdf.withColumn("edge_size", F.size(merged.edges))
    # merged_sdf = merged_sdf.filter((merged_sdf.node_size >= 1) | (merged_sdf.edge_size >= 1))
    # print(f"Number of rows of dataframe after filter {merged_sdf.count()}")
    return merged.select("nodes", "edges", "ds")


def apply_node_transformation_to_records(x: list):
    data = json.loads(x[0])
    ds = x[1]
    # row_id = x[2]

    # datamapper = json.loads(datamappers[datamappers["datasource"] == ds]["datamapper"].values.tolist()[0])
    datamapper = [x["datamapper"] for x in datamappers_dict if x["datasource"] == ds][0]
    # datamapper =

    windows = []
    msexchange = []
    sysmon = []
    wgtraffic = []
    sepc = []
    if ds == "windows":
        windows = [data]
    elif ds == "msexchange":
        msexchange = [data]
    elif ds == "sysmon":
        sysmon = [data]
    elif ds == "watchguard":
        wgtraffic = [data]
    else:
        sepc = [data]

    merged_data = {
        "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
        "networkRecords": wgtraffic, "sepcRecords": sepc
    }

    convertor = IncomingDataToGraphTransformer(merged_data)
    convertor.with_datamapper(datamapper, ds)
    # convertor.for_row_id(row_id)
    graph = convertor.convert()

    return [json.dumps(x) for x in graph["nodes"]]


def read_data_mapper_from_snowflake(ds):

    return


def apply_edge_transformation_to_records(x: list):
    data = json.loads(x[0])
    ds = x[1]
    # row_id = x[2]

    # datamapper = json.loads(datamappers[datamappers["datasource"] == ds]["datamapper"].values.tolist()[0])
    datamapper = [x["datamapper"] for x in datamappers_dict if x["datasource"] == ds][0]

    windows = []
    msexchange = []
    sysmon = []
    wgtraffic = []
    sepc = []
    if ds == "windows":
        windows = [data]
    elif ds == "msexchange":
        msexchange = [data]
    elif ds == "sysmon":
        sysmon = [data]
    elif ds == "watchguard":
        wgtraffic = [data]
    else:
        sepc = [data]

    merged_data = {
        "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
        "networkRecords": wgtraffic, "sepcRecords": sepc
    }

    convertor = IncomingDataToGraphTransformer(merged_data)
    convertor.with_datamapper(datamapper, ds)
    # convertor.for_row_id(row_id)
    graph = convertor.convert()

    return [json.dumps(x) for x in graph["edges"]]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def read_spark_data(spark):
    sdf = spark.read.format("snowflake").options(**options).option("dbtable", "datamappers").load()
    print(sdf.show())
    print("tested retriveal of table using spark")
    return


if __name__ == '__main__':
    import datetime as dt
    import os
    st = dt.datetime.now()
    st1 = dt.datetime.now()

    root_path = "D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\\main\\resources\\dumps\\"
    files = os.listdir(root_path)
    windows_f = []
    sepc_f = []
    wgtraffic_f = []
    sysmon_f = []
    exchange_f = []
    for f in files:
        if "windows" in f:
            windows_f.append(f)
        elif "sepc" in f:
            sepc_f.append(f)
        elif "exchange" in f:
            exchange_f.append(f)
        elif "wgtraffic" in f:
            wgtraffic_f.append(f)
        elif "sysmon" in f:
            sysmon_f.append(f)

    windows_f = ["Case_160035_sstech_5543.428108930588_windows_incoming_data.json"]
    sepc_f = ["Case_160045_sstech_3009.8988740444183_sepc_incoming_data.json"]
    wgtraffic_f = ["Case_160045_sstech_3009.8988740444183_wgtraffic_incoming_data.json"]
    sysmon_f = ["Case_160035_sstech_5543.428108930588_sysmon_incoming_data.json"]
    exchange_f = ["Case_160035_sstech_5543.428108930588_exchange_incoming_data.json"]
    windows = []
    sepc = []
    wgtraffic = []
    sysmon = []
    exchange = []
    windows.extend([x for y in windows_f for x in json.load(open(root_path + y))])
    sepc.extend([x for y in sepc_f for x in json.load(open(root_path + y))])
    wgtraffic.extend([x for y in wgtraffic_f for x in json.load(open(root_path + y))])
    sysmon.extend([x for y in sysmon_f for x in json.load(open(root_path + y))])
    exchange.extend([x for y in exchange_f for x in json.load(open(root_path + y))])

    # windows = json.load(open(root_path + windows_f))
    # sepc = json.load(open(root_path + sepc_f))
    # wgtraffic = json.load(open(root_path + wgtraffic_f))
    # sysmon = json.load(open(root_path + sysmon_f))
    # exchange = json.load(open(root_path + exchange_f))

    print(f"Time to read data {dt.datetime.now() - st}")

    data = []
    data.extend([[json.dumps(x), "windows", "Case_160045"] for x in windows])
    data.extend([[json.dumps(x), "sepc", "Case_160045"] for x in sepc])
    data.extend([[json.dumps(x), "watchguard", "Case_160045"] for x in wgtraffic])
    data.extend([[json.dumps(x), "sysmon", "Case_160045"] for x in sysmon])
    data.extend([[json.dumps(x), "msexchange", "Case_160045"] for x in exchange])

    print(f"Time to aggregate to single list {dt.datetime.now() - st} of size {len(data)}")

    spark = create_spark_session()
    print("Created spark session")
    print(data[:2])

    read_spark_data(spark)
    exit(-1)
    # data = data[:50000]

    chunked_data = list(chunks(data, 100000))
    print(f"Chunked data into {len(chunked_data)} chunks")
    datas = []
    sdfs = []
    idx = 1
    # for chunk in chunked_data:
    #     i_st = dt.datetime.now()
    #     sdf = spark.createDataFrame(chunk, ["data", "ds", "case_id"])
    #     print(f"Number of partitions {sdf.rdd.getNumPartitions()}")
    #     sdf = sdf.repartition(10)
    #     print(f"Number of partitions {sdf.rdd.getNumPartitions()}")
    #     sdf = transform_spark_dataframe(sdf, spark)
    #     # print(pdf.head(10))
    #     # datas.append(pdf)
    #     sdfs.append(sdf)
    #
    #     print(f"Iteration: {idx} in {dt.datetime.now()-i_st}")
    #     idx += 1

    sdf = spark.createDataFrame(data, ["data", "ds", "case_id"])
    print(f"Number of partitions {sdf.rdd.getNumPartitions()}")
    sdf = sdf.repartition(75)
    print(f"Number of partitions {sdf.rdd.getNumPartitions()}")
    sdf = transform_spark_dataframe(sdf, spark)
    sdfs.append(sdf)
    #
    # data = [
    #     [json.dumps({"EventTime": "2020-05-25 11:3:46", "Hostname": "SSTECHLAPTOP357.sstech.internal", "EventID": "400"}), "sepc", "sstech_123"],
    #     [json.dumps({"EventTime": "2020-06-05 12:3:46", "Hostname": "SSTECHLAPTOP357.sstech.internal", "EventID": "400"}), "sepc", "sstech_124"],
    #     [json.dumps({"EventTime": "2020-05-10 12:3:46", "Hostname": "SSTECHLAPTOP357.sstech.internal", "EventID": "400"}), "sepc", "sstech_125"]
    # ]

    print(f"Time to complete process {dt.datetime.now() - st}")
    print(f"Number of records : {len(data)}")
    print(f"Number of windows files: {len(windows_f)}, sepc files: {len(sepc_f)}, sysmon files: {len(sysmon_f)}, exchange files: {len(exchange_f)}, wgtraffifc files: {len(wgtraffic_f)}")
    print(f"Number of windows data: {len(windows)}, sepc data: {len(sepc)}, sysmon data: {len(sysmon)}, exchange data: {len(exchange)}, wgtraffifc data: {len(wgtraffic)}")

    st = dt.datetime.now()
    final_sdf = reduce(DataFrame.union, sdfs)
    print("Showing head 50 of final df")
    # print(final_sdf.show(20))
    print(f"Took {dt.datetime.now()-st} to merge the dataframe into single SDF")
    # final_pdf = pd.concat(datas)

    st = dt.datetime.now()

    # print(f"Number of rows of dataframe before filter {len(data)}")
    merged_sdf = final_sdf.withColumn("node_size", F.size(final_sdf.nodes)).withColumn("edge_size", F.size(final_sdf.edges))
    # print(f"Unique node size vals: {[i.node_size for i in merged_sdf.select('node_size').distinct().collect()]} "
    #       f"and edge size vals: {[i.edge_size for i in merged_sdf.select('edge_size').distinct().collect()]}")
    # merged_sdf = final_sdf.withColumn("node_size", F.size(final_sdf.nodes))
    # merged_sdf = merged_sdf.withColumn("edge_size", F.size(merged_sdf.edges))
    # invalid_sdf = merged_sdf.filter((merged_sdf.edge_size == 0) | (merged_sdf.node_size == 0))
    # valid_edge_df = merged_sdf.filter((merged_sdf.edge_size == 0) | (merged_sdf.node_size == 0))
    # valid_node_df = merged_sdf.filter(merged_sdf.node_size == 0)
    # print("Showing count of df with either len edges = 0")
    # print(valid_edge_df.count())
    # print("Showing count of df with either len nodes = 0")
    # print(valid_node_df.count())
    # print("Showing count of df where either node size = 0 or edge size = 0")
    # print(invalid_sdf.count())

    valid_edge_df = merged_sdf.filter(merged_sdf.edge_size == 0)
    valid_node_df = merged_sdf.filter(merged_sdf.node_size == 0)
    print(f"Number of rows with edge = 0: {valid_edge_df.count()} and with node = 0 {valid_node_df.count()}")

    valid_sdf = merged_sdf.filter((merged_sdf.node_size >= 1) | (merged_sdf.edge_size >= 1))
    valid_sdf = valid_sdf.select("nodes", "edges", "ds")

    print(f"Before explosion, the df size {valid_sdf.count()}")
    print(valid_sdf.show(10))
    valid_sdf = valid_sdf.withColumn("nodes_exploded",  explode("nodes")).withColumn("edges_exploded",  explode("edges")).select("nodes_exploded", "edges_exploded")
    # print(valid_sdf.show(n=200))
    print(f"After explosion, the df size {valid_sdf.count()}")
    print("Dropping node duplicated")
    dedup_node_pdf = valid_sdf.dropDuplicates(['nodes_exploded']).toPandas()
    # print(f"Size of deduplicated nodes df {dedup_node_pdf.count()}")
    dedup_edge_pdf = valid_sdf.dropDuplicates(['edges_exploded']).toPandas()
    # print(f"Size of deduplicated edge df {dedup_edge_pdf.count()}")

    print(f"Time taken for removal of blank elements and other processing is {dt.datetime.now() - st}")
    print(f"Total time taken is {dt.datetime.now() - st}")

    st = dt.datetime.now()
    nodes = dedup_node_pdf["nodes_exploded"].values.tolist()
    edges = dedup_edge_pdf["edges_exploded"].values.tolist()
    nodes = [json.loads(x) for x in nodes]
    edges = [json.loads(x) for x in edges]

    print(f"Num nodes: {len(nodes)} and edges: {len(edges)} after deduplication in {dt.datetime.now()-st}")

    # valid_pdf = valid_sdf.toPandas()
    # print(valid_sdf.show(50))
    # print(f"Number of rows of dataframe after filter {valid_sdf.co}")
    # print(f"Unique node size {valid_pdf.node_size.unique()} and edge size: {valid_pdf.edge_size.unique()}")
    # print("VERIFYING after dropping blank rows")
    # print(f"Unique node size vals: {[i.node_size for i in valid_sdf.select('node_size').distinct().collect()]} "
    #       f"and edge size vals: {[i.edge_size for i in valid_sdf.select('edge_size').distinct().collect()]}")
    #
    # print(valid_sdf.count())

    # TOT records: 357760
    # 50k batch size 0:15:00.554419 [4 partitions]
    # 50k batch size 0:24:37.884307 [25 partitions]
    # 100k batch size 0:18:03.010251 (x2) [25 partitions] / 0:43:56.642366 [Without filters of node size] / Same with filter in end
    # No batching 100 partitions 0:15:26.987091
    # No batching 75 partitions 0:09:36.008495
