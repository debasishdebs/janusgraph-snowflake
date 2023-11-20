import json
from utils.use_databricks import apply_node_transformation_to_records, apply_edge_transformation_to_records, conn, create_engine, options
from utils.constants import Commons, APPLICATION_PROPERTIES
from pyspark.sql import *
from pyspark.sql.functions import udf, monotonically_increasing_id, array
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType
from utils.test_dedup import update_edge_id, update_node_id, generate_edge_id, generate_node_id, generate_identifier
import gen.graphdb_pb2_grpc as graphdb_pb2_grpc
import gen.graphdb_pb2 as graphdb_pb2
import datetime as dt
import grpc
from gen.graphdb_pb2_grpc import ServicesToGraphLoaderStub


spark = SparkSession \
    .builder.appName("test"). \
    config("spark.app.id", 123). \
    config("spark.driver.memory", "15g"). \
    getOrCreate()
sc = spark.sparkContext
sc.setLogLevel("ERROR")


resource_properties = Commons.load_properties(APPLICATION_PROPERTIES)
url = f'{resource_properties["grpc.loader.server.host"]}:{resource_properties["grpc.loader.server.port"]}'

MAX_MESSAGE_LENGTH = 250 * 1024 * 1024
loader_options = [
    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
]
loader_channel = grpc.insecure_channel(url, options=loader_options)
LOADER_CLIENT = ServicesToGraphLoaderStub(channel=loader_channel)


if __name__ == '__main__':
    f = open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\main\\resources\\dumps\\dummy.json")
    extracted_data = json.load(f)

    case_id = "160225_sstech_9465_13349890709"

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Tranaformation data aggregated", caseId=case_id, processingTime=procTime)

    print("Aggregated the data into single list")
    sdf = spark.createDataFrame(extracted_data, ["data", "ds", "case_id"])
    sdf = sdf.repartition(100)
    print("Created spark dataframe and repartitions to 100 paritions")

    sdf = sdf.select("*").withColumn("row_id", monotonically_increasing_id())

    nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
    edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Transformation of nodes & edges done", caseId=case_id, processingTime=procTime)

    nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds", "row_id")))
    edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds", "row_id")))

    nodes_sdf = nodes_sdf.select("*").withColumn("id", monotonically_increasing_id())
    edges_sdf = edges_sdf.select("*").withColumn("id", monotonically_increasing_id())
    print("Generated nodes and edges and defined a id column per row")

    merged = nodes_sdf.select("ds", "nodes", "id", "case_id", F.col("row_id").alias("node_row_id")). \
        join(edges_sdf.select("edges", "id", F.col("row_id").alias("edge_row_id")), nodes_sdf.id == edges_sdf.id). \
        select("ds", "nodes", "edges", "case_id", "node_row_id", "edge_row_id")
    print("Merged nodes and edges df")

    merged = merged.withColumn("node_size", F.size(merged.nodes)).withColumn("edge_size", F.size(merged.edges))
    print("Defined 2 cols of node and edge size")

    valid_sdf = merged.filter((merged.node_size >= 1) | (merged.edge_size >= 1))

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Removed invalid nodes & edges (Transformation)", caseId=case_id, processingTime=procTime)

    valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")).select("nodes_exploded", "edges_exploded", "case_id", "ds", "node_row_id", "edge_row_id")
    valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"), "node_row_id", "edge_row_id")

    nodes_sdf = valid_sdf.select("case_id", "ds", "nodes", F.col("node_row_id").alias("row_id"))
    edges_sdf = valid_sdf.select("case_id", "ds", "edges", F.col("edge_row_id").alias("row_id"))

    unique_identifier_udf = udf(generate_identifier, StringType())
    nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf(array("nodes", "ds")))
    dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Nodes deduplicated (Transformation)", caseId=case_id, processingTime=procTime)

    nodes_sdf = dedup_node_sdf.select("nodes", "ds", "case_id", F.col("row_id").alias("node_id"))
    nodes_sdf = nodes_sdf.withColumn("node_id", monotonically_increasing_id())

    edges_sdf = edges_sdf.select("edges", "ds", "case_id")
    edges_sdf = edges_sdf.withColumn("edge_id", monotonically_increasing_id())

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Node & Edge IDs generated (Transformation)", caseId=case_id, processingTime=procTime)

    nodes_sdf = nodes_sdf.withColumn("element", F.lit("node"))
    edges_sdf = edges_sdf.withColumn("element", F.lit("edge"))

    node_id_updater = udf(update_node_id, StringType())
    edge_id_updater = udf(update_edge_id, StringType())

    nodes_sdf = nodes_sdf.withColumn("nodes", node_id_updater(array("nodes", "node_id")))
    edges_sdf = edges_sdf.withColumn("edges", edge_id_updater(array("edges", "edge_id")))

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Node & Edge ID Updated (Transformation)", caseId=case_id, processingTime=procTime)

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status="Node & Edge ID Updated (Transformation)", caseId=case_id, processingTime=procTime)

    node_id_generator = udf(generate_node_id, StringType())
    edge_id_generator = udf(generate_edge_id, StringType())
    nodes_sdf = nodes_sdf.withColumn("nodes_id_gen", node_id_generator(array("nodes", "node_id")))
    edges_sdf = edges_sdf.withColumn("edges_id_gen", edge_id_generator(array("edges", "edge_id")))

    # unique_node_ids = [i.nodes_id_gen for i in nodes_sdf.select('nodes_id_gen').distinct().collect()]
    # unique_edge_ids = [i.edges_id_gen for i in edges_sdf.select('edges_id_gen').distinct().collect()]
    # print(f"After generating unique node id, the count is {len(unique_node_ids)} and rows in nodes df: {nodes_sdf.count()} using generator")
    # print(f"After generating unique edge id, the count is {len(unique_edge_ids)} and rows in edges df: {edges_sdf.count()} using generator")
    #
    # unique_node_ids = [i.node_id for i in nodes_sdf.select('node_id').distinct().collect()]
    # unique_edge_ids = [i.edge_id for i in edges_sdf.select('edge_id').distinct().collect()]
    # print(f"After generating unique node id, the count is {len(unique_node_ids)} and rows in nodes df: {nodes_sdf.count()} using rowid")
    # print(f"After generating unique edge id, the count is {len(unique_edge_ids)} and rows in edges df: {edges_sdf.count()} using rowid")

    nodes_sdf = nodes_sdf.select("case_id", "ds", F.col("element").alias("element_type"), F.col("nodes").alias("element"), F.col("nodes_id_gen").alias("element_id"))
    nodes_sdf = nodes_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    edges_sdf = edges_sdf.select("case_id", "ds", F.col("element").alias("element_type"), F.col("edges").alias("element"), F.col("edges_id_gen").alias("element_id"))
    edges_sdf = edges_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    final_sdf = nodes_sdf.union(edges_sdf)

    output_table = 'transformed_graph_data'
    print(f"Writing data to snowflake table {output_table} under DB: {options['sfDatabase']} and schema: {options['sfSchema']}")

    final_sdf = final_sdf.select("element", "element_type", "case_id", "ds", "processing_dttm")
    print(final_sdf.show(50))
    final_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
    print("Saved data to snowflake table")

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to {output_table}", caseId=case_id, processingTime=procTime)

    # nodes_pdf = valid_sdf.select("nodes").toPandas()
    nodes_pdf = final_sdf.filter(final_sdf.element_type == 'node').toPandas()
    nodes_json = json.loads(nodes_pdf.to_json(orient="records"))

    nodes_proto = []
    for row in nodes_json:
        node = json.loads(row["element"])

        elem = graphdb_pb2.Node()
        for k, v in node.items():
            vv = Commons._convert_value_to_struct_value_(v)
            elem.properties[k].CopyFrom(vv)
        nodes_proto.append(elem)

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    graphdb_pb2.CaseLoadingStatus(status=f"Transformation completed", caseId=case_id, processingTime=procTime)

    table = graphdb_pb2.TransformedDataTable(table=output_table, caseId=case_id, nodes=nodes_proto)
    LOADER_CLIENT.EnsureGraphInSnowFromFromTable(table)
