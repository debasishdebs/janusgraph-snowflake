from netaddr import valid_ipv4, valid_ipv6
import re
import os


def identify_if_ip_is_src_or_dest(ipType):
    if ipType == "source":
        return "src"
    else:
        return "dest"


def identify_if_ip_is_ip4_or_ip6(ip):
    if valid_ipv4(ip):
        return "ipv4"
    elif valid_ipv6(ip):
        return "ipv6"
    else:
        return "NA"


def get_ip_for_guardduty_events(record):
    internal_ip = record["virtualIP"] if record["virtualIP"] != "" else record["from"]
    external_ip = record["from"] if record["virtualIP"] != "" else ""
    return internal_ip, external_ip


def get_ip_for_guardduty_traffic(record):
    src_ip = record["src"] if "src" in record else ""
    dst_ip = record["dst"] if "dst" in record else ""
    return src_ip, dst_ip


def get_ip_type_for_guardduty_events(record):
    internal_ip_type = "internal"
    external_ip_type = "external" if record["virtualIP"] != "" else ""
    return internal_ip_type, external_ip_type


def get_ip_format_for_guardduty_events(record):
    int_ip, ext_ip = get_ip_for_guardduty_events(record)

    internal_ip_fmt = identify_if_ip_is_ip4_or_ip6(int_ip) if int_ip != "" else "NA"
    external_ip_fmt = identify_if_ip_is_ip4_or_ip6(ext_ip) if ext_ip != "" else "NA"

    return internal_ip_fmt, external_ip_fmt


def get_ip_format_for_guardduty_traffic(record):
    src_ip, dst_ip = get_ip_for_guardduty_traffic(record)

    src_ip_fmt = identify_if_ip_is_ip4_or_ip6(src_ip) if src_ip != "" else "NA"
    dst_ip_fmt = identify_if_ip_is_ip4_or_ip6(dst_ip) if dst_ip != "" else "NA"

    return src_ip_fmt, dst_ip_fmt


def get_src_dst_ips_for_msexchange(record):
    srcIPKey = "server-ip"
    dstIPKey = "client-ip"
    return record[srcIPKey], record[dstIPKey]


def get_receiver_users_for_msexchange(record):
    return record["recipient-address"].split(";")


def get_all_users_for_msexchange_pa(record):
    key1 = "sender-address"
    key2 = "recipient-address"
    users = record[key1].split(";") + record[key2].split(";")
    return users


def get_all_ips_for_msexchange_pa(record):
    key1 = "server-ip"
    key2 = "client-ip"
    ips = record[key1].split(";") + record[key2].split(";")
    return ips


def get_all_users_for_msexchange(record):
    key1 = "sender-address"
    key2 = "recipient-address"
    users = record[key1].split(";") + record[key2].split(";")
    return users


def get_all_ips_for_msexchange(record):
    key1 = "client-ip"
    key2 = "server-ip"
    ips = record[key1].split(";") + record[key2].split(";")
    return ips


def get_src_dst_hostname_for_msexchange(record):
    srcHostKey = "server-hostname"
    dstHostKey = "client-hostname"
    return record[srcHostKey], record[dstHostKey]


def get_src_dst_username_for_msexchange(record):
    srcUserKey = "sender-address"
    dstUserLey = "recipient-address"
    return record[srcUserKey], record[dstUserLey]


def get_ip_format_for_msexchange(record):
    src_ip, dst_ip = get_src_dst_ips_for_msexchange(record)

    src_ip_fmt = identify_if_ip_is_ip4_or_ip6(src_ip) if src_ip != "" else "NA"
    dst_ip_fmt = identify_if_ip_is_ip4_or_ip6(dst_ip) if dst_ip != "" else "NA"

    return src_ip_fmt, dst_ip_fmt


def get_src_dst_ip_for_watchguard_traffic(record):
    src_ip_key = "ip_src_addr"
    dst_ip_key = "ip_dst_addr"
    return record[src_ip_key], record[dst_ip_key]


def get_username_for_watchguard_traffic(*args):
    record = args[-1]

    src_key = "src_user"
    dst_key = "dst_user"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    src_info = record[args[0]]
    dst_info = record[args[1]]

    src_info_dict = dict(regex.findall(src_info))
    dst_info_dict = dict(regex.findall(dst_info))

    if src_key in src_info_dict:
        src_user = src_info_dict[src_key].replace(";", "")
    else:
        src_user = ""

    if dst_key in dst_info:
        dst_user = dst_info_dict[dst_key].replace(";", "")
    else:
        dst_user = ""

    # TODO : REMOVE THIS LATER ONCE DATA RECTIFIES
    src_user = src_user.replace("@local", "@acme.com")
    dst_user = dst_user.replace("@local", "@acme.com")

    return src_user, dst_user


def get_username_for_watchguard_relationships(*args):
    record = args[-1]

    # We know that only one will be present, either src_user or dst_user. We will return that one value

    src_key = "src_user"
    dst_key = "dst_user"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    src_info = record[args[0]]
    dst_info = record[args[1]]

    src_info_dict = dict(regex.findall(src_info))
    dst_info_dict = dict(regex.findall(dst_info))

    if src_key in src_info_dict:
        src_user = src_info_dict[src_key].replace(";", "")

        # TODO : REMOVE THIS LATER ONCE DATA RECTIFIES
        src_user = src_user.replace("@local", "@acme.com")
        return src_user

    if dst_key in dst_info:
        dst_user = dst_info_dict[dst_key].replace(";", "")
        # TODO : REMOVE THIS LATER ONCE DATA RECTIFIES
        dst_user = dst_user.replace("@local", "@acme.com")
        return dst_user

    return ""


def get_url_from_watchguard(*args):
    record = args[-1]
    info_key = record[args[0]]

    url_key = "dstname"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)
    info_dict = dict(regex.findall(info_key))

    if url_key in info_key:
        URL = info_dict[url_key]
    else:
        URL = ""

    return URL


def get_process_from_watchguard(*args):
    record = args[-1]
    info_key = record[args[0]]

    process_key = "arg"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)
    info_dict = dict(regex.findall(info_key))

    if process_key in info_key:
        full_process = info_dict[process_key]

        root, fname = os.path.split(full_process)

    else:
        fname = ""

    return fname


def get_argument_from_watchguard(*args):
    record = args[-1]
    info_key = record[args[0]]

    arg_key = "arg"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)
    info_dict = dict(regex.findall(info_key))

    if arg_key in info_key:
        argument = info_dict[arg_key]

    else:
        argument = ""

    return argument


def get_src_geo_loc_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    src_loc_key = "geo_src"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if src_loc_key in info_dict:
        src_geo = info_dict[src_loc_key].replace(";", "")
    else:
        src_geo = ""

    return src_geo


def get_dst_geo_loc_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    dst_loc_key = "geo_dst"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if dst_loc_key in info_dict:
        dst_geo = info_dict[dst_loc_key].replace(";", "")
    else:
        dst_geo = ""

    return dst_geo


def get_sent_bytes_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    src_bytes_key = "sent_bytes"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if src_bytes_key in info_dict:
        src_bytes = info_dict[src_bytes_key].replace(";", "")
    else:
        src_bytes = ""

    return src_bytes


def get_rcvd_bytes_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    dst_bytes_key = "rcvd_bytes"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if dst_bytes_key in info_dict:
        dst_bytes = info_dict[dst_bytes_key].replace(";", "")
    else:
        dst_bytes = ""

    return dst_bytes


def get_elpsd_time_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    elapsed_time_key = "elapsed_time"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if elapsed_time_key in info_dict:
        elapsed_time = info_dict[elapsed_time_key].replace(";", "")
    else:
        elapsed_time = ""

    return elapsed_time


def get_network_operation_watchguard(*args):
    record = args[-1]

    info = record[args[0]]

    operation_key = "op"

    pattern = r'\b(\w+)=([^=]*)(?=\s\w+=\s*|$)'
    regex = re.compile(pattern)

    info_dict = dict(regex.findall(info))

    if operation_key in info_dict:
        operation = info_dict[operation_key].replace(";", "")
    else:
        operation = ""

    return operation


def get_ip_for_sysmon_events(*args):
    record = args[-1]

    src_ip_key = args[0]
    dst_ip_key = args[1]

    if src_ip_key in record:
        src_ip = record[src_ip_key]
    else:
        src_ip = ""

    if dst_ip_key in record:
        dst_ip = record[dst_ip_key]
    else:
        dst_ip = ""

    return src_ip, dst_ip


def get_host_for_sysmon_events(*args):
    record = args[-1]

    src_host_key = args[0]
    dst_host_key = args[1]

    if src_host_key in record:
        src_host = record[src_host_key]
    else:
        src_host = ""

    if dst_host_key in record:
        dst_host = record[dst_host_key]
    else:
        dst_host = ""

    return src_host, dst_host


def generate_username_for_windows_v3(record):
    key1 = "TargetUserName"
    key2 = "SubjectUserName"

    if key1 in record and key2 in record:
        userName = record[key1]
    elif key1 in record and key2 not in record:
        userName = record[key1]
    elif key2 in record and key1 not in record:
        userName = record[key2]
    else:
        userName = ""

    userName = userName.split("\\")[-1]

    userName = userName# + "@local"

    return userName


def generate_username_for_sysmon_v2(record):
    k = "User"

    if k in record:
        userName = record[k]
    else:
        userName = ""

    userName = userName.split("\\")[-1]

    userName = userName# + "@local"

    return userName


def get_ips_for_watchguard_proxy(record):
    return record["src"], record["dst"]


def get_geo_loc_for_watchguard_proxy(record):
    geo_dst = ""
    geo_src = ""
    if "geo_src" in record:
        geo_src = record["geo_src"]

    if "geo_dst" in record:
        geo_dst = record["geo_dst"]

    return geo_src, geo_dst


def get_url_for_watchguard_proxy(record):
    if "dstname" in record and identify_if_ip_is_ip4_or_ip6(record["dstname"]) == "NA":
        return record["dstname"]
    else:
        return ""


exchange_maps = {
    "property0": "datetime",
    "property1": "client-ip",
    "property2": "client-hostname",
    "property3": "server-ip",
    "property4": "server-hostname",
    "property5": "source-context",
    "property6": "connector-id",
    "property7": "source",
    "property8": "event-id",
    "property9": "internal-message-id",
    "property10": "message-id",
    "property11": "recipient-address",
    "property12": "recipient-status",
    "property13": "total-bytes",
    "property14": "recipient-count",
    "property15": "related-recipient-address",
    "property16": "reference",
    "property17": "message-subject",
    "property18": "sender-address",
    "property19": "return-path",
    "property20": "message-info",
    "property21": "directionality",
    "property22": "tenant-id",
    "property23": "original-client-ip",
    "property24": "original-server-ip",
    "property25": "custom-data"
}

watchguard_maps = {
    "property0": "sid",
    "property1": "cluster",
    "property2": "sn",
    "property3": "messageID",
    "property4": "tag_id",
    "property5": "raw_id",
    "property6": "disp",
    "property7": "direction",
    "property8": "pri",
    "property9": "policy",
    "property10": "protocol",
    "property11": "ip_src_addr",
    "property12": "ip_src_port",
    "property13": "ip_dst_addr",
    "property14": "ip_dst_port",
    "property15": "src_ip_nat",
    "property16": "src_port_nat",
    "property17": "dst_ip_nat",
    "property18": "dst_port_nat",
    "property19": "src_intf",
    "property20": "dst_intf",
    "property21": "rc",
    "property22": "pckt_len",
    "property23": "ttl",
    "property24": "pr_info",
    "property25": "proxy_act",
    "property26": "alarm_name",
    "property27": "alarm_type",
    "property28": "alarm_id",
    "property29": "info_1",
    "property30": "info_2",
    "property31": "info_3",
    "property32": "info_4",
    "property33": "info_5",
    "property34": "info_6",
    "property35": "property35",
    "property36": "property36",
    "property37": "property37",
    "property38": "property38",
    "property39": "property39",
    "property40": "property40",
    "property41": "log_type",
    "property42": "msg",
    "property43": "bucket",
    "property44": "timestamp"
}
