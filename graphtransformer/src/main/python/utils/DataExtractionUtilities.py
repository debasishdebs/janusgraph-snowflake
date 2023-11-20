import string
from utils.constants import Commons
from os import path


def generate_destination_users_for_msexchange(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        users = value.split(";")
        if repeat == -1:
            return users
        return users if repeat == -1 else users[:repeat]
    else:
        return ["NA"]


def generate_user_name_for_windowsnxlog(params, record, repeat):
    if params[0] in record:
        username = record[params[0]]
        username = username.replace("$", "")
        username = username.replace("ACME\\", "")
        username = username.lower()
        users = username.split(";")
        if repeat == -1:
            return users
        return users if repeat == -1 else users[:repeat]
    else:
        return [""]


def generate_user_name_for_sysmon(params, record, repeat):
    if params[0] in record:
        username = record[params[0]]
        username = username.replace("$", "")
        username = username.replace("%", "")
        username = username.replace("ACME\\", "")
        username = username.lower()
        users = username.split(";")
        if repeat == -1:
            return users
        return users if repeat == -1 else users[:repeat]
    else:
        return [""]


def generate_process_name_for_sysmon(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_parent_process_name_for_sysmon(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_target_process_name_for_sysmon(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_process_path_for_sysmon(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        value = value.replace("%", "")
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.dirname(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_process_name_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_process_path_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.dirname(process).lower())
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_elapsed_time_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        values = value.split(" ")
        time_num = values[0]
        time_unit = values[1]
        return [time_num]
    else:
        return ["NA"]


def clean_node(node):
    node_new = {}
    for k, v in node.items():
        if isinstance(v, str):
            if "$" in v:
                # print("Found $ in node ", v)
                v = v.replace("$", "")
            if "\'" in v:
                # print("Found \' in node ", v)
                v = v.replace("\'", "")
            if "\"" in v:
                # print("Found \" in node ", v)
                v = v.replace("\"", "")
            if "\\\"" in v:
                # print("Found \\\" in node ", v)
                v = v.replace("\\\"", "")
            if "\\u" in v:
                # print("Found \\u in node ", v)
                v = v.replace("\\u", "")
            if "\\" in v:
                # print("Found \\ in node ", v)
                v = v.replace("\\", "")
            if "\\x" in v:
                # print("Found \\x in node ", v)
                v = v.replace("\\x", "")

            printable = set(string.printable)
            v = "".join(filter(lambda x: x in printable, v))
            v = v.encode("ascii", "ignore").decode("utf-8")
            # print(v)

        node_new[k] = v
    return node_new


def is_node_empty(node):
    blank = True
    label = node["node_label"]
    unique = "userName" if label == "user" else "ip" if label == "IP" else "hostname" if label == "host" \
        else "fileName" if (label == "process" or label == "childProcess") else "emailSubject" if label == "email" else "URL"
    # print(label, unique, node)
    for k, v in node.items():
        if k in ["label", "node_label", "dataSourceName"]:
            # These are the defaults for a node currently
            pass
        else:
            if v not in ["", "-", "NA", "na", None, "null", "system", "sstechgcdc01", "administrator", "localhost", "127.0.0.1"]:
                # Again defaults for blanks. - found for IPs
                blank = False

    if node[unique] not in ["", "-", "NA", "na", None, "null", "system", "sstechgcdc01", "administrator", "localhost", "127.0.0.1"]:
        return blank
    else:
        # print(f"Found invalid value for node {node} with label {label} and uniqueProp {unique} and value {node[unique]}")
        return True


def is_edge_empty(edge):
    # print("TODO")
    # TODO
    # print("I need to add condition here reflecting similar to valueSkip in DataGenerator so that few generic values")
    # print("like localhost etc which are generic and doesn't make sense from analysis perspective and can be ignored")
    blank = False

    if "left" in edge and "right" in edge:
        if isinstance(edge["left"], list) and isinstance(edge["right"], list):
            if len(edge["left"]) != len(edge["right"]):
                raise AttributeError("Strange error. The length of left and right are diff? Thought this was handled for " + str(edge))

            if len(edge["left"]) != 1:
                raise AttributeError("Strange left/right is supposed to be of length 1 because its handled")

            if edge["left"][0]["value"] in Commons.INVALID_EDGE_IDENTIFIERS \
                    or edge["right"][0]["value"] in Commons.INVALID_EDGE_IDENTIFIERS:
                # Invalid edge, when either's source of destination info isn't available
                blank = True

        elif isinstance(edge["left"], list) and isinstance(edge["right"], dict):
            if len(edge["left"]) != 1:
                raise AttributeError("Strange left is supposed to be of length 1 because its handled")

            if edge["left"][0]["value"] in Commons.INVALID_EDGE_IDENTIFIERS \
                    or edge["right"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS:
                # Invalid edge, when either's source of destination info isn't available
                blank = True

        elif isinstance(edge["right"], list) and isinstance(edge["left"], dict):
            if len(edge["right"]) != 1:
                raise AttributeError("Strange left is supposed to be of length 1 because its handled")

            if edge["left"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS\
                    or edge["right"][0]["value"] in Commons.INVALID_EDGE_IDENTIFIERS:
                # Invalid edge, when either's source of destination info isn't available
                blank = True

        else:
            if edge["left"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS\
                    or edge["right"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS:
                # Invalid edge, when either's source of destination info isn't available
                blank = True

    else:
        blank = True

    return blank


def reformat_left_or_right(obj):
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list):
        if len(obj) > 1:
            raise AttributeError("Strange, by this time the length of left/right should be 1 as its handled got " + str(obj))
        if isinstance(obj[0], dict):
            return obj[0]
        raise AttributeError("Strange, the content inside list isn't dict? " + str(obj))
