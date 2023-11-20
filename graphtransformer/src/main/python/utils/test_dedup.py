import json
from process.IncomingDataToGraphTransformer import IncomingDataToGraphTransformer
from pyspark.sql import *
from pyspark.sql.functions import udf, monotonically_increasing_id, array
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType
from utils.use_databricks import apply_node_transformation_to_records, apply_edge_transformation_to_records, conn, create_engine, options
import pandas as pd
import uuid
import datetime as dt
import random
import sys

engine = create_engine(conn)
datamappers = json.loads(pd.read_sql_table("datamappers", engine).to_json(orient='records'))
datamappers_list = []
for dm in datamappers:
    dm_n = {"datamapper": json.loads(dm["datamapper"]), "nodes": json.loads(dm["nodes"]),
            "edges": json.loads(dm["edges"]), "analyze": json.loads(dm["analyze"]), "datasource": dm["datasource"]}
    datamappers_list.append(dm_n)


def deduplicate_using_pure_python(data):
    windows = []
    msexchange = []
    sysmon = []
    wgtraffic = []
    sepc = []

    print("Read file")

    for row in data:
        ds = row[1]
        if ds == "windows":
            windows.append(json.loads(row[0]))
        elif ds == "msexchange":
            msexchange.append(json.loads(row[0]))
        elif ds == "sysmon":
            sysmon.append(json.loads(row[0]))
        elif ds == "sepc":
            sepc.append(json.loads(row[0]))
        else:
            wgtraffic.append(json.loads(row[0]))

    print(f"Aggregated data with lengths: Windows: {len(windows)} MsExchange: {len(msexchange)} SysMon: {len(sysmon)} "
          f"SEPC: {len(sepc)} WgTraffic: {len(wgtraffic)}")

    data = {
        "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
        "networkRecords": wgtraffic, "sepcRecords": sepc
    }

    convertor = IncomingDataToGraphTransformer(data)
    graph = convertor.convert()


def deduplicate_using_pyspark(data):
    spark = SparkSession \
        .builder.appName("test"). \
        config("spark.app.id", 123). \
        config("spark.driver.memory", "15g"). \
        getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    sdf = spark.createDataFrame(data, ["data", "ds", "case_id"])
    sdf = sdf.repartition(50)

    sdf = sdf.select("*").withColumn("row_id", monotonically_increasing_id())

    nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
    edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

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
    #
    # print(f"Number of records before explostion before filter: {merged.count()}")

    valid_sdf = merged.filter((merged.node_size >= 1) | (merged.edge_size >= 1))
    # print(f"Number of records before explostion after filter: {valid_sdf.count()}")

    valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")).select("nodes_exploded", "edges_exploded", "case_id", "ds", "node_row_id", "edge_row_id")
    valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"), "node_row_id", "edge_row_id")

    # print(f"Number of records after explostion: {valid_sdf.count()}")

    # valid_sdf.toPandas().to_json(orient="records", path_or_buf=open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\main\\resources\\dumps\\filtered_exploded_sdf_1.json", "w+"), indent=1)
    # print("Saved to json file so that I can verify later that the deduplication worked correctly")

    nodes_sdf = valid_sdf.select("case_id", "ds", "nodes", F.col("node_row_id").alias("row_id"))
    edges_sdf = valid_sdf.select("case_id", "ds", "edges", F.col("edge_row_id").alias("row_id"))

    # print(f"Number of nodes before dedup: {nodes_sdf.count()}")
    # print(f"Number of edges before dedup: {edges_sdf.count()}")

    # nodes_dedup_by_properties_sdf = nodes_sdf.drop_duplicates(["nodes"])
    # edges_dedup_by_properties_sdf = edges_sdf.drop_duplicates(["edges"])
    #
    # print(f"Number of nodes after dedup by properties: {nodes_dedup_by_properties_sdf.count()}")
    # print(f"Number of edges after dedup by properties: {edges_dedup_by_properties_sdf.count()}")

    unique_identifier_udf = udf(generate_identifier, StringType())

    nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf(array("nodes", "ds")))
    # edges_sdf = edges_sdf.withColumn("identifier", unique_identifier_udf(array("edges", "ds")))

    dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])
    # dedup_edge_sdf = edges_sdf.dropDuplicates(['identifier'])

    # print(f"Number of nodes after dedup using custom identifier (label_prop_value): {dedup_node_sdf.count()}")
    # print(f"Columns in nodes df: {dedup_node_sdf.schema.names} and edges df: {edges_sdf.schema.names}")
    nodes_sdf = dedup_node_sdf.select("nodes", "ds", "case_id", F.col("row_id").alias("node_id"))
    nodes_sdf = nodes_sdf.withColumn("node_id", monotonically_increasing_id())

    edges_sdf = edges_sdf.select("edges", "ds", "case_id")
    edges_sdf = edges_sdf.withColumn("edge_id", monotonically_increasing_id())

    nodes_sdf = nodes_sdf.withColumn("element", F.lit("node"))
    edges_sdf = edges_sdf.withColumn("element", F.lit("edge"))

    # uuidUdf = udf(lambda x: str(uuid.uuid3(uuid.NAMESPACE_DNS, str(x * dt.datetime.now().timestamp() * 1000))), StringType())
    # edges_sdf = edges_sdf.withColumn("edge_id", uuidUdf("row_id"))

    # print(nodes_sdf.show(5))
    # print(edges_sdf.show(5))

    # unique_node_ids = [i.node_id for i in nodes_sdf.select('node_id').distinct().collect()]
    # unique_edge_ids = [i.edge_id for i in edges_sdf.select('edge_id').distinct().collect()]
    # print(f"Number of rows in nodes df: {nodes_sdf.count()} and unique node ids: {len(unique_node_ids)} after recreating mono increasing ids")
    # print(f"Number of rows in edges df: {edges_sdf.count()} and unique edge ids: {len(unique_edge_ids)} after recreating mono increasing ids")

    node_id_updater = udf(update_node_id, StringType())
    edge_id_updater = udf(update_edge_id, StringType())

    nodes_sdf = nodes_sdf.withColumn("nodes", node_id_updater(array("nodes", "node_id")))
    edges_sdf = edges_sdf.withColumn("edges", edge_id_updater(array("edges", "edge_id")))

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

    nodes_pdf = final_sdf.filter(final_sdf.element_type == 'node').toPandas()
    nodes_json = nodes_pdf.to_json(orient="records")
    print(type(nodes_json))
    print(json.loads(nodes_json)[:10])
    print("======")
    print(json.loads(nodes_json)[0]["element"])
    print(type(json.loads(nodes_json)[0]["element"]))
    print(json.loads(json.loads(nodes_json)[0]["element"]))
    # edges_sdf = final_sdf.filter(final_sdf.element_type == 'edge')

    # print("Finding dups")
    # print(nodes_sdf.groupBy("element_id").count().select("element_id", F.col("count")).filter("`count` > 1").sort(F.col("count").desc()).show(25))
    # print(50*"=")
    # print(edges_sdf.groupBy("element_id").count().select("element_id", F.col("count")).filter("`count` > 1").sort(F.col("count").desc()).show(25))
    # print(50*"=")
    # print(f"Number of nodes: {nodes_sdf.count()}")
    # print(f"Number of edges: {edges_sdf.count()}")

    final_sdf = final_sdf.select("element", "element_type", "case_id", "ds", "processing_dttm")
    print(final_sdf.show(10))
    final_sdf.write.format("snowflake").options(**options).option("dbtable", "transformed_graph_data").mode("append").save()

    # print(f"Number of edges after dedup (id_label): {dedup_edge_sdf.count()}")
    # Before explosion before filter 244578 / 244578
    # Before explosion after filter 178756 / 176745
    # After explosion 197270 / 179680
    # EDGES: 208834 -> 95061 / 202050 -> 89559
    # NODES: 218563 -> 2053 / 208349 -> 2209

    # Using file and dedup in python not spark
    # Before deduplicating, num nodes: 214741 and num edges: 214741
    # After deduplicating, num nodes: 2167 and num edges: 97008

    #
    # nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf("nodes"))
    # edges_sdf = edges_sdf.withColumn("identifier", unique_identifier_udf("edges"))

    # dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])
    # dedup_edge_sdf = edges_sdf.dropDuplicates(['identifier'])
    #

    return


def update_node_id(x: list):
    node_str = x[0]
    row_id = x[1]

    node = json.loads(node_str)
    node["node_id"] = row_id
    return json.dumps(node)


def generate_node_id(x: list):
    node_str = x[0]
    row_id = x[1]

    mills_since_epoch = dt.datetime.now().timestamp() * 1000
    random.seed(mills_since_epoch)
    node_id = int(random.randint(0, sys.maxsize) + mills_since_epoch)
    node_id += int(row_id)

    node = json.loads(node_str)
    node["node_id"] = node_id
    return row_id


def update_edge_id(x: list):
    edge_str = x[0]
    row_id = x[1]
    edge = json.loads(edge_str)

    mills_since_epoch = dt.datetime.now().timestamp() * 1000
    mills_since_epoch *= int(row_id)

    random.seed(mills_since_epoch)
    edge_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(mills_since_epoch)))

    edge_id = f"{row_id}-{mills_since_epoch}-{edge_uuid}"
    edge["edge_id"] = edge_id

    return json.dumps(edge)


def generate_edge_id(x: list):
    edge_str = x[0]
    row_id = x[1]
    edge = json.loads(edge_str)

    mills_since_epoch = dt.datetime.now().timestamp() * 1000
    mills_since_epoch *= int(row_id)

    random.seed(mills_since_epoch)
    edge_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(mills_since_epoch)))

    edge_id = f"{row_id}-{mills_since_epoch}-{edge_uuid}"
    return edge_id


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


def get_unique_label_for_ds_and_label(node, ds):
    label = node["node_label"]
    dm = [x["datamapper"] for x in datamappers_list if x["datasource"] == ds][0]["nodes"]
    for type_node, mapper in dm.items():
        node_type = mapper["maps"]["node_label"].split("default=")[1]
        if label.lower() == node_type.lower():
            return mapper["constraints"]["unique"]


def deduplicate_graph(graph):
    nodes_global = {}
    edges_global = {}
    nodes = graph["nodes"]
    edges = graph["edges"]

    for node in nodes:
        ds = node["dataSourceName"]
        unique_prop = get_unique_label_for_ds_and_label(node, ds)
        unique_val = node[unique_prop]

        if isinstance(unique_val, str):
            if unique_val not in nodes_global:
                nodes_global[unique_val] = node
        else:
            assert len(unique_val) == 1
            if unique_val[0] not in nodes_global:
                nodes_global[unique_val[0]] = node

    for edge in edges:
        edge_id = edge["edge_id"]
        if edge_id not in edges_global:
            edges_global[edge_id] = edge

    return {"nodes": list(nodes_global.values()), "edges": list(edges_global.values())}


if __name__ == '__main__':
    # f = open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\main\\resources\\dumps\\dummy.json")
    # data = json.load(f)
    #
    # f_inter = open("D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\graphtransformer\\src\main\\resources\\dumps\\filtered_exploded_sdf.json")
    # data_inter = json.load(f_inter)

    extracted_data = json.load(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\incoming.json"))
    final_extracted_data = []

    windows = []
    msexchange = []
    sysmon = []
    wgtraffic = []
    sepc = []
    for row in extracted_data:
        if row["DS"] == "watchguard":
            wgtraffic.append(json.loads(row["DATA"]))
        elif row["DS"] == "windows":
            windows.append(json.loads(row["DATA"]))
        elif row["DS"] == "msexchange":
            msexchange.append(json.loads(row["DATA"]))
        elif row["DS"] == "sysmon":
            sysmon.append(json.loads(row["DATA"]))
        else:
            sepc.append(json.loads(row["DATA"]))

    data = {
        "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
        "networkRecords": wgtraffic, "sepcRecords": sepc
    }

    convertor = IncomingDataToGraphTransformer(data)
    graph = convertor.convert()

    json.dump(graph, open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\graph.json", "w+"), indent=1)

    # nodes = []
    # edges = []
    # for row in data_inter:
    #     nodes.append(json.loads(row["nodes"]))
    #     edges.append(json.loads(row["edges"]))
    #
    # graph = {
    #     "nodes": nodes,
    #     "edges": edges
    # }

    print(f"after conversion, num nodes: {len(graph['nodes'])} and num edges: {len(graph['edges'])}")
    # dedup_graph = deduplicate_graph(graph)
    # print(f"After deduplicating, num nodes: {len(dedup_graph['nodes'])} and num edges: {len(dedup_graph['edges'])}")
