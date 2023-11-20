import gen.graphdb_pb2 as graphdb_pb2
import datetime as dt
from time import sleep
import grpc, json, os
from utils.constants import Commons, APPLICATION_PROPERTIES
from gen.graphdb_pb2_grpc import ServicesToGraphCoreStub
from pyspark.sql import *
from pyspark.sql.functions import udf, monotonically_increasing_id, array
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType, MapType
from utils.use_databricks import apply_node_transformation_to_records, apply_edge_transformation_to_records
from utils.test_dedup_2 import convert_to_json_from_str
import pandas as pd
from utils.use_databricks import create_engine, conn

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


engine = create_engine(conn)
datamappers = json.loads(pd.read_sql_table("datamappers", engine).to_json(orient='records'))
print(datamappers)
datamappers_list = []
for dm in datamappers:
    dm_n = {"datamapper": json.loads(dm["datamapper"]), "nodes": json.loads(dm["nodes"]),
            "edges": json.loads(dm["edges"]), "analyze": json.loads(dm["analyze"]), "datasource": dm["datasource"]}
    datamappers_list.append(dm_n)


def generate_identifier(x: str):
    data = x[0]
    d = json.loads(data)
    ds = d["dataSourceName"]
    datamapper = [x["datamapper"] for x in datamappers_list if x["datasource"] == ds][0]["nodes"]
    # dm = self.load_datamapper(ds)["nodes"] if self.DATAMAPPERS is {} else self.DATAMAPPERS[ds]["nodes"]

    elem_type = "edge" if "edge_id" in d else "node"
    if elem_type == "node":
        # prop_key = "ip" if "ip" in d else "userName" if "userName" in d else "emailSubject" if "emailSubject" in d else "hostname" if "hostname" in d else "URL" if "URL" in d else "fileName"
        label = d["node_label"]

        for type_node, mapper in datamapper.items():
            node_type = mapper["maps"]["node_label"].split("default=")[1]
            if label.lower() == node_type.lower():
                prop_key = mapper["constraints"]["unique"]
        prop_val = d[prop_key]

        # try:
        #     prop_val = d[prop_key]
        # except KeyError:
        #     raise ValueError(f"Invalid node found. None of primary keys found in node {d}")
        identifier = f"{label}_{prop_key}_{prop_val}"
    else:
        identifier = f"{d['edge_id']}_{d['edge_label']}"
        print(identifier)
    return identifier


resource_properties = Commons.load_properties(APPLICATION_PROPERTIES)

MAX_MESSAGE_LENGTH = 250 * 1024 * 1024
options = [
    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
]

url = f'{resource_properties["grpc.core.server.host"]}:{resource_properties["grpc.core.server.port"]}'
core_channel = grpc.insecure_channel(url, options=options)
CORE_CLIENT = ServicesToGraphCoreStub(channel=core_channel)


def transform_data_from_spark_dataframe(sdf: DataFrame, case_id):
    sleep(6)
    print("Sleep for 6 sec done")

    nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
    edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

    nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds")))
    edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds")))

    nodes_sdf = nodes_sdf.withColumn("node_size", F.size(nodes_sdf.nodes)).select("case_id", "ds", "nodes", "node_size")
    edges_sdf = edges_sdf.withColumn("edge_size", F.size(edges_sdf.edges)).select("case_id", "ds", "edges", "edge_size")

    # print("oooooooooooooooooooooooooooooooooooooo")
    # print("Before converting to array of maps")
    #
    # nodes_pdf = nodes_sdf.toPandas()
    # edges_pdf = edges_sdf.toPandas()
    # print(nodes_pdf.head(50))
    # print(edges_pdf.head(50))
    # print(nodes_pdf.shape, edges_pdf.shape)
    # print("=========================")
    # print(nodes_pdf[nodes_pdf.node_size >= 1].head(10))
    # # print(merged.filter(merged.node_size >= 1).show(1))
    # print("=========================")
    # print(edges_pdf[edges_pdf.edge_size >= 1].head(15))
    # # print(merged.filter(merged.node_size >= 2).show(2))
    # print("=========================")
    # print(nodes_pdf[nodes_pdf.node_size == 0].shape, edges_pdf[edges_pdf.edge_size == 0].shape)
    # print("pppppppppppppppppppppppppppppppppppppp")

    convertor = F.udf(convert_to_json_from_str, ArrayType(MapType(StringType(), StringType())))
    nodes_sdf = nodes_sdf.withColumn("nodes", convertor("nodes"))
    edges_sdf = edges_sdf.withColumn("edges", convertor("edges"))
    print("converted to  array of maps")

    # merged = nodes_sdf.select("ds", "nodes", "id", "case_id", "node_size"). \
    #     join(edges_sdf.select("edges", "id", "edge_size"), nodes_sdf.id == edges_sdf.id)
    # print("Defined 2 cols of node and edge size")
    # merged_pdf = merged.toPandas()
    #
    # print(merged_pdf.shape)
    # print(merged_pdf.head(50))
    # print("=========================")
    # print(merged_pdf[merged_pdf.node_size >= 1].head(1))
    # # print(merged.filter(merged.node_size >= 1).show(1))
    # print("=========================")
    # print(merged_pdf[merged_pdf.edge_size >= 1].head(1))
    # # print(merged.filter(merged.node_size >= 2).show(2))
    # print("=========================")
    # print(merged_pdf[merged_pdf.node_size == 0].shape, merged_pdf[merged_pdf.edge_size == 0].shape, merged_pdf[(merged_pdf.node_size == 0) | (merged_pdf.edge_size == 0)].shape)
    # nodes_pdf = nodes_sdf.toPandas()
    # edges_pdf = edges_sdf.toPandas()
    # print(nodes_pdf.head(50))
    # print(edges_pdf.head(50))
    # print(nodes_pdf.shape, edges_pdf.shape)
    # print("=========================")
    # print(nodes_pdf[nodes_pdf.node_size >= 1].head(10))
    # # print(merged.filter(merged.node_size >= 1).show(1))
    # print("=========================")
    # print(edges_pdf[edges_pdf.edge_size >= 1].head(15))
    # # print(merged.filter(merged.node_size >= 2).show(2))
    # print("=========================")
    # print(nodes_pdf[nodes_pdf.node_size == 0].shape, edges_pdf[edges_pdf.edge_size == 0].shape)
    # print(merged.filter(merged.node_size == 0).count(), merged.filter(merged.edge_size == 0).count(), merged.filter((merged.node_size == 0) | (merged.edge_size == 0)).toPandas().shape)
    # print(f"Merged df size before filter: {merged_pdf.shape}")

    # print(f"before filter, node size {nodes_sdf.count()}")
    # print(f"before filter, edge size {edges_sdf.count()}")

    # nodes_sdf = nodes_sdf.select("*").withColumn("id", monotonically_increasing_id())
    # edges_sdf = edges_sdf.select("*").withColumn("id", monotonically_increasing_id())
    # print("Generated nodes and edges and defined a id column per row")
    # merged = nodes_sdf.select("ds", "nodes", "id", "case_id"). \
    #     join(edges_sdf.select("edges", "id"), nodes_sdf.id == edges_sdf.id). \
    #     select("ds", "nodes", "edges", "case_id")

    filtered_nodes_sdf = nodes_sdf.filter(nodes_sdf.node_size >= 1)
    filtered_edges_sdf = edges_sdf.filter(edges_sdf.edge_size >= 1)

    # print(f"After filter, before eplosion, node size {filtered_nodes_sdf.count()}")
    # print(f"After filter, before eplosion, edge size {filtered_edges_sdf.count()}")

    exploded_nodes = filtered_nodes_sdf.withColumn("nodes_exploded", F.explode("nodes")).select("case_id", "ds", F.col("nodes_exploded").alias("element"))
    exploded_edges = filtered_edges_sdf.withColumn("edges_exploded", F.explode("edges")).select("case_id", "ds", F.col("edges_exploded").alias("element"))

    # print(f"After explosion, node size {exploded_nodes.count()}")
    # print(f"After explosion, edge size {exploded_edges.count()}")

    list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
    exploded_nodes = exploded_nodes.withColumn("element", list_to_str_udf("element"))
    print("Converted node maps to string")
    # exploded_nodes_pdf = exploded_nodes.toPandas()
    # print(f"Node df after explosion and conversion to str, size is {exploded_nodes_pdf.shape}")
    # exploded_nodes_pdf.to_csv("nodes_sdf_post_str.csv")

    unique_identifier_udf = udf(generate_identifier, StringType())
    exploded_nodes = exploded_nodes.withColumn("identifier", unique_identifier_udf(array("element", "ds")))
    dedup_node_sdf = exploded_nodes.dropDuplicates(['identifier']).select("case_id", "ds", "element")
    # print(f"After dedup, node size {dedup_node_sdf.count()}")
    # print(f"After dedup, edge size {exploded_edges.count()}")

    nodes_sdf = dedup_node_sdf.withColumn("element_type", F.lit("node"))
    edges_sdf = exploded_edges.withColumn("element_type", F.lit("edge"))

    edges_sdf = edges_sdf.withColumn("element", list_to_str_udf("element"))

    print(nodes_sdf.printSchema())
    print("=======")
    print(edges_sdf.printSchema())
    final_sdf = nodes_sdf.union(edges_sdf)
    final_pdf = final_sdf.toPandas()

    print(f"Final node size: {final_pdf[final_pdf.element_type == 'node'].shape}")
    print(f"Final edge size: {final_pdf[final_pdf.element_type == 'edge'].shape}")

    exit(-100)

    valid_sdf = merged.filter((merged.node_size >= 1) | (merged.edge_size >= 1))
    print(valid_sdf.show(50))
    print(f"Merged df before explosion, size is {valid_sdf.count()}")
    print(valid_sdf.printSchema())

    print(valid_sdf.withColumn("nodes_exploded", F.explode("nodes")).select("ds", "nodes_exploded").show(10))
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(valid_sdf.show(10))
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")). \
        select("nodes_exploded", "edges_exploded", "case_id", "ds")
    print(valid_sdf.show(50))
    print(f"Merged df after explosion, size is {valid_sdf.toPandas().shape}")

    valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"))

    nodes_sdf = valid_sdf.select("case_id", "ds", "nodes")
    nodes_pdf = nodes_sdf.toPandas()
    print(f"Node df after explosion, size is {nodes_pdf.shape}")
    nodes_pdf.to_csv("nodes_sdf_pre_dedp.csv")
    edges_sdf = valid_sdf.select("case_id", "ds", "edges")
    print(f"Edge df after explosion, size is {nodes_pdf.shape}")

    list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
    nodes_sdf = nodes_sdf.withColumn("nodes", list_to_str_udf("nodes"))
    print("Converted node maps to string")
    nodes_pdf = nodes_sdf.toPandas()
    print(f"Node df after explosion and conversion to str, size is {nodes_pdf.shape}")
    nodes_pdf.to_csv("nodes_sdf_post_str.csv")

    unique_identifier_udf = udf(generate_identifier, StringType())
    nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf(array("nodes", "ds")))
    dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])

    print(f"Merged df after deduplication, size is {dedup_node_sdf.toPandas().shape}")

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    status = graphdb_pb2.CaseLoadingStatus(status="Nodes deduplicated (Transformation)", caseId=case_id, processingTime=procTime)
    CORE_CLIENT.UpdateCaseLoadingStatus(status)

    nodes_sdf = dedup_node_sdf.withColumn("element_type", F.lit("node"))
    edges_sdf = edges_sdf.withColumn("element_type", F.lit("edge"))
    print(f"Edges df size: {edges_sdf.toPandas().shape}")

    nodes_sdf = nodes_sdf.select("case_id", "ds", "element_type", F.col("nodes").alias("element"))
    nodes_sdf = nodes_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    edges_sdf = edges_sdf.select("case_id", "ds", "element_type", F.col("edges").alias("element"))
    edges_sdf = edges_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    edges_sdf = edges_sdf.withColumn("element", list_to_str_udf("element"))
    print("Converted edge maps to string")
    final_sdf = nodes_sdf.union(edges_sdf)

    output_table = credentials.additionalParameters["src_transformed_tbl"]
    options = {
        "sfUrl": credentials.url,
        "sfAccount": credentials.account,
        "sfUser": credentials.user,
        "sfPassword": credentials.password,
        "sfDatabase": credentials.database,
        "sfSchema": credentials.schema,
        "sfWarehouse": credentials.warehouse
    }
    # options['sfDatabase'] = "snowflake_graph_test"
    # options["sfSchema"] = "graph_test",
    print(f"Writing data to snowflake table {output_table} under DB: {options['sfDatabase']} and schema: {options['sfSchema']} @ {dt.datetime.now()}")

    print(f"Merged df before writing to DB, size is {final_sdf.toPandas().shape}")
    final_sdf = final_sdf.select("element", "element_type", "case_id", "ds", "processing_dttm")

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    status = graphdb_pb2.CaseLoadingStatus(status=f"Loading transformed data to {output_table}", caseId=case_id, processingTime=procTime)
    CORE_CLIENT.UpdateCaseLoadingStatus(status)

    final_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
    print(f"Saved data to snowflake table @ {dt.datetime.now()}")

    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
    status = graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to {output_table}", caseId=case_id, processingTime=procTime)
    CORE_CLIENT.UpdateCaseLoadingStatus(status)

    params = graphdb_pb2.ProcedureParams()
    # params.procedure = "SP_GENERATE_NODE_AND_EDGE_IDS"
    params.procedure = credentials.additionalParameters["node_edge_id_generator_stored_procedure"]
    order = credentials.additionalParameters["node_edge_id_generator_stored_procedure_order"].split(",")
    params.order[:] = order

    print(params)
    print("xxxxxx")
    params.parameters["CASE_ID_VAL"] = case_id
    params.parameters["SRC_TRANSFORMED_TBL"] = credentials.additionalParameters["src_transformed_tbl"]
    params.parameters["TARGET_TRANSFORMED_TBL"] = credentials.additionalParameters["target_transformed_tbl"]
    print(params)
    CORE_CLIENT.ExecuteStoredProcedure(params)
    print("Updated node_ids and edge_ids for transformed data")

    print("Transformation completed")
    print("Data load started")


if __name__ == '__main__':
    spark = SparkSession \
        .builder.appName("test"). \
        config("spark.app.id", 123). \
        config("spark.driver.memory", "15g"). \
        getOrCreate()
    # sc = spark.sparkContext
    # sc.setLogLevel("ERROR")

    case_id = '160374_sstech_7756_480891942978'
    table = "extracted_streaming_graph_data_1"

    print("Going to start transformation")

    print("Reading in snowflake table")
    st = dt.datetime.now()

    dbi = graphdb_pb2.DataBaseIdentifier(database="tenant5", schema="enriched", caller="python")
    credentials = CORE_CLIENT.GetSnowFlakeCredentials(dbi)
    enriched_options = {
        "sfUrl": credentials.url,
        "sfAccount": credentials.account,
        "sfUser": credentials.user,
        "sfPassword": credentials.password,
        "sfDatabase": credentials.database,
        "sfSchema": credentials.schema,
        "sfWarehouse": credentials.warehouse
    }

    sdf = spark.read.format("snowflake").options(**enriched_options).option("query", f"select data, ds, case_id from {table} where case_id = '{case_id}'").load()
    sdf = sdf.repartition(25)
    print("Read in data from snowflake and repartitioned")
    transform_data_from_spark_dataframe(sdf, case_id)
