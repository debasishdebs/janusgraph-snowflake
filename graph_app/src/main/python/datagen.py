import json
import datetime as dt
import uuid


def generate_user_node(properties, i):
    node = dict()
    for prop in properties:
        if prop == "userName" or prop == "address":
            node[prop] = prop + "_" + str(i)
        else:
            node[prop] = prop + "_" + str(i%10)
    node["label"] = "user"
    node["id"] = i
    return node


def generate_ip_node(properties, i):
    node = dict()
    for prop in properties:
        if prop == "ip":
            node[prop] = "192.168.0." + str(i)
        elif prop == "ipFormat":
            node[prop] = "ipv4"
        else:
            node[prop] = prop + "_" + str(i % 10)
    node["label"] = "IP"
    node["id"] = i
    return node


def generate_host_node(properties, i):
    node = dict()
    for prop in properties:
        if prop == "hostname":
            node[prop] = prop + "_" + str(i)
        else:
            node[prop] = prop + "_" + str(i % 10)
    node["label"] = "hosts"
    node["id"] = i
    return node


def generate_nodes(schema, initial=None):
    label = schema["label"]
    count = schema["number"]
    properties = schema["properties"]

    nodes = []
    for i in range(count):
        if label == "user":
            nodes.append(generate_user_node(properties, i) if initial is None else generate_user_node(properties, i + initial))
        elif label == "IP":
            nodes.append(generate_ip_node(properties, i) if initial is None else generate_ip_node(properties, i + initial))
        else:
            nodes.append(generate_host_node(properties, i) if initial is None else generate_host_node(properties, i + initial))

    return nodes, len(nodes) if initial is None else len(nodes) + initial


def get_nodes_for_label(label, nodes):
    nodes_for_label = []
    for node in nodes:
        if node["label"] == label:
            nodes_for_label.append(node)

    return nodes_for_label


def generate_properties_for_edge(props, i):
    properties = {}
    for prop in props:
        if prop == "eventTime":
            properties[prop] = dt.datetime.now() + dt.timedelta(minutes=i)
        else:
            properties[prop] = i % 10
    return properties


def generate_edges(nodes, schema):
    label = schema["label"]
    ratio = schema["ratio"]["ratio"]
    properties = schema["properties"]
    source = schema["source"]
    dest = schema["destination"]

    source_nodes = get_nodes_for_label(source, nodes)
    dest_nodes = get_nodes_for_label(dest, nodes)

    edges = []

    if ratio > 1:
        if len(source_nodes) > len(dest_nodes):
            pass
        else:
            for i in range(len(source_nodes)):
                for j in range(ratio):
                    dst_node = dest_nodes[i + j] if (i+j) < len(dest_nodes) else dest_nodes[-1]

                    edge = {
                        "id": uuid.uuid4(),
                        "target": dst_node,
                        "source": source_nodes[i],
                        "label": label,
                        "properties": generate_properties_for_edge(properties, i)
                    }

                    if edge["source"]["id"] != edge["target"]["id"]:
                        edges.append(edge)
    return edges


def myconverter(o):
    if isinstance(o, dt.datetime):
        return o.__str__()
    if isinstance(o, uuid.UUID):
        # if the obj is uuid, we simply return the value of uuid
        return o.hex


if __name__ == '__main__':
    node_schema = json.load(open("../resources/dummy_data/node_gen_schema.json"))
    edge_schema = json.load(open("../resources/dummy_data/edge_gen.json"))

    nodes = []
    initial = None
    for schema in node_schema:
        nodes_for_label, initial = generate_nodes(schema, initial)
        nodes.extend(nodes_for_label)

    print("Generated nodes")

    edges = []
    for schema in edge_schema:
        edges.extend(generate_edges(nodes, schema))

    print("Generated edges")

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    print(edges[0]["id"])
    print(len([edge for edge in edges if edge["id"] is None]))

    print(f'Nodes: {len(nodes)} and edges {len(edges)}')

    json.dump(graph, open("../../../target/dummy_graph_full.json", "w+"), indent=2, default=myconverter)
