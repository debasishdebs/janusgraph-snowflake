import importlib
import pandas
import json
import os
import uuid
import snowflake.connector
# snowflake.connector.paramstyle = 'qmark'
import datetime as dt
from sqlalchemy.types import Variant, JSON
from sqlalchemy_utils.types.json import JSONType
from snowflake.connector.pandas_tools import pd_writer
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.sql import text

COUNTER = 0


def find_node_by_prop_in_nodes(custom_nodes, prop, val):
    for i in range(len(custom_nodes)):
        node = custom_nodes[i]
        if prop not in node["properties"]:
            continue
        if node["properties"][prop] == val:
            return node, i
    return {}, -1


def are_two_nodes_same(curr_node, oth_node):
    return curr_node["node_id"] == oth_node["node_id"]


def create_node_variant_cols(nodes, edges):

    for node in nodes:
        cs = ["outEdges", "inEdges", "bothEdges", "outVertices", "inVertices", "otherVertices"]
        for c in cs:
            node[c] = []

    new_nodes = []
    nodes_added = []
    all_nodes = nodes.copy()
    for node in nodes:
        outvertices = {}
        invertices = {}
        bothvertices = {}
        outedges = {}
        inedges = {}
        bothedges = {}

        for edge in edges:
            left_prop = edge["srcVertex"]["property_key"]
            left_val = edge["srcVertex"]["value"].replace("$", "").lower()

            right_prop = edge["dstVertex"]["property_key"]
            right_val = edge["dstVertex"]["value"].replace("$", "").lower()

            if "acme\\\\" in left_val:
                left_val = left_val.replace("acme\\\\", "")
            if "acme\\" in left_val:
                left_val = left_val.replace("acme\\", "")
            if "@acme.com" in left_val:
                left_val = left_val.replace("@acme.com", "")
            if "acme\\\\" in right_val:
                right_val = right_val.replace("acme\\\\", "")
            if "acme\\" in right_val:
                right_val = right_val.replace("acme\\", "")
            if "@acme.com" in right_val:
                right_val = right_val.replace("@acme.com", "")

            dst_node, d_idx = find_node_by_prop_in_nodes(all_nodes, right_prop, right_val)
            src_node, s_idx = find_node_by_prop_in_nodes(all_nodes, left_prop, left_val)

            if s_idx is not -1:
                # src_value = src_node["properties"]["userName"] if "userName" in src_node["properties"] else src_node["properties"]["ip"] if "ip" in src_node["properties"] \
                #     else src_node["properties"]["hostname"] if "hostname" in src_node["properties"] else src_node["properties"]["emailSubject"]
                # src_prop = "userName" if "userName" in src_node["properties"] else "ip" if "ip" in src_node["properties"] \
                #     else "hostname" if "hostname" in src_node["properties"] else "emailSubject" if "emailSubject" in src_node["properties"] else "NA"

                if are_two_nodes_same(node, src_node):
                    node_to_add = edge["dstVertex"]
                    try:
                        node_to_add["node_id"] = dst_node["node_id"]
                    except KeyError:
                        print(f"For dst node {dst_node}, i.e. prop: {right_prop} = val: {right_val}, node_id not found")
                        node_to_add["node_id"] = -1

                    eid = edge["edge_id"]
                    nid = node_to_add["node_id"]
                    outedges[eid] = edge
                    bothedges[eid] = edge
                    outvertices[nid] = node_to_add
                    bothvertices[nid] = node_to_add
                    #
                    # outedges.append(edge)
                    # bothedges.append(edge)
                    # outvertices.append(node_to_add)
                    # bothvertices.append(node_to_add)

                # if src_value not in nodes_added:
                #     src_node["outEdges"].append(edge)
                #     src_node["bothEdges"].append(edge)
                #     src_node["outVertices"].append(edge["dstVertex"])
                #     src_node["otherVertices"].append(edge["dstVertex"])
                #
                #     new_nodes.append(src_node)
                #     nodes_added.append(src_value)
                # else:
                #     added_src_node, idx = find_node_by_prop_in_nodes(new_nodes, src_prop, src_value)
                #     if idx != -1:
                #         added_src_node["outEdges"].append(edge)
                #         added_src_node["bothEdges"].append(edge)
                #         added_src_node["outVertices"].append(edge["dstVertex"])
                #         added_src_node["otherVertices"].append(edge["dstVertex"])
                #
                #         new_nodes.pop(idx)
                #         new_nodes.append(added_src_node)
                #     else:
                #         print(f"Strange the newly added node (SRC) prop: {src_prop} and val: {src_value} not found ")
            # else:
            #     print(f"Source node ({src_node}) not found for edge {edge} and prop {left_prop} and val {left_val}")

            if d_idx != -1:
                # dst_value = dst_node["properties"]["userName"] if "userName" in dst_node["properties"] else dst_node["properties"]["ip"] if "ip" in dst_node["properties"] \
                #     else dst_node["properties"]["hostname"] if "hostname" in dst_node["properties"] else dst_node["properties"]["emailSubject"]
                # dst_prop = "userName" if "userName" in dst_node["properties"] else "ip" if "ip" in dst_node["properties"] \
                #     else "hostname" if "hostname" in dst_node["properties"] else "emailSubject"

                if are_two_nodes_same(node, dst_node):
                    node_to_add = edge["srcVertex"]
                    try:
                        node_to_add["node_id"] = src_node["node_id"]
                    except KeyError:
                        print(f"For src node {src_node}, i.e. prop: {left_prop} = val: {left_val}, node_id not found")
                        node_to_add["node_id"] = -1

                    eid = edge["edge_id"]
                    nid = node_to_add["node_id"]
                    inedges[eid] = edge
                    bothedges[eid] = edge
                    invertices[nid] = node_to_add
                    bothvertices[nid] = node_to_add

                    # inedges.append(edge)
                    # bothedges.append(edge)
                    # invertices.append(node_to_add)
                    # bothvertices.append(node_to_add)
                #
                # if dst_value not in nodes_added:
                #     dst_node["inEdges"].append(edge)
                #     dst_node["bothEdges"].append(edge)
                #     dst_node["inVertices"].append(edge["srcVertex"])
                #     dst_node["otherVertices"].append(edge["srcVertex"])
                #
                #     new_nodes.append(dst_node)
                #     nodes_added.append(dst_value)
                # else:
                #     added_dst_node, idx = find_node_by_prop_in_nodes(new_nodes, dst_prop, dst_value)
                #
                #     if idx != -1:
                #         added_dst_node["outEdges"].append(edge)
                #         added_dst_node["bothEdges"].append(edge)
                #         added_dst_node["outVertices"].append(edge["srcVertex"])
                #         added_dst_node["otherVertices"].append(edge["srcVertex"])
                #
                #         new_nodes.pop(idx)
                #         new_nodes.append(added_dst_node)
                #     else:
                #         print(f"Strange the newly added node (DST) prop: {dst_prop} and val: {dst_value} not found "
                #               f"")
            # else:
            #     print(f"Destination node ({dst_node}) not found for edge {edge} and prop {right_prop} and val {right_val}")

        node["outVertices"] = list(outvertices.values())
        node["inVertices"] = list(invertices.values())
        node["otherVertices"] = list(bothvertices.values())
        node["outEdges"] = list(outedges.values())
        node["inEdges"] = list(inedges.values())
        node["bothEdges"] = list(bothedges.values())

        try:
            value = node["properties"]["userName"] if "userName" in node["properties"] \
                else node["properties"]["ip"] if "ip" in node["properties"] \
                else node["properties"]["hostname"] if "hostname" in node["properties"] \
                else node["properties"]["emailSubject"]
        except KeyError:
            value = None
            print("node is strange one, ignoring", {k: v for k, v in node.items() if k in ["node_id", "label", "properties"]})
            continue

        if value not in nodes_added:
            new_nodes.append(node)
            nodes_added.append(value)
            #
            #
            # try:
            #     if node["properties"][left_prop].replace("$", "") == left_val:
            #         # print(f"{node} is srcVertex for {edge}")
            #
            #         node["outEdges"].append(edge)
            #         node["bothEdges"].append(edge)
            #         node["outVertices"].append(edge["right"])
            #         node["otherVertices"].append(edge["right"])
            #
            #         right_prop = edge["dstVertex"]["property_key"]
            #         right_val = edge["dstVertex"]["value"].replace("$", "")
            #         dst_node = find_node_by_prop_val(right_prop, right_val)
            #         dst_node["inEdges"].append(edge)
            #         dst_node["bothEdges"].append(edge)
            #         dst_node["inVertices"].append(edge["left"])
            #         dst_node["otherVertices"].append(edge["left"])
            #         continue
            # except KeyError:
            #     continue
    #
    # for node in nodes:
    #     for edge in edges:
    #         right_prop = edge["dstVertex"]["property_key"]
    #         right_val = edge["dstVertex"]["value"].replace("$", "")
    #
    #         try:
    #             if node["properties"][right_prop].replace("$", "") == right_val:
    #                 print(f"{node} is dstVertex for {edge}")
    #
    #                 node["inEdges"].append(edge)
    #                 node["bothEdges"].append(edge)
    #                 node["inVertices"].append(edge["left"])
    #                 node["otherVertices"].append(edge["left"])
    #                 continue
    #         except KeyError:
    #             continue
        #
        # for edge in edges:
        #     left_prop = edge["srcVertex"]["property_key"]
        #     left_val = edge["srcVertex"]["value"].replace("$", "")
        #     right_prop = edge["dstVertex"]["property_key"]
        #     right_val = edge["dstVertex"]["value"].replace("$", "")
        #
        #     try:
        #         if node["properties"][left_prop].replace("$", "") == left_val:
        #             # print(f"{node} is srcVertex for {edge}")
        #
        #             node["outEdges"].append(edge)
        #             node["bothEdges"].append(edge)
        #             node["outVertices"].append(edge["right"])
        #             node["otherVertices"].append(edge["right"])
        #             continue
        #         if node["properties"][right_prop].replace("$", "") == right_val:
        #             # print(f"{node} is dstVertex for {edge}")
        #
        #             node["inEdges"].append(edge)
        #             node["bothEdges"].append(edge)
        #             node["inVertices"].append(edge["left"])
        #             node["otherVertices"].append(edge["left"])
        #             continue
        #     except KeyError:
        #         continue

    return pandas.DataFrame(new_nodes)


def create_nodes_data_frame(nodes, edges, node_mapper, row_id = None):
    row_id = 0 if row_id is None else row_id

    rows = []
    nodes_added = []
    for node in nodes:
        for n in node:
            cols = n.keys()
            new_node = {
                "node_id": row_id,
                "label": n["node_label"],
                "properties": {}
            }

            if "userName" not in n and "ip" not in n and "hostname" not in n and "emailSubject" not in n:
                print(f"Primary properties not found in node {n} skipping")
                continue
            if "userName" in n and n['userName'] == 'None':
                print(f"userName properties not found in node {n} skipping if {n['userName']} and {n['userName'] is None} and {n['userName'] == 'None'}")
                continue
            if "ip" in n and n['ip'] == 'None':
                print(f"IP properties not found in node {n} skipping if {n['ip']}")
                continue
            if "hostname" in n and n['hostname'] == 'None':
                print(f"hostname properties not found in node {n} skipping if {n['hostname']}")
                continue
            if "emailSubject" in n and n['emailSubject'] == 'None':
                print(f"emailSubject properties not found in node {n} skipping if {n['emailSubject']}")
                continue

            for c in cols:
                if c not in ["node_label"]:
                    if isinstance(n[c], str):
                        new_node["properties"][c] = n[c].replace("$", "").lower()
                    elif isinstance(n[c], list):
                        assert len(n[c]) == 1
                        val = n[c][0]
                        new_node["properties"][c] = val.replace("$", "").lower()

                    if c == "userName":
                        if "acme\\\\" in new_node["properties"][c]:
                            new_node["properties"][c] = new_node["properties"][c].replace("acme\\\\", "")
                        if "acme\\" in new_node["properties"][c]:
                            new_node["properties"][c] = new_node["properties"][c].replace("acme\\", "")
                        if "@acme.com" in new_node["properties"][c]:
                            new_node["properties"][c] = new_node["properties"][c].replace("@acme.com", "")
                    # elif isinstance(n[c], list):
                    #     val = n[c][0]
                    #     new_node["properties"][c] = val.replace("$", "").lower()
                    #     if c == "userName":
                    #         if "acme\\\\" in new_node["properties"][c]:
                    #             new_node["properties"][c] = new_node["properties"][c].replace("acme\\\\", "")
                    #         if "acme\\" in new_node["properties"][c]:
                    #             new_node["properties"][c] = new_node["properties"][c].replace("acme\\", "")
                    #         if "@acme.com" in new_node["properties"][c]:
                    #             new_node["properties"][c] = new_node["properties"][c].replace("@acme.com", "")

            value = new_node["properties"]["userName"] if "userName" in new_node["properties"] \
                else new_node["properties"]["ip"] if "ip" in new_node["properties"] \
                else new_node["properties"]["hostname"] if "hostname" in new_node["properties"] \
                else new_node["properties"]["emailSubject"]

            if value == "":
                print(f"Got empty value identifier of node {new_node}, ignoring")
                continue

            if value not in nodes_added:
                print(f"Identifier value is -{value}- and of type {type(value)} for node {new_node}")
                rows.append(new_node)
                nodes_added.append(value)

            row_id += 1

    print(f"Total nodes before {sum([len(n) for n in nodes])} after {len(rows)}")
    print(set(nodes_added))
    nodes = pandas.DataFrame(rows)
    return nodes, rows


def generate_edge_id(edge, nodes, row_id):
    src_id = 0
    dst_id = 0
    src_info = edge["left"]
    dst_info = edge["right"]

    for node in nodes:
        # left_prop = src_info["property_key"]
        # left_val = src_info["value"]
        # if left_prop in nod
        try:
            if node["properties"][src_info["property_key"]] == src_info["value"]:
                src_id = node["node_id"]
                continue
            if node["properties"][dst_info["property_key"]] == dst_info["value"]:
                dst_id = node["node_id"]
                continue
        except KeyError:
            continue

    eid = f"{src_id}_{row_id}_{edge['edge_label']}_{dst_id}"

    return eid


def create_edges_data_frame(edges, edge_id=None):
    row_id = 0 if edge_id is None else edge_id

    rows = []
    for edge in edges:
        for e in edge:
            cols = e.keys()
            new_edge = {
                "label": e["edge_label"],
                "srcVertex": e["left"],
                "dstVertex": e["right"],
                "edge_id": str(uuid.uuid4().hex),
                "properties": {},

            }
            src_val = new_edge["srcVertex"]["value"].replace("$", "").lower()
            dst_val = new_edge["dstVertex"]["value"].replace("$", "").lower()

            if "acme\\\\" in src_val:
                src_val = src_val.replace("acme\\\\", "")
            if "acme\\" in src_val:
                src_val = src_val.replace("acme\\", "")
            if "@acme.com" in src_val:
                src_val = src_val.replace("@acme.com", "")
            if "acme\\\\" in dst_val:
                dst_val = dst_val.replace("acme\\\\", "")
            if "acme\\" in dst_val:
                dst_val = dst_val.replace("acme\\", "")
            if "@acme.com" in dst_val:
                dst_val = dst_val.replace("@acme.com", "")

            new_edge["srcVertex"]["value"] = src_val
            new_edge["dstVertex"]["value"] = dst_val

            for c in cols:
                if c not in ["edge_label", "left", "right"]:
                    if isinstance(e[c], str):
                        new_edge["properties"][c] = e[c].replace("$", "")
                    else:
                        new_edge["properties"][c] = e[c]

            if new_edge["srcVertex"]["value"] == 'None' or new_edge["srcVertex"]["value"] == 'None':
                print(f"Invalid edge found as its src = {new_edge['srcVertex']['value']} or dst = {new_edge['srcVertex']['value']} is invalid")
                continue

            rows.append(new_edge)
            row_id += 1

    print(f"Total edges before {sum([len(e) for e in edges])} after {len(rows)}")
    edges = pandas.DataFrame(rows)
    return edges, rows

# I see. only thing I didn't try is defining the table schema beforehand. Was making use of "auto infer" from pandas.


def load_to_snowflake_using_query(engine, nodes, edges, database, schema):
    # nodes.to_sql("nodes", con=connection, index=False, if_exists="append")

    nodes_insert = " \
        insert into nodes (id, node_id, label, properties, OUTEDGES, INEDGES, BOTHEDGES, OUTVERTICES, INVERTICES, OTHERVERTICES) \
        select column1, column2, column3, parse_json(column4), parse_json(column5), parse_json(column6), parse_json(column7), parse_json(column8), parse_json(column9), parse_json(column10) \
        from values ( \
            {id}, \
            {node_id}, \
            '{label}', \
            '{properties}', \
            '{outEdges}', \
            '{inEdges}', \
            '{bothEdges}', \
            '{outVertices}', \
            '{inVertices}', \
            '{otherVertices}' \
        )"

    node_json = json.loads(nodes.to_json(orient="records"))
    cur = engine.raw_connection().cursor()

    # cur.execute("truncate table nodes")
    # cur.execute("truncate table edges")

    cur.execute(f"USE {database}.{schema}")

    print("Truncated tables")

    failed_nodes = []
    print(f"Going to load {len(node_json)} nodes")
    i = 0
    start = dt.datetime.now()
    for row in node_json:
        sql = nodes_insert.format(id=row["id"], node_id=row["node_id"], label=row["label"],
                                  properties=json.dumps(row["properties"]), outEdges=json.dumps(row["outEdges"]),
                                  inEdges=json.dumps(row["inEdges"]), bothEdges=json.dumps(row["bothEdges"]),
                                  outVertices=json.dumps(row["outVertices"]), inVertices=json.dumps(row["inVertices"]),
                                  otherVertices=json.dumps(row["otherVertices"]))

        try:
            cur.execute(sql)
        except:
            import traceback
            traceback.print_exc()
            print("Failed for " + sql)
            failed_nodes.append(sql)

        i += 1

        if i % 100 == 0:
            end = dt.datetime.now()
            cur.execute("commit")
            print(f"Loaded successfully {i} nodes in {(end - start).total_seconds()} seconds")
            start = dt.datetime.now()

    print(failed_nodes)

    cur.execute("commit")

    # print(nodes.head(0))
    # nodes.head(0).to_sql(name="nodes", con=connection, if_exists="replace", index=False)
    # print("Created nodes table successfully")
    #
    # connection.execute("truncate table nodes")
    # connection.execute(f'put file://{node_path}* @%nodes')
    # connection.execute("copy into nodes FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = '|')")
    print("Loaded nodes successfully")

    # edges.head(0).to_sql(name="edges", con=connection, if_exists="replace", index=False)
    # print("Created edges table successfully")
    # connection.execute("truncate table edges")
    # connection.execute(f'put file://{edge_path}* @%edges')
    # connection.execute("copy into edges FILE_FORMAT = (type = csv field_delimiter = '|')")

    edges_insert = " \
            insert into edges (id, edge_id, label, properties, SOURCEVERTEX, DESTINATIONVERTEX) \
            select column1, to_binary(column2, 'hex'), column3, parse_json(column4), parse_json(column5), parse_json(column6) \
            from values ( \
                {id}, \
                '{edge_id}', \
                '{label}', \
                '{properties}', \
                '{sourceVertex}', \
                '{destinationVertex}' \
            )"

    edge_json = json.loads(edges.to_json(orient="records"))
    failed_edges = []

    print(f"Going to load {len(edge_json)} edges")
    i = 0
    start = dt.datetime.now()
    for row in edge_json:
        sql = edges_insert.format(id=row["id"], edge_id=row["edge_id"], label=row["label"],
                                  properties=json.dumps(row["properties"]),
                                  sourceVertex=json.dumps(row["sourceVertex"]),
                                  destinationVertex=json.dumps(row["destinationVertex"]))

        try:
            cur.execute(sql)
        except:
            import traceback
            traceback.print_exc()
            failed_edges.append(sql)

        i += 1
        if i % 500 == 0:
            end = dt.datetime.now()
            cur.execute("commit")
            print(f"Successfully loaded {i} edges in {(end - start).total_seconds()} seconds")
            start = dt.datetime.now()

    print(failed_edges)
    # edges.to_sql("edges", con=connection, index=False, if_exists="replace", method=pd_writer)
    print("Loaded edges successfully")

    cur.execute("commit")

    engine.dispose()


def load_data_using_dataframe(engine, nodes, edges):

    node_variants = ["properties", "outEdges", "inEdges", "bothEdges", "outVertices", "inVertices", "otherVertices"]
    edge_variants = ["srcVertex", "dstVertex", "properties"]
    print(f"Going to load {len(nodes)} nodes and {len(edges)}")

    connection = engine.connect()

    nodes = convert_data_to_json_str(nodes, node_variants)
    edges = convert_data_to_json_str(edges, edge_variants)

    start = dt.datetime.now()
    nodes.to_sql("nodes_demo_tmp", con=connection, index=False, if_exists="replace", method="multi", chunksize=500)
    end = dt.datetime.now()
    print(f'Loaded {len(nodes)} nodes in {end-start}')
    start = dt.datetime.now()
    edges.to_sql("edges_demo_tmp", con=connection, index=False, if_exists="replace", method="multi", chunksize=500)
    end = dt.datetime.now()
    print(f'Loaded {len(edges)} edges in {end-start}')

    convert_and_load_data_from_tmp_table(engine, nodes.columns.tolist(), edges.columns.tolist(), node_variants, edge_variants)

    connection.close()
    engine.dispose()


def convert_and_load_data_from_tmp_table(engine, node_cols, edge_cols, node_variant_cols, edge_variant_cols):
    start = dt.datetime.now()

    migration_stmt = '''
    insert into {output_tbl} ({cols})
    select {src_cols_with_parse} from {src_tbl}
    '''

    node_output_tbl = "nodes_demo"
    node_cols_merged = ",".join(["\"{}\"".format(x.upper()) if x not in node_variant_cols else "\"{}\"".format(x) for x in node_cols]).replace("properties", "PROPERTIES")
    node_cols_with_parse = ",".join(["\"{}\"".format(x.upper()) if x not in node_variant_cols else "parse_json(\"{}\")".format(x) for x in node_cols]).replace("properties", "PROPERTIES")
    node_src_tbl = "nodes_demo_tmp"

    nodes_sql = migration_stmt.format(output_tbl=node_output_tbl, cols=node_cols_merged, src_cols_with_parse=node_cols_with_parse, src_tbl=node_src_tbl)

    edge_output_tbl = "edges_demo"
    edge_cols_merged = ",".join(["\"{}\"".format(x.upper()) if x not in edge_variant_cols else "\"{}\"".format(x) for x in edge_cols]).replace("properties", "PROPERTIES")
    edge_cols_with_parse = ",".join(
        ["\"{}\"".format(x.upper()) if x not in edge_variant_cols else "parse_json(\"{}\")".format(x) for x in edge_cols]).replace("properties", "PROPERTIES")
    edge_src_tbl = "edges_demo_tmp"

    edges_sql = migration_stmt.format(output_tbl=edge_output_tbl, cols=edge_cols_merged,
                                      src_cols_with_parse=edge_cols_with_parse, src_tbl=edge_src_tbl)

    cursor = engine.raw_connection().cursor()

    print(nodes_sql)
    print(edges_sql)
    cursor.execute(nodes_sql)
    cursor.execute(edges_sql)
    cursor.execute("commit")

    end = dt.datetime.now()
    print(f"Migrated data to variant in {end-start}")

    cursor.execute(f"drop table {edge_src_tbl}")
    cursor.execute(f"drop table {node_src_tbl}")
    cursor.execute("commit")
    print(f"Dropped the temp tables {node_src_tbl} and {edge_src_tbl}")


def load_data_to_snowflake(nodes, edges, node_path, edge_path):
    load_start = dt.datetime.now()

    url = "jdbc:snowflake://ik55883.east-us-2.azure.snowflakecomputing.com"
    account = "ik55883.east-us-2.azure"
    user = "Debasish"
    pwd = "Work@456"
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

    # load_to_snowflake_using_query(engine, nodes, edges, database, schema)

    load_data_using_dataframe(engine, nodes, edges)

    load_end = dt.datetime.now()
    print(f"Total time to insert all data is {load_end-load_start}")


def convert_data_to_json_str(df, cols):
    for col in cols:
        df[col] = df[col].apply(json.dumps)
    return df


if __name__ == '__main__':
    data = json.load(open("../resources/dummy_data/graph_sample_2.json"))
    mapper = json.load(open("../resources/dummy_data/table_mapper.json"))
    node_rows = None
    edge_rows = None

    full_data = {
        "nodes": [],
        "edges": []
    }
    full_data["nodes"].extend(data["windows"]["nodes"])
    full_data["nodes"].extend(data["msexchange"]["nodes"])
    full_data["nodes"].extend(data["watchguard"]["nodes"])

    full_data["edges"].extend(data["windows"]["edges"])
    full_data["edges"].extend(data["msexchange"]["edges"])
    full_data["edges"].extend(data["watchguard"]["edges"])

    print(f"Total data to be loaded. NODES: {full_data['nodes']} and EDGES: {full_data['edges']}")

    node_path = f"../../../target/full_nodes.csv"
    edge_path = f"../../../target/full_edges.csv"

    print(f'Number of nodes is {len(full_data["nodes"])} and edges {len(full_data["edges"])}')

    nodes_df, nodes = create_nodes_data_frame(full_data["nodes"], full_data["edges"], mapper["nodes"], node_rows)
    node_rows = len(nodes)
    print("Generated nodes")

    edges_df, edges = create_edges_data_frame(full_data["edges"], edge_rows)
    edge_rows = len(edges)
    print("Generated edges")
    nodes_df = create_node_variant_cols(nodes, edges)
    print("Converted node cols to variants")

    print(edges_df.head())

    nodes_df.to_csv(node_path) # , index=False, header=False, sep="|")
    print(f"Saved nodes to {os.path.abspath(node_path)}")

    edges_df.to_csv(edge_path) # , index=False, header=False, sep="|")
    print(f"Saved edges to {os.path.abspath(edge_path)}")

    # nodes_df = convert_data_to_json_str(nodes_df, ["properties", "outEdges", "inEdges", "bothEdges", "outVertices", "inVertices", "otherVertices"])
    # edges_df = convert_data_to_json_str(edges_df, ["sourceVertex", "destinationVertex", "properties"])

    load_data_to_snowflake(nodes_df, edges_df, node_path, edge_path)
    print("Loaded successfully")



# 1 hop ego query along both edges (union on in and out)
# select n.id as srcId, n.label as srcLabel, n.properties as srcProp, o.value:properties as outEdgeProp, o.value:target:id as targetId, o.value:target:label::string as targetLabel, o.value:target as targetProp from nodes n, lateral flatten(n."outEdges") o where n.properties:userName='userName_0'
# union
# select n.id as targetId, n.label as targetLabel, n.properties as targetProp, i.value:properties as outEdgeProp, i.value:target:id as srcId, i.value:target:label::string as srcLabel, i.value:target as srcProp from nodes n, lateral flatten(n."inEdges") i where n.properties:userName='userName_0';

# 2 hop ego query along out edges
# select a.*, bce.value:properties as b_c_outprop, bce.value:id::string as b_c_id, bce.value:label::string as b_c_label, bce.value:target:id as cID, bce.value:target:label::string as cLabel, bce.value:target as cprop
# from nodes as c,
# lateral(
# select a.srcId as aId, a.srcLabel as aLabel, a.srcProp as aProp, a.outEdgeProp as a_b_outProp, a.outEdgeLabel::string as a_b_label, a.outEdgeId::string as a_b_Id, a.targetId as bId, a.targetLabel as bLabel, a.targetProp as bProp
#     from edges as e ,
#     lateral(select n."NODE_ID" as srcId, n.LABEL as srcLabel, n.PROPERTIES as srcProp, o.value:properties as outEdgeProp, o.value:id as outEdgeId, o.value:label as outEdgeLabel, o.value:target:id as targetId, o.value:target:label::string as targetLabel, o.value:target as targetProp from nodes n, lateral flatten(n."outEdges") o where n.properties:userName='userName_0') as a
# where e.edge_id = to_binary(a_b_Id, 'hex')
# ) as a,
# lateral flatten(c."outEdges") bce
# where a.bprop:id = c.node_id ;
