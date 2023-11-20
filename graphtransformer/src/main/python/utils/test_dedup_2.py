import json, os
from process.IncomingDataToGraphTransformer import IncomingDataToGraphTransformer
from pyspark.sql import *
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType, MapType
import pandas as pd
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

DATAMAPPERS = {}


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


def convert_to_json_from_str(x):
    print(x, type(x))
    return [json.loads(a) for a in x]


def load_datamapper(ds):
    from utils.constants import Commons, APPLICATION_PROPERTIES
    properties = Commons.load_properties(APPLICATION_PROPERTIES)
    datamapper_file = properties[f"graph.{ds}.datamapper"]
    dm = json.load(open(os.path.abspath(properties["resource.path"] + datamapper_file))) if datamapper_file != "" else {}

    if ds not in DATAMAPPERS:
        DATAMAPPERS[ds] = dm
    return dm


def generate_identifier(x: str):
    data = x[0]
    d = json.loads(data)
    ds = d["dataSourceName"]
    datamapper = [x["datamapper"] for x in datamappers_dict if x["datasource"] == ds][0]["nodes"]

    label = d["node_label"]
    for type_node, mapper in datamapper.items():
        node_type = mapper["maps"]["node_label"].split("default=")[1]
        if label.lower() == node_type.lower():
            prop_key = mapper["constraints"]["unique"]
            prop_val = d[prop_key]
    identifier = f"{label}_{prop_key}_{prop_val}"
    return identifier


def get_unique_label_for_ds_and_label(node, ds):
    label = node["node_label"]
    # dm = load_datamapper(ds)["nodes"] if ds not in DATAMAPPERS else DATAMAPPERS[ds]["nodes"]
    dm = [x["datamapper"] for x in datamappers_dict if x["datasource"] == ds][0]["nodes"]
    # print(datamapper)
    for type_node, mapper in dm.items():
        node_type = mapper["maps"]["node_label"].split("default=")[1]
        if label.lower() == node_type.lower():
            return mapper["constraints"]["unique"]


if __name__ == '__main__':
    extracted_data = json.load(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\incoming.json"))
    # unfiltered_data = json.load(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\unfiltered.json"))
    # unexploded_data = json.load(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\unexploded.json"))

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
    print(f"Using pure python, the nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")
    print(f"Total undeducted edge count {convertor.TOT_EDGES}")

    nodes = graph["nodes"]
    process_nodes = [x for x in nodes if x["node_label"] == "process"]
    import pprint
    pprint.pprint(process_nodes)
    exit(-1)

    skipped_overall_tot = 0
    for ds, values in convertor.EMPTY_EDGES.items():
        print(f"ds: {ds} and {values.keys()}")
        for key in values.keys():
            print(len(convertor.EMPTY_EDGES[ds][key]))
            json.dump(convertor.EMPTY_EDGES[ds][key], open(f"D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\{ds}_{key}_empty_edges_tracker.json", "w+"), indent=2)
            print(f"Saved {key} of ds {ds} empty edge json of size {len(convertor.EMPTY_EDGES[ds][key])} for verification at '{ds}_{key}_empty_edges_tracker.json'")
            skipped_overall_tot += len(convertor.EMPTY_EDGES[ds][key])

    print(len(extracted_data), len(unfiltered_data), len(unexploded_data))

    local_unexploded = []
    unexploded_with_size = []
    others_1 = []
    others_2 = []
    for data in unfiltered_data:
        nodes = [json.loads(x) for x in data["nodes"]]
        edges = [json.loads(x) for x in data["edges"]]
        elem = {
            "nodes": nodes, "edges": edges, "ds": data["ds"], "case_id": data["case_id"]
        }
        if len(data["nodes"]) > 0 or len(data["edges"]) > 0:
            local_unexploded.append(elem)
        else:
            others_1.append(elem)

        if data["node_size"] > 0 or data["edge_size"] > 0:
            unexploded_with_size.append(data)
        else:
            others_2.append(data)
        if data["node_size"] != len(data["nodes"]):
            print(f"Mismatch in node sizes: {data}")
        if data["edge_size"] != len(data["edges"]):
            print(f"Mismatch in edge sizes: {data}")

    print(len(local_unexploded), len(unexploded_with_size))
    assert len(local_unexploded) == len(unexploded_with_size) == len(unexploded_data)

    exploded_nodes = []
    exploded_edges = []
    i = 1
    for data in local_unexploded:
        for node in data["nodes"]:
            exploded_nodes.append(node)
        for edge in data["edges"]:
            # print(i, data)
            exploded_edges.append(edge)
            i += 1

    print(f"Exploded nodes: {len(exploded_nodes)}, edges: {len(exploded_edges)}, tot: {len(exploded_nodes) + len(exploded_edges)}")
    exit(-1)

    spark = SparkSession \
        .builder.appName("test"). \
        config("spark.app.id", 123). \
        config("spark.driver.memory", "15g"). \
        getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    sdf = spark.createDataFrame(unexploded_data, ["case_id", "ds", "edge_size", "edges", "node_size", "nodes"])
    print(sdf.printSchema())
    # print(sdf.show(10))
    print("Created spark dataframe from unexploded data")
    convertor = F.udf(convert_to_json_from_str, ArrayType(MapType(StringType(), StringType())))
    sdf = sdf.withColumn("nodes", convertor("nodes")).withColumn("edges", convertor("edges"))
    print(f"Before explosion, count of df: {sdf.count()}")

    # print(sdf.filter(F.col("edge_size") > 1).show(50))
    # print("====================")
    # print(sdf.filter(F.col("node_size") > 1).show(50))
    nodes_sdf = sdf.select("nodes", "case_id", "ds", "node_size").withColumn("nodes_exploded", F.explode("nodes"))
    edges_sdf = sdf.select("edges", "case_id", "ds", "edge_size").withColumn("edges_exploded", F.explode("edges"))

    # print(f"Node count: {nodes_sdf.count()}")
    # print(f"Edge count: {edges_sdf.count()}")

    # print(nodes_sdf.select("nodes_exploded", "node_size").show(200))
    # print("++++++++++++++++++++++++")
    # print(edges_sdf.select("edges_exploded", "edge_size").show(200))

    final_sdf = nodes_sdf.union(edges_sdf)
    # print(f"Final df count after union of dfs {final_sdf.count()}")

    # valid_sdf = sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")). \
    #     select("nodes_exploded", "edges_exploded", "case_id", "ds")
    # print(f"Count of exploded dataframe is {valid_sdf.count()}")

    # sums = sdf.agg(sum("node_size").as_("node_sum"), sum("edge_size").as_("edge_sum")).first()
    # print(sums)
    # nodes_sdf.withColumn("node_size", F.expr("CAST(node_size AS INTEGER)"))
    # edges_sdf.withColumn("edge_size", F.expr("CAST(edge_size AS INTEGER)"))
    # print(f"Sum of nodes: {nodes_sdf.toPandas()['node_size'].sum()}")
    # print(f"Sum of edges: {edges_sdf.toPandas()['edge_size'].sum()}")

    nodes_sdf.toPandas().to_csv("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\nodes_ind.csv")
    edges_sdf.toPandas().to_csv("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\edges_ind.csv")

    nodes = nodes_sdf.toPandas().to_json(orient="records")
    nodes_dict = []
    nodes_dict = json.loads(nodes)
    nodes_dict = [x["nodes_exploded"] for x in nodes_dict]
    print(nodes_dict[:10])
    # for n in nodes:
    #     print(n, type(n))
    #     nodes_dict.append(json.loads(n))

    nodes_dedup = {}
    for node in nodes_dict:
        prop = get_unique_label_for_ds_and_label(node, node["dataSourceName"])
        unique_val = node[prop]

        if isinstance(unique_val, str):
            if unique_val not in nodes_dedup:
                nodes_dedup[unique_val] = node
        else:
            assert len(unique_val) == 1
            if unique_val[0] not in nodes_dedup:
                nodes_dedup[unique_val[0]] = node
    nodes_final = list(nodes_dedup.values())
    print(f"Nodes len after dedup using pure python: {len(nodes_final)}")

    list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
    nodes_sdf = nodes_sdf.withColumn("nodes_exploded", list_to_str_udf("nodes_exploded"))
    print("Converted to string")

    unique_identifier_udf = F.udf(generate_identifier, StringType())
    nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf(F.array("nodes_exploded", "ds")))
    dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])
    print(dedup_node_sdf.show(5))
    print(f"Nodes len after dedup using spark: {dedup_node_sdf.count()}")
