import gen.graphdb_pb2_grpc as graphdb_pb2_grpc
import gen.graphdb_pb2 as graphdb_pb2
from time import sleep
import grpc, json, datetime as dt, threading
from utils.constants import Commons, APPLICATION_PROPERTIES
from client.connection.SnowGraphConnection import SnowGraphConnection
from client.traversal.GraphTraversal import GraphTraversal
from gen.graphdb_pb2_grpc import ServicesToGraphCoreStub
from google.protobuf.json_format import MessageToDict
from loader.GraphLoader import GraphLoader


class GraphLoaderController(graphdb_pb2_grpc.ServicesToGraphLoaderServicer):

    def __init__(self):
        resource_properties = Commons.load_properties(APPLICATION_PROPERTIES)

        self.BATCH_SIZE = 10000

        MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
        ]

        core_host = resource_properties["grpc.core.server.host"]
        core_port = int(resource_properties["grpc.core.server.port"])
        url = f'{core_host}:{core_port}'

        self.core_channel = grpc.insecure_channel(url, options=options)
        self.CORE_CLIENT = ServicesToGraphCoreStub(channel=self.core_channel)
        print(f"Initialized connection to core client to URL: {url} in constructor")

        conn = SnowGraphConnection()
        conn.set_host(core_host)
        conn.set_port(core_port)
        self.traversal = GraphTraversal(conn)
        print(f"Initialized connection to SnowGraph Server {self.traversal} with URL: {core_host} & PORT: {core_port}")

        dbi = graphdb_pb2.DataBaseIdentifier(database="snowflake_graph_test", schema="snowgraph_demo", caller="python")
        self.credentials = self.CORE_CLIENT.GetSnowFlakeCredentials(dbi)
        # print(f"Queried graph core for credentials & the credentials are {self.credentials}")

    def load_data_to_snowflake(self, request_iterator):
        graph = {
            "nodes": [],
            "edges": []
        }

        case_id = None
        print("Starting to merge data from stream input in GraphLoader and load in batches")
        print(f"Total size of data is {len(request_iterator)}")

        # Custom logic for batching of graph data
        # graphs = []
        nodes = []
        i = 0
        batch_num = 1
        MAX_BATCHES = 5
        record_batches = Commons.chunks(request_iterator, self.BATCH_SIZE)
        for batch in record_batches:
            print(f"Starting loading for batch {batch_num}")
            for record in batch:
                case_id = record.caseId
                data_type = record.WhichOneof('data')
                if data_type == "node":
                    graph["nodes"].append(MessageToDict(getattr(record, data_type)))
                else:
                    graph["edges"].append(MessageToDict(getattr(record, data_type)))

                if i == 0:
                    procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
                    loading_status = graphdb_pb2.CaseLoadingStatus(status=f"Dataload Started", caseId=case_id, processingTime=procTime)
                    self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

                i += 1

            print(f"Finished batch number {batch_num} with nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")

            loader = GraphLoader(graph)
            loader.with_traversal(self.traversal)
            loader.convert()
            loader.load()

            procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
            loading_status = graphdb_pb2.CaseLoadingStatus(status=f"Loaded batch {batch_num}", caseId=case_id, processingTime=procTime)
            self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

            nodes.extend(loader.NODES_IN_CASE)

            print(f"Finished Loading batch number {batch_num} with nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")

            # path = f"../../resources/dumps/{case_id}_batch_{batch_num}_graph.json"
            # json.dump(graph, open(path, "w+"))
            # print(f"Dumped graph for batch {batch_num} to {path}")

            # graphs.append(graph)
            graph = {
                "nodes": [],
                "edges": []
            }
            batch_num += 1

            if batch_num >= MAX_BATCHES:
                print("Going to break out as I'm going to test only till batch size of 5 in loading")
                break
                #
                #
                # if i < (batch_num * self.BATCH_SIZE):
                #     case_id = record.caseId
                #
                #     data_type = record.WhichOneof('data')
                #     if data_type == "node":
                #         graph["nodes"].append(MessageToDict(getattr(record, data_type)))
                #     else:
                #         graph["edges"].append(MessageToDict(getattr(record, data_type)))
                #
                #     if i == 0:
                #         procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
                #         loading_status = graphdb_pb2.CaseLoadingStatus(status=f"Dataload Started", caseId=case_id, processingTime=procTime)
                #         self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
                #
                # else:
                #     print(f"Finished batch number {batch_num} with nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")
                #
                #     loader = GraphLoader(graph)
                #     loader.with_traversal(self.traversal)
                #     loader.convert()
                #     loader.load()
                #
                #     procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
                #     loading_status = graphdb_pb2.CaseLoadingStatus(status=f"Loaded batch {batch_num}", caseId=case_id, processingTime=procTime)
                #     self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
                #
                #     nodes.extend(loader.NODES_IN_CASE)
                #
                #     print(f"Finished Loading batch number {batch_num} with nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")
                #
                #     path = f"../../resources/dumps/{case_id}_batch_{batch_num}_graph.json"
                #     json.dump(graph, open(path, "w+"))
                #     print(f"Dumped graph for batch {batch_num} to {path}")
                #
                #     # graphs.append(graph)
                #     graph = {
                #         "nodes": [],
                #         "edges": []
                #     }
                #     batch_num += 1
                #
                # # case_id = record.caseId
                # #
                # # data_type = record.WhichOneof('data')
                # # if data_type == "node":
                # #     graph["nodes"].append(MessageToDict(getattr(record, data_type)))
                # # else:
                # #     graph["edges"].append(MessageToDict(getattr(record, data_type)))
                # #
                # i += 1
                #
                # if batch_num >= MAX_BATCHES:
                #     print("Going to break out as I'm going to test only till batch size of 5 in loading")
                #     break

        print("Loading started for case " + str(case_id))

        # json.dump(graph, open(f"../../resources/dumps/Case_{case_id}_graph_data.json", "w+"), indent=2)
        print("Dumped the data to resources/dumps file for the case")

        # if case_id is not None:
        #     nodes = []
        #     for i in range(len(graphs)):
        #         graph = graphs[i]
        #         print(f"Loading the batch {i+1} with nodes: {len(graph['nodes'])} and edges: {len(graph['edges'])}")
        #         loader = GraphLoader(graph)
        #         loader.with_traversal(self.traversal)
        #         loader.convert()
        #         loader.load()
        #
        #         nodes.extend(loader.NODES_IN_CASE)

        # nodes_in_case = Commons.node_list_to_update_case_properties(nodes[:1000], case_id)

        sleep(10)
        print("Data loading over")
        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Data Load Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        sleep(10)

        # nodes_in_record_it = Commons.node_list_to_case_node_iterator(nodes, case_id)
        # self.CORE_CLIENT.UpdateNodesForCase(nodes_in_record_it)

        # self.CORE_CLIENT.UpdateCaseLoadingProperties(nodes_in_case)
        print("Updated the nodes which were added as part of node")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Export Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

    def EnsureGraphInSnowFromFromTable(self, request, context):
        # print(request)
        table = request.table
        case_id = request.caseId
        # nodes_proto = request.nodes

        print("Read in incoming params")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Data load started", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        print("Updated status in case table")

        # nodes = [MessageToDict(n) for n in nodes_proto]
        # import pprint
        # pprint.pprint(nodes)
        # print("Generatied nodes as list of dict from Node Repeated Container")
        # nodes_in_record_it = Commons.node_list_to_case_node_iterator(nodes, case_id)
        # print("Generted nodes iterator")
        # self.CORE_CLIENT.UpdateNodesForCase(nodes_in_record_it)
        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Nodes for case updated", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        print("Updated the nodes in case table")

        params = graphdb_pb2.ProcedureParams()
        # params.procedure = "SP_GRAPH_NODE_LOAD"
        params.procedure = self.credentials.additionalParameters["nodes_load_stored_procedure"]
        order = self.credentials.additionalParameters["nodes_load_stored_procedure_order"].split(",")
        params.order[:] = order
        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["TARGET_NODE_TBL"] = "DEFAULT"
        params.parameters["TRANSFORMED_TBL"] = self.credentials.additionalParameters["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Loaded nodes")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Nodes Loaded", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        # params.procedure = "SP_GRAPH_EDGE_LOAD"
        params.procedure = self.credentials.additionalParameters["edges_load_stored_procedure"]
        order = self.credentials.additionalParameters["edges_load_stored_procedure_order"].split(",")
        params.order[:] = order
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["TARGET_EDGE_TBL"] = "DEFAULT"
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Loaded edges")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Edges Loaded", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        # params.procedure = "LOAD_NODES_FOR_CASE"
        params.procedure = self.credentials.additionalParameters["nodes_for_case_load_stored_procedure"]
        order = self.credentials.additionalParameters["nodes_for_case_load_stored_procedure_order"].split(",")
        params.order[:] = order
        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["TRANSFORMED_TBL"] = self.credentials.additionalParameters["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Loaded nodes for case")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Loaded nodes for case", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Export Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Data load & Export complete")

        return graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

    def EnsureGraphInSnowFlakeStream(self, request_iterator, context):

        datasets = []
        for record in request_iterator:
            datasets.append(record)

        print("Going to start data loading in thread")
        t = threading.Thread(target=self.load_data_to_snowflake, kwargs={"request_iterator": datasets})
        print("Created dataload thread")
        t.start()
        # t.join()

        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

        print("Returning back from graph loader with empty msg")
        print("============")

        return empty

    def EnsureGraphInSnowFlake(self, request, context):

        case_id = request.caseId
        print("Loading started for case " + str(case_id))

        loading_status = graphdb_pb2.CaseLoadingStatus(status="Data Load Started", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        graph_data = MessageToDict(request)
        # json.dump(graph_data, open(f"../../resources/dumps/Case_{case_id}_graph_data.json", "w+"), indent=2)
        # print("Dumped the data to resources/dumps file for the case")

        loader = GraphLoader(graph_data)
        loader.with_traversal(self.traversal)
        loader.convert()
        loader.load()

        # nodes_in_case = Commons.node_list_to_update_case_properties(loader.NODES_IN_CASE, case_id)

        sleep(10)
        print("Data loading over")
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Data Load Complete", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        sleep(10)

        # self.CORE_CLIENT.UpdateCaseLoadingProperties(nodes_in_case)
        # print("Updated the nodes which were added as part of node")

        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

        loading_status = graphdb_pb2.CaseLoadingStatus(status="Export Complete", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print("Returning back from graph loader with empty msg")
        print("============")

        return empty

# support@cleartax.in
