import datetime as dt
from gen.graphdb_pb2 import Time, ConditionalURLs, ConditionalHosts, ConditionalIPs, ConditionalUsers, CaseInformation, Node, NodesInCase
from dateutil.parser import parse

APPLICATION_PROPERTIES = "/app/src/main/resources/application.properties"
# APPLICATION_PROPERTIES = "../../resources/application.properties"


class Utilities:
    @staticmethod
    def load_properties(filepath, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props

    @staticmethod
    def convert_proto_map_to_python_dict(obj):
        python_obj = {}
        for key in obj:
            python_obj[key] = obj[key]
        return python_obj

    @staticmethod
    def convert_proto_list_to_python_list(obj):
        elements = []
        for o in obj:
            elements.append(o)
        return elements

    @staticmethod
    def convert_nodes_in_record_proto_to_python_list(obj):
        assert type(obj) == NodesInCase
        nodes_got = obj.nodes
        nodes = []
        for node in nodes_got:
            assert type(node) == Node
            node_dict = {}
            for prop in node.properties:
                node_dict[prop] = node.properties[prop].string_value
            nodes.append(node_dict)
        return nodes

    @staticmethod
    def convert_proto_time_to_time_string(time):
        t = dt.datetime(time.year, time.month, time.day, time.hour, time.minutes, time.seconds)
        return t.strftime("%a %b %d %Y %H:%M:%S")

    @staticmethod
    def convert_case_information_to_python_query_dict(obj):
        assert type(obj) == CaseInformation
        ips = obj.IPs
        users = obj.users
        hosts = obj.hosts
        urls = obj.urls

        ip_list = []
        user_list = []
        host_list = []
        url_list = []
        for ip in ips:
            assert type(ip) == ConditionalIPs
            ip_info = {
                "IP": ip.IP
                # "startTime": ip.startTime,
                # "endTime": ip.endTime,
                # "dataSource": ip.dataSource
            }
            ip_list.append(ip.IP)

        for user in users:
            assert type(user) == ConditionalUsers
            user_info = {
                "USER": user.USER
                # "startTime": user.startTime,
                # "endTime": user.endTime,
                # "dataSource": user.dataSource
            }
            user_list.append(user.USER)

        for host in hosts:
            assert type(host) == ConditionalHosts
            host_info = {
                "HOST": host.HOST
                # "startTime": host.startTime,
                # "endTime": host.endTime,
                # "dataSource": host.dataSource
            }
            host_list.append(host.HOST)

        for url in urls:
            assert type(url) == ConditionalURLs
            url_info = {
                "URL": url.URL
                # "startTime": url.startTime,
                # "endTime": url.endTime,
                # "dataSource": url.dataSource
            }
            url_list.append(url.URL)

        return {"IP": ip_list, "Users": user_list, "URLs": url_list, "Host": host_list}

    @staticmethod
    def convert_time_string_to_proto_time(time: str):
        time = parse(time, fuzzy=True)

        t = Time()
        t.year = time.year
        t.month = time.month
        t.day = time.day
        t.hour = time.hour
        t.minutes = time.minute
        t.seconds = time.second
        return t

    @staticmethod
    def convert_python_time_to_proto_time(time: dt.datetime):
        t = Time()
        t.year = time.year
        t.month = time.month
        t.day = time.day
        t.hour = time.hour
        t.minutes = time.minute
        t.seconds = time.second
        return t

    @staticmethod
    def convert_case_query_to_case_information_proto(case_query: dict):
        user_list = []
        ip_list = []
        host_list = []
        url_list = []

        for label, label_queries in case_query.items():
            print(f"Label: {label}, label_queries: {label_queries}")

            if label == "user":
                for query in label_queries["entityQueries"]:
                    elem = ConditionalUsers(USER=query)
                    # elem.dataSource = query["dataSource"] if "dataSource" in query else None
                    # if "startTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["startDate"]))
                    # if "endTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["endDate"]))
                    user_list.append(elem)

            elif label == "IP":
                for query in label_queries["entityQueries"]:
                    print(query)
                    elem = ConditionalIPs(IP=query)
                    # elem.dataSource = query["dataSource"] if "dataSource" in query else None
                    # if "startTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["startDate"]))
                    # if "endTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["endDate"]))
                    ip_list.append(elem)

            elif label == "host":
                for query in label_queries["entityQueries"]:
                    elem = ConditionalHosts(HOST=query)
                    # elem.dataSource = query["dataSource"] if "dataSource" in query else None
                    # if "startTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["startDate"]))
                    # if "endTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["endDate"]))
                    host_list.append(elem)

            elif label == "url":
                for query in label_queries["entityQueries"]:
                    elem = ConditionalURLs(URL=query)
                    # elem.dataSource = query["dataSource"] if "dataSource" in query else None
                    # if "startTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["startDate"]))
                    # if "endTime" in query:
                    #     elem.startTime.CopyFrom(Utilities.convert_python_time_to_proto_time(query["endDate"]))
                    url_list.append(elem)

        info = CaseInformation(IPs=ip_list, users=user_list, hosts=host_list, urls=url_list)

        return info

    @staticmethod
    def generate_case_id():
        epoch = dt.datetime.utcfromtimestamp(0)
        epoch_sec = (dt.datetime.now() - epoch).total_seconds()
        pre_char = int(epoch_sec/10000)
        post_char = epoch_sec % 10000
        post_char = str(post_char).replace(".", "_")
        case_id = f"{pre_char}_sstech_{post_char}"
        return case_id


class API_UTILITIES:
    API_DATE_FORMAT_2 = "%a %b %d %Y %H:%M:%S"
    API_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def __get_selection__(args):
        selection = args["selection"] if "selection" in args else None
        return selection.split(",") if selection is not None else None

    @staticmethod
    def __get_data_sources__(args):
        data_sources = args["data_source_name"] if "data_source_name" in args else None
        return data_sources.split(",") if data_sources is not None else None

    @staticmethod
    def __get_start_time__(args):
        start_time = args["startTime"] if "startTime" in args else None
        start_time = None if start_time is None or start_time == "null" else start_time
        if start_time is None:
            return start_time
        else:
            try:
                start_time = dt.datetime.strptime(start_time, API_UTILITIES.API_DATE_FORMAT)
            except ValueError:
                try:
                    start_time = dt.datetime.strptime(start_time, API_UTILITIES.API_DATE_FORMAT_2)
                except ValueError:
                    from dateutil.parser import parse
                    start_time = parse(start_time)
            return start_time

    @staticmethod
    def __get_end_time__(args):
        end_time = args["endTime"] if "endTime" in args else None
        end_time = None if end_time is None or end_time == "null" else end_time
        if end_time is None:
            return end_time
        else:
            try:
                end_time = dt.datetime.strptime(end_time, API_UTILITIES.API_DATE_FORMAT)
            except ValueError:
                try:
                    end_time = dt.datetime.strptime(end_time, API_UTILITIES.API_DATE_FORMAT_2)
                except ValueError:
                    from dateutil.parser import parse
                    end_time = parse(end_time) if end_time is not None else None
            return end_time

    @staticmethod
    def __get_current_time__():
        return dt.datetime.now()

    @staticmethod
    def __get_time_type__(args):
        time_type = args["type"].lower() if "type" in args else None

        if time_type is None or time_type not in ["h", "m", "d"]:
            status_msg = "time_type needs to be provided as param. provide type=h or type=m of type=d (if type=d) " \
                         "then snowflake=true is needed."
            return False, status_msg
        else:
            return True, time_type

    @staticmethod
    def __get_time_range__(args):
        time_range = args["range"] if "range" in args else None
        if time_range is None:
            status_msg = "time range needs to be provided using 'range' parameter. Else for how long range will " \
                         "data be fetched?"
            return False, status_msg

        return True, time_range

    @staticmethod
    def __get_start_end_time_for_recent_data_api__(args):
        current_time = API_UTILITIES.__get_current_time__()
        time_type_status, time_type = API_UTILITIES.__get_time_type__(args)
        time_range_status, time_range = API_UTILITIES.__get_time_range__(args)

        if time_type_status and time_range_status:
            if time_type == "h":
                beg_time = current_time - dt.timedelta(hours=time_range)
            elif time_type == "m":
                beg_time = current_time - dt.timedelta(minutes=time_range)
            else:
                beg_time = current_time - dt.timedelta(days=time_range)

            return beg_time, current_time

        status_msg = "Concatenating the message. Check accordingly: [%s]: time_type & [%s]: time_range".format(time_type, time_range)
        return False, status_msg

