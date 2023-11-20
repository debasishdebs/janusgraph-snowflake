import uuid


def generate_node_id(node, edges, nodes):
    return node["id"]


def generate_node_label(node, edges, nodes):
    return node["label"]


def generate_node_property_json(node, edges, nodes):
    return {k:v for k,v in node.items() if k not in ["id", "label"]}


def generate_outgoing_edges_json_list(node, edges, nodes):
    edge_list = []
    for edge in edges:
        if edge["source"]["id"] == node["id"]:
            edge_list.append(edge)
    return edge_list


def generate_incoming_edges_json_list(node, edges, nodes):
    edge_list = []
    for edge in edges:
        if edge["target"]["id"] == node["id"]:
            edge_list.append(edge)
    return edge_list


def generate_both_edges_json_list(node, edges, nodes):
    edge_list = []
    for edge in edges:
        if edge["target"]["id"] == node["id"] or edge["source"]["id"] == node["id"]:
            edge_list.append(edge)
    return edge_list


def get_node_for_id(id, nodes):
    for node in nodes:
        if node["id"] == id:
            return node


def generate_outside_vertices_json_list(node, edges, nodes):
    node_list = []
    for edge in edges:
        if edge["source"]["id"] == node["id"]:
            node_list.append(get_node_for_id(edge["target"]["id"], nodes))

    return node_list


def generate_inside_vertices_json_list(node, edges, nodes):
    node_list = []
    for edge in edges:
        if edge["target"]["id"] == node["id"]:
            node_list.append(get_node_for_id(edge["source"]["id"], nodes))

    return node_list


def generate_other_vertices_json_list(node, edges, nodes):
    node_list = []
    for edge in edges:
        if edge["target"]["id"] == node["id"]:
            node_list.append(get_node_for_id(edge["source"]["id"], nodes))

        if edge["source"]["id"] == node["id"]:
            node_list.append(get_node_for_id(edge["target"]["id"], nodes))

    return node_list


def generate_edge_label(edge, nodes):
    return edge["label"]


def generate_edge_id(edge, nodes):
    return edge["id"]


def generate_source_vertex_for_edge(edge, nodes):
    return get_node_for_id(edge["source"]["id"], nodes)


def generate_dst_vertex_for_edge(edge, nodes):
    return get_node_for_id(edge["target"]["id"], nodes)


def generate_edge_property_json(edge, nodes):
    return edge["properties"]
