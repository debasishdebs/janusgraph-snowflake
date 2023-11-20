import json

from utils.commons import Utilities as U
import grpc
from gen.graphdb_pb2 import CaseSubmissionPayload, EntityQuery, EntityTypeQuery, Time, CaseInfo, CaseLoadingStatus, \
    google_dot_protobuf_dot_empty__pb2 as empty, CaseExportStatus, AddAddedTimeForRawData, UpdateProcessedTime
from gen.graphdb_pb2_grpc import ServicesToGraphExtractorStub, ServicesToGraphCoreStub
from time import sleep
from datetime import datetime as dt
from client.connection.SnowGraphConnection import SnowGraphConnection
from client.traversal.GraphTraversal import GraphTraversal
from client.traversal.Predicates import P
from client.traversal.Column import Column as C
from client.traversal.AnonymousTraversal import __


class GraphAppController:

    def __init__(self, config):
        resource_properties = config

        url = f'{resource_properties["grpc.extractor.server.host"]}:{resource_properties["grpc.extractor.server.port"]}'
        self.extractor_channel = grpc.insecure_channel(url)
        print(f"Initialized extractor client at url: {url}")

        url = f'{resource_properties["grpc.core.server.host"]}:{resource_properties["grpc.core.server.port"]}'
        self.core_channel = grpc.insecure_channel(url)
        print(f"Initialized core client at url: {url}")
        host = resource_properties["grpc.core.server.host"]
        port = int(resource_properties["grpc.core.server.port"])

        self.CORE_CLIENT = ServicesToGraphCoreStub(channel=self.core_channel)
        self.EXTRACTOR_CLIENT = ServicesToGraphExtractorStub(channel=self.extractor_channel)
        self.SNOWGRAPH_CONN = SnowGraphConnection().set_host(host).set_port(port)

    def get_case_status(self, case_info: dict):

        case_ids = case_info["case_id"]
        assert type(case_ids) == list
        case = CaseInfo(caseId=case_ids)

        response = self.CORE_CLIENT.GetCaseLoadingStatus(case)

        return response

    def update_case_status(self, case_info: dict, status: str):
        case_id = case_info["case_id"]
        case_query = case_info["query"] if "query" in case_info else None

        startTime = U.convert_python_time_to_proto_time(case_info["startTime"])
        endTime = U.convert_python_time_to_proto_time(case_info["endTime"])
        procTime = U.convert_python_time_to_proto_time(dt.now())
        dataSources = case_info["dataSource"]

        if status.lower() == "initialized":
            case_status = CaseLoadingStatus(status=status, caseId=case_id, startTime=startTime, endTime=endTime,
                                            processingTime=procTime, dataSources=dataSources, queryExportTime=procTime)
        else:
            case_status = CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)

        if case_query is not None:
            case_status.query.CopyFrom(U.convert_case_query_to_case_information_proto(case_query))

        if "startDate" in case_info:
            case_status.startTime.CopyFrom(U.convert_python_time_to_proto_time(case_info["startDate"]))
        if "endDate" in case_info:
            case_status.endTime.CopyFrom(U.convert_python_time_to_proto_time(case_info["endDate"]))

        if "dataSource" in case_info:
            for ds in case_info["dataSource"]:
                print(case_status.dataSources, type(case_status.dataSources), ds)
                case_status.dataSources.append(ds)

        print("Case status updater object is")
        print(case_status)

        return self.CORE_CLIENT.UpdateCaseLoadingStatus(case_status)

    def get_status_for_query_export(self, case_info: dict):
        case_msg = CaseSubmissionPayload()
        for label, entity_queries_dict in case_info["query"].items():
            entity_type_query = EntityTypeQuery()

            for entity_query in entity_queries_dict["entityQueries"]:
                ent_q = EntityQuery(value=entity_query)
                entity_type_query.entityQuery.append(ent_q)

            case_msg.query[label].CopyFrom(entity_type_query)

        return self.CORE_CLIENT.IsCaseExported(case_msg)

    def get_all_case_ids(self):
        params = empty.Empty()
        return self.CORE_CLIENT.GetCaseIds(params)

    def get_delta_between_raw_and_graph_data(self):
        query = self.CORE_CLIENT.GetTheDataToQueryInNextIteration(CaseExportStatus())
        print(query.msg, type(query.msg))
        print(json.loads(query.msg), type(json.loads(query.msg)))
        print(json.loads(json.loads(query.msg)), type(json.loads(json.loads(query.msg))))
        return json.loads(json.loads(query.msg))

    def update_added_time_to_tracking_table(self, tables: list, added_time: Time, data_sources: list):
        params = AddAddedTimeForRawData()
        params.tables[:] = tables
        params.data_sources[:] = data_sources
        params.added_time.CopyFrom(added_time)
        res = self.CORE_CLIENT.UpdateAddedTimeToTrackingTableForRawData(params)
        return json.loads(res.msg)

    def update_processed_time_to_tracking_table(self, processed_time: Time):
        params = UpdateProcessedTime()
        params.processed_time.CopyFrom(processed_time)
        res = self.CORE_CLIENT.UpdateProcessedTimeToTrackingTableForRawData(params)
        return json.loads(res.msg)

    def start_case_import(self, case_info: dict):
        print("Starting case import as async, sleeping for 5")
        print(case_info)
        print("=====")

        case_dict = dict()
        case_dict["case_id"] = case_info["case_id"]
        case_info.pop("case_id")
        if "hops" not in case_info:
            case_dict.update({"hops": 1})
        case_dict["query"] = case_info["query"]

        case_dict["dataSource"] = case_info["dataSource"]
        case_dict["startTime"] = case_info["startTime"]
        case_dict["endTime"] = case_info["endTime"]

        case_id = case_dict["case_id"]

        print("Modified caseDict ", case_dict)

        self.update_case_status(case_dict, "Initialized")
        print("Updated case status for import")

        startTime = U.convert_python_time_to_proto_time(case_dict["startTime"])
        endTime = U.convert_python_time_to_proto_time(case_dict["endTime"])
        procTime = U.convert_python_time_to_proto_time(dt.now())

        case_msg = CaseSubmissionPayload(caseId=case_id, startDate=startTime, endDate=endTime,
                                         dataSources=case_dict["dataSource"])
        for label, entity_queries_dict in case_info["query"].items():
            entity_type_query = EntityTypeQuery()

            for entity_query in entity_queries_dict["entityQueries"]:
                # if "startDate" not in entity_query:
                #     entity_query["startDate"].CopyFrom(Time(year=1970, month=1, day=1))
                # else:
                #     entity_query["startDate"] = U.convert_python_time_to_proto_time(entity_query["startDate"])
                #
                # if "endDate" not in entity_query:
                #     entity_query["endDate"].CopyFrom(Time(year=1970, month=1, day=1))
                # else:
                #     entity_query["endDate"] = U.convert_python_time_to_proto_time(entity_query["endDate"])

                ent_q = EntityQuery(value=entity_query)
                entity_type_query.entityQuery.append(ent_q)

            case_msg.query[label].CopyFrom(entity_type_query)

        print(f"Passed the case submission payload to GraphExtractor at {dt.now()}")

        self.EXTRACTOR_CLIENT.StartGraphExtraction(case_msg)
        print(f"Returned from GraphExtractor at {dt.now()}. Should be negligible as implementing fire & forget")
        #
        # self.update_case_status(case_dict, "COMPLETE")
        # print(f"Updated case metadata again at {dt.now()}")

        return case_msg

    def generate_ego_network_for_vertex_id(self, search_id, selection, hops, data_sources, startTime, endTime, direction, dedup):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if selection is not None:
            if len(selection) > 1:
                return {"ERROR": f"Selection should be 1, got {len(selection)} and selection as {selection}", "nodes": [], "edges": []}
            else:
                selection = selection[0]

        if data_sources is not None:
            query = tr.V().withId(search_id).with_("dataSourceName", P.within(*data_sources))
        else:
            query = tr.V().withId(search_id)

        for i in range(hops):
            if selection is None:
                if startTime is not None and endTime is not None:
                    if data_sources is not None:
                        if direction == "both":
                            query = query.bothE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                        elif direction == "out":
                            query = query.outE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).inV().with_("dataSourceName", P.within(*data_sources))
                        else:
                            query = query.inE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).outV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        print("this sectipon")
                        # query = query.bothE("ip").with_("eventTime", P.between(startTime, endTime)).with_("counter", 10).otherV("test").withLabel("random").with_("p1", 100).outE("2").with_("counter", P.gte(2)).with_("eventTme", P.between(1, 5)).inV("2a").with_("22", 2).with_("33", 3)
                        if direction == "both":
                            query = query.bothE().with_("eventTime", P.between(startTime, endTime)).otherV()
                        elif direction == "out":
                            query = query.outE().with_("eventTime", P.between(startTime, endTime)).inV()
                        else:
                            query = query.inE().with_("eventTime", P.between(startTime, endTime)).outV()

                else:
                    if data_sources is not None:
                        query = query.bothE().with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE().otherV()
                        elif direction == "out":
                            query = query.outE().inV()
                        else:
                            query = query.inE().outV()
            else:
                if startTime is not None and endTime is not None:
                    if data_sources is not None:
                        if direction == "both":
                            query = query.bothE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                        elif direction == "out":
                            query = query.outE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).inV().with_("dataSourceName", P.within(*data_sources))
                        else:
                            query = query.inE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).outV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        print("this sectipon")
                        # query = query.bothE("ip").with_("eventTime", P.between(startTime, endTime)).with_("counter", 10).otherV("test").withLabel("random").with_("p1", 100).outE("2").with_("counter", P.gte(2)).with_("eventTme", P.between(1, 5)).inV("2a").with_("22", 2).with_("33", 3)
                        if direction == "both":
                            query = query.bothE(selection).with_("eventTime", P.between(startTime, endTime)).otherV()
                        elif direction == "out":
                            query = query.outE(selection).with_("eventTime", P.between(startTime, endTime)).inV()
                        else:
                            query = query.inE(selection).with_("eventTime", P.between(startTime, endTime)).outV()

                else:
                    if data_sources is not None:
                        query = query.bothE(selection).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE(selection).otherV()
                        elif direction == "out":
                            query = query.outE(selection).inV()
                        else:
                            query = query.inE(selection).outV()
        if dedup:
            result = query.project(C.all_()).dedup().next()
        else:
            result = query.project(C.all_()).next()

        return result

    def generate_ego_network_for_case_id(self, case_id, dedup, data_source, start_time, end_time):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if start_time is None and end_time is None and data_source is None:
            query = tr.V().withCaseId(case_id).both()
        else:
            if data_source is None:
                query = tr.V().withCaseId(case_id).bothE().with_("eventTime", P.between(start_time, end_time)).otherV()
            else:
                if start_time is None:
                    query = tr.V().withCaseId(case_id).bothE().with_("dataSourceName", P.within(data_source)).otherV()
                else:
                    query = tr.V().withCaseId(case_id).bothE().with_("dataSourceName", P.within(data_source)).with_("eventTime", P.between(start_time, end_time)).otherV()

        if dedup:
            result = query.project(C.all_()).dedup().next()
        else:
            result = query.project(C.all_()).next()

        return result

    def generate_ego_network_for_vertex_property(self, search_for, search_by, selection, hops, data_sources, startTime, endTime, direction, dedup):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if selection is not None:
            if len(selection) > 1:
                return {"ERROR": f"Selection should be 1, got {len(selection)} and selection as {selection}", "nodes": [], "edges": []}
            else:
                selection = selection[0]

        if data_sources is not None:
            query = tr.V().with_(search_for, search_by).with_("dataSourceName", P.within(*data_sources))
        else:
            query = tr.V().with_(search_for, search_by)

        for i in range(hops):
            if selection is None:
                if startTime is not None and endTime is not None:
                    if data_sources is not None:
                        if direction == "both":
                            query = query.bothE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                        elif direction == "out":
                            query = query.outE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).inV().with_("dataSourceName", P.within(*data_sources))
                        else:
                            query = query.inE().with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).outV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE().with_("eventTime", P.between(startTime, endTime)).otherV()
                        elif direction == "out":
                            query = query.outE().with_("eventTime", P.between(startTime, endTime)).inV()
                        else:
                            query = query.inE().with_("eventTime", P.between(startTime, endTime)).outV()

                else:
                    if data_sources is not None:
                        query = query.bothE().with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE().otherV()
                        elif direction == "out":
                            query = query.outE().inV()
                        else:
                            query = query.inE().outV()
            else:
                if startTime is not None and endTime is not None:
                    if data_sources is not None:
                        if direction == "both":
                            query = query.bothE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                        elif direction == "out":
                            query = query.outE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).inV().with_("dataSourceName", P.within(*data_sources))
                        else:
                            query = query.inE(selection).with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(*data_sources)).outV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE(selection).with_("eventTime", P.between(startTime, endTime)).otherV()
                        elif direction == "out":
                            query = query.outE(selection).with_("eventTime", P.between(startTime, endTime)).inV()
                        else:
                            query = query.inE(selection).with_("eventTime", P.between(startTime, endTime)).outV()

                else:
                    if data_sources is not None:
                        query = query.bothE(selection).with_("dataSourceName", P.within(*data_sources)).otherV().with_("dataSourceName", P.within(*data_sources))
                    else:
                        if direction == "both":
                            query = query.bothE(selection).otherV()
                        elif direction == "out":
                            query = query.outE(selection).inV()
                        else:
                            query = query.inE(selection).outV()

        if dedup:
            result = query.project(C.all_()).dedup().next()
        else:
            result = query.project(C.all_()).next()

        return result

    def get_vertex_by_id(self, search_id):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        result = tr.V().withId(search_id).properties().dedup().next()
        print(result)
        return result

    def get_vertex_by_property(self, search_for, search_by):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        result = tr.V().with_(search_for, search_by).properties().dedup().next()
        print(result)
        return result

    # def collapse_to_user_process_user_relation(self, node_id, startTime, endTime, data_sources):
    #     tr = GraphTraversal(self.SNOWGRAPH_CONN)
    #
    #     if startTime is None and endTime is None and dataSource is None:
    #         query = tr.V().as_("a").withId(node_id).union(
    #             __.both("resolved").out("hasIP"),
    #             __.out("hasIP")
    #         ).as_("b").out("runningProcess").as_("c").in_("runningProcess").union(__.in_("hasIP"), __.in_("hasIP").in_("resolved")).dedup().project()
    #
    #         query = traversal.V(vid).as_("srcUser"). \
    #             optional(__.both("resolved").out("hasIP").as_("withIP")). \
    #             optional(__.out("hasIP").as_("withIP")). \
    #             out("runningProcess").as_("proc"). \
    #             in_("runningProcess").where(P.neq("withIP")).as_("ip"). \
    #             in_("hasIP").in_("resolved").where(P.neq("srcUser")).as_("u"). \
    #             dedup(). \
    #             project("rootUser", "hasIP", "process", "throughIP", "userAffected"). \
    #             by(__.select("srcUser").valueMap(True)). \
    #             by(__.select("withIP").valueMap(True)). \
    #             by(__.select("proc").valueMap(True)). \
    #             by(__.select("ip").valueMap(True)). \
    #             by(__.select("u").valueMap(True))
    #     else:
    #         return {"ERROR": "Not implemented time filter and data source filter with user-process-user collapse api"}
    #     return

    def collapse_to_process_user_relation(self, node_id, startTime, endTime, dataSource):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id).both("downloadedOn").both("hasIP").dedup().project(C.all_())
            # query = tr.V().withId(node_id). \
            #     in_("runningProcess"). \
            #     in_("hasIP"). \
            #     dedup(). \
            #     project(C.all_())
        else:
            if dataSource is None:
                query = tr.V().withId(node_id).bothE("downloadedOn").with_("eventTime", P.between(startTime, endTime)).inV()\
                    .bothE("hasIP").with_("eventTime", P.between(startTime, endTime)).otherV()\
                    .dedup().project(C.all_())

                # query = tr.V().withId(node_id).\
                #     inE("runningProcess").with_("eventTime", P.between(startTime, endTime)).outV(). \
                #     inE("hasIP").with_("eventTime", P.between(startTime, endTime)).outV(). \
                #     dedup(). \
                #     project(C.all_())
            else:
                if startTime is not None:
                    query = tr.V().withId(node_id).bothE("downloadedOn").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).otherV() \
                        .bothE("hasIP").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).otherV() \
                        .dedup().project(C.all_())

                    # query = tr.V().withId(node_id).inE("runningProcess").\
                    #     with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV(). \
                    #     inE("hasIP").\
                    #         with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV().\
                    #     dedup().\
                    #     project(C.all_())
                else:
                    query = tr.V().withId(node_id).bothE("downloadedOn").with_("dataSourceName", P.within(dataSource)).otherV() \
                        .bothE("hasIP").with_("dataSourceName", P.within(dataSource)).otherV() \
                        .dedup().project(C.all_())

                    # query = tr.V().withId(node_id).inE("runningProcess").with_("dataSourceName", P.within(dataSource)).outV(). \
                    #     inE("hasIP").with_("dataSourceName", P.within(dataSource)).outV(). \
                    #     dedup(). \
                    #     project(C.all_())

            # return {"ERROR": "Not implemented time filter and data source filter with user-process-user collapse api"}

        data = query.next()

        print(data)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_to_process_ip_communicated(self, node_id, startTime, endTime, dataSource):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id).both("downloadedOn").both("IPsCommunicated").dedup().project(C.all_())

        else:
            if dataSource is None:
                query = tr.V().withId(node_id).bothE("downloadedOn").with_("eventTime", P.between(startTime, endTime)).inV() \
                    .bothE("IPsCommunicated").with_("eventTime", P.between(startTime, endTime)).otherV() \
                    .dedup().project(C.all_())

            else:
                if startTime is not None:
                    query = tr.V().withId(node_id).bothE("downloadedOn").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).otherV() \
                        .bothE("IPsCommunicated").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).otherV() \
                        .dedup().project(C.all_())

                else:
                    query = tr.V().withId(node_id).bothE("downloadedOn").with_("dataSourceName", P.within(dataSource)).otherV() \
                        .bothE("IPsCommunicated").with_("dataSourceName", P.within(dataSource)).otherV() \
                        .dedup().project(C.all_())

        data = query.next()

        print(data)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_to_user_process_relation(self, node_id, startTime, endTime, dataSource):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id). \
                union(__.both("resolved").out("hasIP"), __.out("hasIP")).\
                out("runningProcess").dedup().\
                project(C.all_())
        else:
            if dataSource is None:
                query = tr.V().withId(node_id). \
                    union(
                        __.bothE("resolved").with_("eventTime", P.between(startTime, endTime)).otherV()
                            .outE("hasIP").with_("eventTime", P.between(startTime, endTime)).inV(),
                        __.outE("hasIP").with_("eventTime", P.between(startTime, endTime)).inV()
                    ). \
                    outE("runningProcess").with_("eventTime", P.between(startTime, endTime)).inV().\
                    dedup(). \
                    project(C.all_())

            else:
                if startTime is not None:
                    query = tr.V().withId(node_id). \
                        union(
                        __.bothE("resolved").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).otherV()
                            .outE("hasIP").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV(),
                        __.outE("hasIP").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV()
                    ). \
                        outE("runningProcess").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV(). \
                        dedup(). \
                        project(C.all_())
                else:
                    query = tr.V().withId(node_id). \
                        union(
                        __.bothE("resolved").with_("dataSourceName", P.within(dataSource)).otherV()
                            .outE("hasIP").with_("dataSourceName", P.within(dataSource)).inV(),
                        __.outE("hasIP").with_("dataSourceName", P.within(dataSource)).inV()
                    ). \
                        outE("runningProcess").with_("dataSourceName", P.within(dataSource)).inV(). \
                        dedup(). \
                        project(C.all_())

            # return {"ERROR": "Not implemented time filter and data source filter with user-process-user collapse api"}

        data = query.next()

        print(data)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_to_user_email_user_relation(self, node_id, startTime, endTime, dataSource):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id). \
                in_("receivedEmail").withLabel("email"). \
                in_("sentEmail").withLabel("user"). \
                out("sentEmail").withLabel("email"). \
                out("receivedEmail").withLabel("user"). \
                out("clicked").withLabel("URL"). \
                project(C.all_())

        else:
            if dataSource is None:
                query = tr.V().withId(node_id).\
                    inE("receivedEmail").with_("emailTime", P.between(startTime, endTime)).outV().withLabel("email"). \
                    inE("sentEmail").with_("emailTime", P.between(startTime, endTime)).outV().withLabel("user"). \
                    outE("receivedEmail").with_("emailTime", P.between(startTime, endTime)).inV().withLabel("email"). \
                    outE("sentEmail").with_("emailTime", P.between(startTime, endTime)).inV().withLabel("user"). \
                    outE("clicked").with_("eventTime", P.between(startTime, endTime)).inV().withLabel("URL"). \
                    project(C.all_())

            else:
                if startTime is not None:
                    query = tr.V().withId(node_id). \
                        inE("receivedEmail").with_("emailTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV().withLabel("email"). \
                        inE("sentEmail").with_("emailTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV().withLabel("user"). \
                        outE("receivedEmail").with_("emailTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV().withLabel("email"). \
                        outE("sentEmail").with_("emailTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV().withLabel("user"). \
                        outE("clicked").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).inV().withLabel("URL"). \
                        project(C.all_())
                else:
                    query = tr.V().withId(node_id). \
                        inE("receivedEmail").with_("dataSourceName", P.within(dataSource)).outV().withLabel("email"). \
                        inE("sentEmail").with_("dataSourceName", P.within(dataSource)).outV().withLabel("user"). \
                        outE("receivedEmail").with_("dataSourceName", P.within(dataSource)).inV().withLabel("email"). \
                        outE("sentEmail").with_("dataSourceName", P.within(dataSource)).inV().withLabel("user"). \
                        outE("clicked").with_("dataSourceName", P.within(dataSource)).inV().withLabel("URL"). \
                        project(C.all_())

                # return {"ERROR": "Not implemented time filter and data source filter with user-process-user collapse api"}

        data = query.next()

        # print(data)
        nodes = data["nodes"]
        edges = data["edges"]
        graph = {"nodes": [], "edges": []}
        # for node in nodes:
        #     if node["lvl"] in [3, 4, 5, 6]:
        #         graph["nodes"].append(node)
        #
        # for edge in edges:
        #     if edge["lvl"] in [4, 5, 6]:
        #         graph["edges"].append(edge)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_user_URL_user_relation(self, node_id, start_time, end_time, data_sources):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if start_time is None and end_time is None and data_sources is None:
            query = tr.V().withId(node_id). \
                out("clicked"). \
                in_("clicked"). \
                dedup(). \
                project(C.all_())
        else:
            print(start_time, end_time, data_sources)
            if data_sources is None:
                print("Data source is not none but time is")
                query = tr.V().withId(node_id). \
                    outE("clicked").with_("eventTime", P.between(start_time, end_time)).inV(). \
                    inE("clicked").with_("eventTime", P.between(start_time, end_time)).outV(). \
                    dedup(). \
                    project(C.all_())
            else:
                if start_time is None:
                    query = tr.V().withId(node_id). \
                        outE("clicked").with_("dataSourceName", P.within(data_sources)).inV(). \
                        inE("clicked").with_("dataSourceName", P.within(data_sources)).outV(). \
                        dedup(). \
                        project(C.all_())
                else:
                    query = tr.V().withId(node_id). \
                        outE("clicked").with_("eventTime", P.between(start_time, end_time)).with_("dataSourceName", P.within(data_sources)).inV(). \
                        inE("clicked").with_("eventTime", P.between(start_time, end_time)).with_("dataSourceName", P.within(data_sources)).outV(). \
                        dedup(). \
                        project(C.all_())

            # return {"ERROR": "Not implemented time filter and data source filter with user-URL-user collapse api"}

        data = query.next()

        print(data)

        nodes = data["nodes"]
        edges = data["edges"]
        # graph = {"nodes": [], "edges": []}
        # for node in nodes:
        #     if node["lvl"] == 3:
        #         graph["nodes"].append(node)
        #
        # for edge in edges:
        #     if edge["lvl"] == 3:
        #         graph["edges"].append(edge)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_ip_user_relation(self, node_id, startTime, endTime, dataSource):
        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id). \
                union(__.in_("hasIP"), __.in_("userInteracted")). \
                project(C.all_()). \
                dedup()
        else:
            if dataSource is None:
                query = tr.V().withId(node_id). \
                    union(
                    __.inE("hasIP").with_("eventTime", P.between(startTime, endTime)).outV().withLabel("user"),
                    __.inE("userInteracted").with_("eventTime", P.between(startTime, endTime)).withLabel("user")
                ).project(C.all_()).dedup()
            else:
                if startTime is not None:
                    query = tr.V().withId(node_id). \
                        union(
                        __.inE("hasIP").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV().withLabel("user"),
                        __.inE("userInteracted").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).withLabel("user")
                    ).project(C.all_()).dedup()
                else:
                    query = tr.V().withId(node_id). \
                        union(
                        __.inE("hasIP").with_("dataSourceName", P.within(dataSource)).outV().withLabel("user"),
                        __.inE("userInteracted").with_("dataSourceName", P.within(dataSource)).withLabel("user")
                    ).project(C.all_()).dedup()

        data = query.next()

        print(data)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_process_ip_relation(self, node_id, startTime, endTime, dataSource):
        """

        Args:
            vid (long):
            graph (JanusGraph):

        Returns:

        """

        tr = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and dataSource is None:
            query = tr.V().withId(node_id). \
                in_("runningProcess"). \
                project(C.all_()).dedup()
        else:
            if dataSource is None:
                query = tr.V().withId(node_id).inE("runningProcess").with_("eventTime", P.between(startTime, endTime)).outV().\
                    project(C.all_()).dedup()
            else:
                if startTime is not None:
                    query = tr.V().withId(node_id).inE("runningProcess").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(dataSource)).outV(). \
                        project(C.all_()).dedup()
                else:
                    query = tr.V().withId(node_id).inE("runningProcess").with_("dataSourceName", P.within(dataSource)).outV(). \
                        project(C.all_()).dedup()

        data = query.next()

        print(data)

        print("Number of nodes: ", len(data["nodes"]))
        print("Number of edges: ", len(data["edges"]))

        return data

    def collapse_process_communicated(self, vid, startTime, endTime, timeWindow=None):
        """

        Args:
            vid (long):
            graph (JanusGraph):

        Returns:

        """

        if timeWindow is None:
            timeWindow = "1d"

        traversal = GraphTraversal(self.SNOWGRAPH_CONN)

        # First we need to find the downloaded time of process. Then use that to fetch query. EndTime will be 24hours more

        downloadTime = traversal.V().withId(vid). \
            coalesce(
            __.outE().has("edge_label", "downloadedOn"),
            __.outE().has("edge_label", "childProcessOn")
        ). \
            values("eventTime").dedup().toList()

        # Time range will be first fetch min time, then add 12 hours to max time and fetch.
        beginTime = min(downloadTime)
        if "h" in timeWindow:
            stopTime = beginTime + dt.timedelta(hours=int(timeWindow.split("h")[0]))
        elif "m" in timeWindow:
            stopTime = beginTime + dt.timedelta(minutes=int(timeWindow.split("m")[0]))
        elif "d" in timeWindow:
            stopTime = beginTime + dt.timedelta(days=int(timeWindow.split("d")[0]))
        else:
            stopTime = beginTime + dt.timedelta(seconds=int(timeWindow.split("s")[0]))

        timePredicate = P.and_(P.gte(beginTime), P.lt(stopTime))
        print(timePredicate)

        if startTime is None and endTime is None:
            query = traversal.V(vid).as_("p"). \
                coalesce(
                __.outE().has("edge_label", "downloadedOn").inV().has("node_label", "IP"),
                __.outE().has("edge_label", "childProcessOn").inV().has("node_label", "hosts"). \
                    outE().has("edge_label", "withIP").inV().has("node_label", "IP")
            ).as_("ip"). \
                outE().has("edge_label", "IPsCommunicated").has("eventTime", timePredicate).inV().has("node_label", "IP").as_("dst"). \
                project("process", "hostIP", "destinationIP", "hostID", "dstID"). \
                by(__.select("p").valueMap(True)). \
                by(__.select("ip").valueMap("node_label", "ip", "dataSourceName")). \
                by(__.select("dst").valueMap("node_label", "ip", "dataSourceName")). \
                by(__.select("ip").id()). \
                by(__.select("dst").id()). \
                dedup("process", "hostIP", "destinationIP")
        else:
            query = traversal.V(vid).as_("p"). \
                coalesce(
                __.outE().has("edge_label", "downloadedOn").inV().has("node_label", "IP"),
                __.outE().has("edge_label", "childProcessOn").inV().has("node_label", "hosts"). \
                    outE().has("edge_label", "withIP").inV().has("node_label", "IP")
            ).as_("ip"). \
                outE().has("edge_label", "IPsCommunicated").inV().has("node_label", "IP").as_("dst"). \
                project("process", "hostIP", "destinationIP", "hostID", "dstID"). \
                by(__.select("p").valueMap(True)). \
                by(__.select("ip").valueMap("node_label", "ip", "dataSourceName")). \
                by(__.select("dst").valueMap("node_label", "ip", "dataSourceName")). \
                by(__.select("ip").id()). \
                by(__.select("dst").id()). \
                dedup()

        data = query.toList()

    def collapse_process_downloaded_on(self, vid, start_time, end_time, data_sources):
        """

        Args:
            vid (long):
            graph (JanusGraph):

        Returns:

        """

        traversal = GraphTraversal(self.SNOWGRAPH_CONN)

        if start_time is None and end_time is None and data_sources is None:
            query = traversal.V().withId(vid). \
                coalesce(
                    __.outE("downloadedOn").inV("IP"),
                    __.outE("childProcessOn").inV("hosts"),
                ). \
                project(C.all_()).dedup()
        else:
            if data_sources is None:
                query = traversal.V().withId(vid). \
                    coalesce(
                    __.outE("downloadedOn").with_("eventTime", P.between(start_time, end_time)).inV("IP"),
                    __.outE("childProcessOn").with_("eventTime", P.between(start_time, end_time)).inV("hosts"),
                ). \
                project(C.all_()).dedup()
            else:
                if start_time is not None:
                    query = traversal.V().withId(vid). \
                        coalesce(
                        __.outE("downloadedOn").with_("eventTime", P.between(start_time, end_time)).with_("dataSourceName", P.within(data_sources)).inV("IP"),
                        __.outE("childProcessOn").with_("eventTime", P.between(start_time, end_time)).with_("dataSourceName", P.within(data_sources)).inV("hosts"),
                    ). \
                    project(C.all_()).dedup()
                else:
                    query = traversal.V().withId(vid). \
                        coalesce(
                        __.outE("downloadedOn").with_("dataSourceName", P.within(data_sources)).inV("IP"),
                        __.outE("childProcessOn").with_("dataSourceName", P.within(data_sources)).inV("hosts"),
                    ). \
                        project(C.all_()).dedup()

        # query = traversal.V().withId(vid). \
        #     coalesce(
        #     __.outE("downloadedOn").inV("IP"),
        #     __.outE("childProcessOn").inV("hosts"),
        # ). \
        #     project(C.all_()).dedup()

        data = query.next()

        return data

    def collapse_user_loggedin_host_relation(self, vid, startTime, endTime, data_source):
        traversal = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and data_source is not None:
            query = traversal.V().withId(vid). \
                outE("loggedIn").inV("IP"). \
                project(C.all_()).dedup()
        else:
            if data_source is None:
                query = traversal.V().withId(vid). \
                    outE("loggedIn").with_("eventTime", P.between(startTime, endTime)).inV("IP"). \
                    project(C.all_()).dedup()
            else:
                if startTime is not None:
                    query = traversal.V().withId(vid). \
                        outE("loggedIn").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(data_source)).inV("IP"). \
                        project(C.all_()).dedup()
                else:
                    query = traversal.V().withId(vid). \
                        outE("loggedIn").with_("dataSourceName", P.within(data_source)).inV("IP"). \
                        project(C.all_()).dedup()

        data = query.next()
        return data

    def collapse_user_clicked_url(self, vid, startTime, endTime, data_source):
        traversal = GraphTraversal(self.SNOWGRAPH_CONN)

        if startTime is None and endTime is None and data_source is None:
            query = traversal.V().withId(vid).out("clicked").withLabel("URLs").project(C.all_()).dedup()

        else:
            if data_source is None:
                query = traversal.V().withId(vid).outE("clicked").with_("eventTime", P.between(startTime, endTime)).inV("URLs").project(C.all_()).dedup()
            else:
                if startTime is not None:
                    query = traversal.V().withId(vid).outE("clicked").with_("eventTime", P.between(startTime, endTime)).with_("dataSourceName", P.within(data_source)).inV("URLs").project(C.all_()).dedup()
                else:
                    query = traversal.V().withId(vid).outE("clicked").with_("dataSourceName", P.within(data_source)).inV("URLs").project(C.all_()).dedup()

        data = query.next()
        return data
