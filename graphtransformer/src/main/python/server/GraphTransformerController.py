import gen.graphdb_pb2_grpc as graphdb_pb2_grpc
import gen.graphdb_pb2 as graphdb_pb2
from executor.TransformAndLoader import Loader
from utils.sample_data_gen import SampleDataGenerator
import datetime as dt
from time import sleep
import grpc, json, os
from utils.constants import Commons, APPLICATION_PROPERTIES
from process.IncomingDataToGraphTransformer import IncomingDataToGraphTransformer
from gen.graphdb_pb2_grpc import ServicesToGraphCoreStub, ServicesToGraphLoaderStub
from google.protobuf.json_format import MessageToDict
from pyspark.sql import *
from pyspark.sql.functions import udf, monotonically_increasing_id, array
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType, MapType
from utils.use_databricks import apply_node_transformation_to_records, apply_edge_transformation_to_records
from utils.test_dedup import generate_identifier
from utils.test_dedup_2 import convert_to_json_from_str
import threading
import pandas as pd
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL


class GraphTransformerController(graphdb_pb2_grpc.ServicesToGraphTransformerServicer):

    def __init__(self):
        self.DATAMAPPERS = {}

        self.MINI_STREAM = False

        resource_properties = Commons.load_properties(APPLICATION_PROPERTIES)

        self.USE_SPARK = resource_properties["databricks"] == "true"

        MAX_MESSAGE_LENGTH = 250 * 1024 * 1024
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
        ]

        url = f'{resource_properties["grpc.core.server.host"]}:{resource_properties["grpc.core.server.port"]}'
        self.core_channel = grpc.insecure_channel(url, options=options)
        self.CORE_CLIENT = ServicesToGraphCoreStub(channel=self.core_channel)
        print(f"Initialized connection to core client to URL: {url} in constructor")

        url = f'{resource_properties["grpc.loader.server.host"]}:{resource_properties["grpc.loader.server.port"]}'
        self.loader_channel = grpc.insecure_channel(url, options=options)
        self.LOADER_CLIENT = ServicesToGraphLoaderStub(channel=self.loader_channel)
        print(f"Initialized connection to loader client to URL: {url} in constructor")

        self.spark = SparkSession \
            .builder.appName("test"). \
            config("spark.app.id", 123). \
            config("spark.driver.memory", "15g"). \
            getOrCreate()
        self.sc = self.spark.sparkContext
        self.sc.setLogLevel("ERROR")

        dbi = graphdb_pb2.DataBaseIdentifier(database="snowflake_graph_test", schema="snowgraph_demo", caller="python")
        self.credentials = MessageToDict(self.CORE_CLIENT.GetSnowFlakeCredentials(dbi))
        print(f"Queried graph core for credentials & the credentials are {self.credentials}")

    def loader_data_proto_iterator(self, graph, caseid):
        nodes = graph["nodes"]
        edges = graph["edges"]
        nodes_l = len(nodes)
        edges_l = len(edges)

        graph_data = nodes + edges
        for i in range(len(graph_data)):
            data = graph_data[i]
            data_type = "node" if i < nodes_l else "edge"

            if data_type == "node":
                elem = graphdb_pb2.Node()
                for k, v in data.items():
                    vv = Commons._convert_value_to_struct_value_(v)
                    elem.properties[k].CopyFrom(vv)
                dataset = graphdb_pb2.GraphLoaderDataFormat(caseId=caseid)
                dataset.node.CopyFrom(elem)

            else:
                elem = graphdb_pb2.Edge()
                for k, v in data.items():
                    vv = Commons._convert_value_to_struct_value_(v)
                    elem.properties[k].CopyFrom(vv)
                dataset = graphdb_pb2.GraphLoaderDataFormat(caseId=caseid)
                dataset.edge.CopyFrom(elem)

            yield dataset

    def load_datamapper(self, ds):
        properties = Commons.load_properties(APPLICATION_PROPERTIES)
        print("loaded properties")
        datamapper_file = properties[f"graph.{ds}.datamapper"]
        print("read data mapper file name")
        dm = json.load(open(os.path.abspath(properties["resource.path"] + datamapper_file))) if datamapper_file != "" else {}
        print("read datamapper")
        if ds not in self.DATAMAPPERS:
            self.DATAMAPPERS[ds] = dm
        print(self.DATAMAPPERS)
        return dm

    def get_unique_identifier_of_node_for_label(self, node):
        label = node["node_label"]
        ds = node["dataSourceName"]
        dm = Commons.get_datamapper(ds)["nodes"]
        for type_node, mapper in dm.items():
            if label.lower() == type_node.lower():
                return mapper["constraints"]["unique"]

    def batch_data_transformation(self, request_iterator, case_id, st):
        windows = []
        msexchange = []
        sysmon = []
        wgtraffic = []
        sepc = []

        print("Data aggregation in transformer started for " + str(case_id), dt.datetime.now())
        start = dt.datetime.now()
        initial_update = True
        idx = 0
        for record in request_iterator:
            # print(f"IDX: {idx} and Record: {record}")
            case_id = record.caseId

            if initial_update:
                procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
                loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

                start = dt.datetime.now()
                procTime = Commons.convert_python_time_to_proto_time(start)
                loading_status = graphdb_pb2.CaseLoadingStatus(status="Data aggregation Started", caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
                initial_update = False

            data_type = record.WhichOneof('data')
            if data_type == "windowsRecord":
                windows.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "exchangeRecord":
                msexchange.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "sysmonRecord":
                sysmon.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "sepcRecord":
                sepc.append(MessageToDict(getattr(record, data_type)))
            else:
                wgtraffic.append(MessageToDict(getattr(record, data_type)))

            print(f"Record sizes windows: {len(windows)}, exchange: {len(msexchange)}, sysmon: {len(sysmon)}, "
                  f"sepc: {len(sepc)}, network: {len(wgtraffic)}")

            idx += 1

        end = dt.datetime.now()
        procTime = Commons.convert_python_time_to_proto_time(end)
        duration = (end-start).total_seconds()
        status = f"Transformer incoming data aggregated. Duration (sec): {duration}. Record sizes windows: " \
            f"{len(windows)}, exchange: {len(msexchange)}, sysmon: {len(sysmon)}, sepc: {len(sepc)}, " \
            f"network: {len(wgtraffic)}"
        loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print("Transformation started")
        start = dt.datetime.now()
        procTime = Commons.convert_python_time_to_proto_time(start)
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation started", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print("Split the incoming records by iterating over everything creating respective lists")
        data = {
            "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
            "networkRecords": wgtraffic, "sepcRecords": sepc
        }

        print("windows of len ", len(windows))
        print("msexchange of len ", len(msexchange))
        print("sysmon of len ", len(sysmon))
        print("wgtraffic of len ", len(wgtraffic))
        print("symantec of len ", len(sepc))
        print(f"Total len: {len(windows) + len(msexchange) + len(sysmon) + len(wgtraffic) + len(sepc)}")

        convertor = IncomingDataToGraphTransformer(data)
        graph = convertor.convert()
        print("Converted Incoming data to Graph")

        end = dt.datetime.now()
        procTime = Commons.convert_python_time_to_proto_time(end)
        duration = (end-start).total_seconds()
        status = f"Transformation completed. Duration (sec): {duration}. Record sizes nodes: " \
            f"{len(graph['nodes'])}, edges: {len(graph['edges'])}"
        loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print(f"All Graph transformation operaionts over in {dt.datetime.now()-st}")
        return graph

    def mini_stream_data_transformation(self, request_iterator, case_id, st):
        windows = []
        msexchange = []
        sysmon = []
        wgtraffic = []
        sepc = []

        initial_update = True
        idx = 0
        batch = 50000
        batch_num = 1

        nodes = []
        edges = []

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        start = dt.datetime.now()
        for record in request_iterator:
            if batch_num == 5:
                print(len(windows), len(msexchange), len(sysmon), len(sepc), len(wgtraffic), record, "\n====")
            case_id = record.caseId

            if initial_update:
                print("Data aggregation in transformer started for " + str(case_id), dt.datetime.now())

                start = dt.datetime.now()
                procTime = Commons.convert_python_time_to_proto_time(start)
                loading_status = graphdb_pb2.CaseLoadingStatus(status=f"Batch {batch_num} Data aggregation Started", caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
                initial_update = False

            data_type = record.WhichOneof('data')
            if data_type == "windowsRecord":
                windows.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "exchangeRecord":
                msexchange.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "sysmonRecord":
                sysmon.append(MessageToDict(getattr(record, data_type)))
            elif data_type == "sepcRecord":
                sepc.append(MessageToDict(getattr(record, data_type)))
            else:
                wgtraffic.append(MessageToDict(getattr(record, data_type)))

            if batch_num == 5:
                print("After append ", len(windows), len(msexchange), len(sysmon), len(sepc), len(wgtraffic))

            if idx >= (batch_num*batch):
                end = dt.datetime.now()
                procTime = Commons.convert_python_time_to_proto_time(end)
                status = f"Batch {batch_num} Data aggregation completed. Duration (s): {(end-start).total_seconds()}"
                loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

                print(f"Aggregated batch {batch_num} for transformation at ", dt.datetime.now())

                start = dt.datetime.now()
                procTime = Commons.convert_python_time_to_proto_time(start)
                status = f"Batch {batch_num} Transformation started"
                loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

                data = {
                    "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
                    "networkRecords": wgtraffic, "sepcRecords": sepc
                }

                convertor = IncomingDataToGraphTransformer(data)
                graph = convertor.convert()
                print(f"Generated graph for batch {batch_num} with nodes: {len(graph['nodes'])} & edges: {len(graph['edges'])}")

                end = dt.datetime.now()
                print(start, end)
                duration = (end-start).total_seconds()
                print(f"Duration: {duration}")
                procTime = Commons.convert_python_time_to_proto_time(end)
                print(f"Processing time in Proto:\n{procTime}")
                status = f"Batch {batch_num} Transformation completed. Duration (s): {duration}, " \
                    f"Windows: {len(windows)}, Exchange: {len(msexchange)}, SysMon: {len(sysmon)}, " \
                    f"Network: {len(wgtraffic)}, SEPC: {len(sepc)}"
                print(f"Status to be updated is: {status}")
                loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
                print("Case loading status obj created")
                self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
                print("Status updated in Core")

                print(f"Transformed batch {batch_num} at {dt.datetime.now()}")

                nodes.append(graph["nodes"])
                edges.append(graph["edges"])

                windows = []
                msexchange = []
                sysmon = []
                wgtraffic = []
                sepc = []

                batch_num += 1
                initial_update = True
                print(f"Starting next iteration for batch {batch_num} and idx: {idx} and size: {batch}")

            idx += 1

        print("Iterated over all records done")

        if (batch_num == 1):# and (len(windows) > 0 or len(msexchange) > 0 or len(sysmon) > 0 or len(wgtraffic) > 0 or len(sepc) > 0):
            # Meaning that the total records less than specified batch size
            print(f"The total num records {idx} is less than batch size {batch}, so going to convert")

            end = dt.datetime.now()
            procTime = Commons.convert_python_time_to_proto_time(end)
            status = f"Batch {batch_num} Data aggregation completed. Duration (s): {(end-start).total_seconds()}"
            loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
            self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

            print(f"Aggregated batch {batch_num} for transformation at ", dt.datetime.now())

            start = dt.datetime.now()
            procTime = Commons.convert_python_time_to_proto_time(start)
            status = f"Batch {batch_num} Transformation started"
            loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
            self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

            data = {
                "windowsRecords": windows, "exchangeRecords": msexchange, "sysmonRecords": sysmon,
                "networkRecords": wgtraffic, "sepcRecords": sepc
            }

            convertor = IncomingDataToGraphTransformer(data)
            graph = convertor.convert()

            end = dt.datetime.now()
            duration = (end-start).total_seconds()
            procTime = Commons.convert_python_time_to_proto_time(end)
            status = f"Batch {batch_num} Transformation completed. Duration (s): {duration}, " \
                f"Windows: {len(windows)}, Exchange: {len(msexchange)}, SysMon: {len(sysmon)}, " \
                f"Network: {len(wgtraffic)}, SEPC: {len(sepc)}"
            loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
            self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

            nodes.append(graph["nodes"])
            edges.append(graph["edges"])

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformer Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
        print("Transformation completed", dt.datetime.now())

        start = dt.datetime.now()
        procTime = Commons.convert_python_time_to_proto_time(start)
        tot_nodes = sum([len(x) for x in nodes])
        tot_edges = sum([len(x) for x in edges])
        status = f"Deduplicated nodes and edges across batches. Batch: {len(nodes)}, Nodes: {tot_nodes}, Edges: {tot_edges}"
        loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
        print("Deduplicating batched graphs", dt.datetime.now())

        nodes_dedup = {}
        edges_dedup = {}
        x = 1
        for nodes_of_batch in nodes:
            print(f"Deduplicating {len(nodes_of_batch)} nodes in batch {x}")
            for node in nodes_of_batch:
                unique_prop = self.get_unique_identifier_of_node_for_label(node)
                unique_val = node[unique_prop]
                if isinstance(unique_val, str):
                    if unique_val not in nodes_dedup:
                        nodes_dedup[unique_val] = node
                else:
                    assert len(unique_val) == 1
                    if unique_val[0] not in nodes_dedup:
                        nodes_dedup[unique_val[0]] = node
            x += 1
            print(f"Deduplicated nodes in batch {batch_num} and current size {len(nodes_dedup)}")
        print(f"Nodes deduplicated {dt.datetime.now()}")

        x = 1
        for edges_of_batch in edges:
            print(f"Deduplicating {len(edges_of_batch)} nodes in batch {x}")
            for edge in edges_of_batch:
                unique_val = edge["edge_id"]
                if unique_val not in edges_dedup:
                    edges_dedup[unique_val] = edge
            x += 1
        print(f"Edges deduplicated {dt.datetime.now()}")

        graph = {"nodes": list(nodes_dedup.values()), "edges": list(edges_dedup.values())}

        end = dt.datetime.now()
        duration = (end-start).total_seconds()
        procTime = Commons.convert_python_time_to_proto_time(end)
        status = f"Deduplication complete. Duration: {duration}, Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}"
        loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
        print("Deduplicating batched graphs")

        print("Data deduplication over")
        print(f"All Graph transformation operaionts over in {dt.datetime.now()-st}")
        return graph

    def transform_data_using_pandas_dataframe(self, pdf: pd.DataFrame, case_id):
        data = json.loads(pdf.to_json(orient='records'))

        extracted_data = {
            "windowsRecords": [], "exchangeRecords": [], "sysmonRecords": [],
            "networkRecords": [], "sepcRecords": []
        }

        start = dt.datetime.now()

        for row in data:
            record = json.loads(row["data"])
            ds = record["dataSourceName"]
            if ds == "windows":
                extracted_data["windowsRecords"].append(record)
            elif ds == "watchguard":
                extracted_data["networkRecords"].append(record)
            elif ds == "sysmon":
                extracted_data["sysmonRecords"].append(record)
            elif ds == "msexchange":
                extracted_data["exchangeRecords"].append(record)
            else:
                extracted_data["sepcRecords"].append(record)

        convertor = IncomingDataToGraphTransformer(extracted_data)
        graph = convertor.convert()

        end = dt.datetime.now()
        duration = (end-start).total_seconds()
        procTime = Commons.convert_python_time_to_proto_time(end)
        status = f"Transformation completed. Duration (s): {duration}"
        loading_status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print("Going to load to target table")

        output_table_o = self.credentials["additionalParameters"]["src_transformed_tbl"]
        output_table = "transformed_graph_data_demo_tmp"
        options = {
            "sfUrl": self.credentials["url"],
            "sfAccount": self.credentials["account"],
            "sfUser": self.credentials["user"],
            "sfPassword": self.credentials['password'],
            "sfDatabase": self.credentials['database'],
            "sfSchema": self.credentials['schema'],
            "sfWarehouse": self.credentials['warehouse']
        }

        conn = URL(
            account=options["sfAccount"],
            user=options["sfUser"],
            password=options["sfPassword"],
            database=options["sfDatabase"],
            schema=options["sfSchema"],
            warehouse=options["sfWarehouse"]
        )
        engine = create_engine(conn)

        pdf_data = []
        for node in graph["nodes"]:
            elem = {"element": json.dumps(node), "element_type": "node", "case_id": case_id, "ds": node["dataSourceName"], "processing_dttm": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            pdf_data.append(elem)

        for edge in graph["edges"]:
            elem = {"element": json.dumps(edge), "element_type": "edge", "case_id": case_id, "ds": edge["dataSourceName"], "processing_dttm": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            pdf_data.append(elem)

        final_pdf = pd.DataFrame(pdf_data)
        final_pdf.to_sql(output_table, engine.connect(), if_exists="append", method="multi", index=False, chunksize=10000)
        print("Saved to snowflake table")

        params = graphdb_pb2.ProcedureParams()
        params.procedure = "SP_CONVERT_VARCHAR_TO_VARIANT_FOR_TRANSFORMED_DATA"
        order = "SOURCE_TABLE,TARGET_TABLE".split(",")
        params.order[:] = order
        params.parameters["SOURCE_TABLE"] = output_table
        params.parameters["TARGET_TABLE"] = output_table_o
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Modified to variants from varchar")
        #
        # connection = engine.connect()
        # connection.execute(f"call SP_CONVERT_VARCHAR_TO_VARIANT_FOR_TRANSFORMED_DATA('transformed_graph_data_demo_tmp', '{output_table_o}')")
        # print("Converted to variants")
        #
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"Loading transformed data to transformed_graph_data_demo_tmp", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        #
        print(f"Saved data to snowflake table @ {dt.datetime.now()}")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to transformed_graph_data_demo_tmp", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        params.procedure = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure"]
        order = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure_order"].split(",")
        params.order[:] = order

        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["SRC_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["src_transformed_tbl"]
        params.parameters["TARGET_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Updated node_ids and edge_ids for transformed data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Node and Edge IDs created for transformed data", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Transformation completed")
        print("Data load started")

        table = graphdb_pb2.TransformedDataTable(table=output_table, caseId=case_id)
        self.LOADER_CLIENT.EnsureGraphInSnowFromFromTable(table)

    def transform_data_from_spark_dataframe_2(self, sdf: DataFrame, case_id):

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started (In Thread)", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
        edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

        print("Defined transformer udfs")

        nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds")))
        edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds")))

        print("transformed extracted data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation of nodes & edges done", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        nodes_sdf = nodes_sdf.withColumn("node_size", F.size(nodes_sdf.nodes)).select("case_id", "ds", "nodes", "node_size")
        edges_sdf = edges_sdf.withColumn("edge_size", F.size(edges_sdf.edges)).select("case_id", "ds", "edges", "edge_size")

        print("Created node and edge size col")

        convertor = F.udf(convert_to_json_from_str, ArrayType(MapType(StringType(), StringType())))
        nodes_sdf = nodes_sdf.withColumn("nodes", convertor("nodes"))
        edges_sdf = edges_sdf.withColumn("edges", convertor("edges"))

        print("Converted node and edge string obj to array of map")

        filtered_nodes_sdf = nodes_sdf.filter(nodes_sdf.node_size >= 1)
        filtered_edges_sdf = edges_sdf.filter(edges_sdf.edge_size >= 1)

        print("Filtered nodes and edges for blank elements")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Removed invalid nodes & edges (Transformation)", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        exploded_nodes = filtered_nodes_sdf.withColumn("nodes_exploded", F.explode("nodes")).select("case_id", "ds", F.col("nodes_exploded").alias("element"))
        exploded_edges = filtered_edges_sdf.withColumn("edges_exploded", F.explode("edges")).select("case_id", "ds", F.col("edges_exploded").alias("element"))

        print("Exploded nodes and edges")

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Explosion of nodes & edges done", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
        exploded_nodes = exploded_nodes.withColumn("element", list_to_str_udf("element"))
        exploded_edges = exploded_edges.withColumn("element", list_to_str_udf("element"))

        print("Converted back node and edges from json obj to str")

        unique_identifier_udf = udf(generate_identifier, StringType())
        exploded_nodes = exploded_nodes.withColumn("identifier", unique_identifier_udf(array("element", "ds")))

        exploded_nodes.select("identifier", "element").toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\identifier_nodes.json", "w+"), indent=2, orient="records")
        print("Saved identifier + nodes")
        exit(-1)

        dedup_node_sdf = exploded_nodes.dropDuplicates(['identifier']).select("case_id", "ds", "element")

        print("deduplicated nodes")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Nodes Deduplicated in Transformer", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        nodes_sdf = dedup_node_sdf.withColumn("element_type", F.lit("node"))
        edges_sdf = exploded_edges.withColumn("element_type", F.lit("edge"))

        print("Created element type col")

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Created element_type col", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        #
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Converted edges col from map to str", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        final_sdf = nodes_sdf.union(edges_sdf)

        print("Union nodes and edges sdf")

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"Unionify nodes and edges df for credentials {self.credentials}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"URL: {self.credentials['url']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"account: {self.credentials['account']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"user: {self.credentials['user']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"password: {self.credentials['password']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"database: {self.credentials['database']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"schema: {self.credentials['schema']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"warehouse: {self.credentials['warehouse']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"additionalParameters: {self.credentials['additionalParameters']}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        output_table = self.credentials["additionalParameters"]["src_transformed_tbl"]
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"defined output tbl {output_table}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        options = {
            "sfUrl": self.credentials["url"],
            "sfAccount": self.credentials["account"],
            "sfUser": self.credentials["user"],
            "sfPassword": self.credentials['password'],
            "sfDatabase": self.credentials['database'],
            "sfSchema": self.credentials['schema'],
            "sfWarehouse": self.credentials['warehouse']
        }

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"Extracted credentials: {options}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        final_sdf = final_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        print(f"Writing data to snowflake table {output_table} under DB: {options['sfDatabase']} and schema: {options['sfSchema']} @ {dt.datetime.now()}")

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"Defined processing_dttm: {final_sdf.printSchema()}", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print(final_sdf.printSchema())
        final_sdf = final_sdf.select("element", "element_type", "case_id", "ds", "processing_dttm")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Loading transformed data to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Loading to sf table")
        print(options)
        # print(final_sdf.show(50))

        final_sdf.filter(final_sdf.element_type == "node").toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\nodes.json", "w+"), indent=2, orient="records")

        final_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
        print(f"Saved data to snowflake table @ {dt.datetime.now()}")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        params.procedure = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure"]
        order = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure_order"].split(",")
        params.order[:] = order

        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["SRC_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["src_transformed_tbl"]
        params.parameters["TARGET_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Updated node_ids and edge_ids for transformed data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Node and Edge IDs created for transformed data", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Transformation completed")
        print("Data load started")

        table = graphdb_pb2.TransformedDataTable(table=output_table, caseId=case_id)
        self.LOADER_CLIENT.EnsureGraphInSnowFromFromTable(table)

    def transform_data_from_spark_dataframe_3(self, sdf: DataFrame, case_id):

        nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
        edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

        print("Defined transformer udfs")

        nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds")))
        edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds")))

        print("transformed extracted data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation of nodes & edges done", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        nodes_sdf = nodes_sdf.select("case_id", "ds", F.col("nodes").alias("element"))
        edges_sdf = edges_sdf.select("case_id", "ds", F.col("edges").alias("element"))

        nodes_sdf = nodes_sdf.withColumn("element_type", F.lit("node"))
        edges_sdf = edges_sdf.withColumn("element_type", F.lit("edge"))

        merged_sdf = nodes_sdf.union(edges_sdf)

        convertor = F.udf(convert_to_json_from_str, ArrayType(MapType(StringType(), StringType())))
        merged_sdf = merged_sdf.withColumn("element", convertor("element"))

        merged_sdf = merged_sdf.withColumn("element_size", F.size(merged_sdf.element)).select("case_id", "ds", "element", "element_size", "element_type")

        filtered_merges_sdf = merged_sdf.filter(merged_sdf.element_size >= 1)

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Removed invalid nodes & edges (Transformation)", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        exploded_merged_sdf = filtered_merges_sdf.withColumn("element_exploded", F.explode("element")).\
            select("case_id", "ds", F.col("element_exploded").alias("element"), "element_type")

        exploded_nodes_sdf = exploded_merged_sdf.filter(exploded_merged_sdf.element_type == "node")
        exploded_edges_sdf = exploded_merged_sdf.filter(exploded_merged_sdf.element_type == "edge")

        unique_identifier_udf = udf(generate_identifier, StringType())
        exploded_nodes_sdf = exploded_nodes_sdf.withColumn("identifier", unique_identifier_udf(array("element", "ds")))
        dedup_node_sdf = exploded_nodes_sdf.dropDuplicates(['identifier']).select("case_id", "ds", "element", "element_type")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Nodes deduplicated (Transformation)", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        final_sdf = dedup_node_sdf.union(exploded_edges_sdf.select("case_id", "ds", "element", "element_type"))

        list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
        final_sdf = final_sdf.withColumn("element", list_to_str_udf("element"))

        final_sdf = final_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        output_table = self.credentials["additionalParameters"]["src_transformed_tbl"]
        options = {
            "sfUrl": self.credentials["url"],
            "sfAccount": self.credentials["account"],
            "sfUser": self.credentials["user"],
            "sfPassword": self.credentials['password'],
            "sfDatabase": self.credentials['database'],
            "sfSchema": self.credentials['schema'],
            "sfWarehouse": self.credentials['warehouse']
        }

        final_sdf = final_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        print(f"Writing data to snowflake table {output_table} under DB: {options['sfDatabase']} and schema: {options['sfSchema']} @ {dt.datetime.now()}")
        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Loading transformed data to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        print("Loading to sf table")
        print(options)

        final_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
        print(f"Saved data to snowflake table @ {dt.datetime.now()}")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        params.procedure = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure"]
        order = self.credentials["additionalParameters"]["node_edge_id_generator_stored_procedure_order"].split(",")
        params.order[:] = order

        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["SRC_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["src_transformed_tbl"]
        params.parameters["TARGET_TRANSFORMED_TBL"] = self.credentials["additionalParameters"]["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Updated node_ids and edge_ids for transformed data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Node and Edge IDs created for transformed data", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation Complete", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Transformation completed")
        print("Data load started")

    def transform_data_from_spark_dataframe(self, sdf: DataFrame, case_id):
        sleep(60)
        print("Sleep for 60 sec done")
        # sdf = sdf.select("*").withColumn("row_id", monotonically_increasing_id())

        # sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\incoming.json", "w+"), indent=2, orient="records")
        # print("saves incoming to json")

        nodes_transformer = udf(apply_node_transformation_to_records, ArrayType(StringType()))
        edges_transformer = udf(apply_edge_transformation_to_records, ArrayType(StringType()))

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation of nodes & edges done", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # print(f"Total numbr of records {sdf.count()}")

        nodes_sdf = sdf.withColumn("nodes", nodes_transformer(array("data", "ds")))
        edges_sdf = sdf.withColumn("edges", edges_transformer(array("data", "ds")))

        convertor = F.udf(convert_to_json_from_str, ArrayType(MapType(StringType(), StringType())))
        nodes_sdf = nodes_sdf.withColumn("nodes", convertor("nodes"))
        edges_sdf = edges_sdf.withColumn("edges", convertor("edges"))

        nodes_sdf = nodes_sdf.select("*").withColumn("id", monotonically_increasing_id())
        edges_sdf = edges_sdf.select("*").withColumn("id", monotonically_increasing_id())
        print("Generated nodes and edges and defined a id column per row")
        # print(f"After tranformation and row id addition, nodes: {nodes_sdf.count()} & edges: {edges_sdf.count()}")

        # merged = nodes_sdf.select("ds", "nodes", "id", "case_id", F.col("row_id").alias("node_row_id")). \
        #     join(edges_sdf.select("edges", "id", F.col("row_id").alias("edge_row_id")), nodes_sdf.id == edges_sdf.id). \
        #     select("ds", "nodes", "edges", "case_id", "node_row_id", "edge_row_id")
        merged = nodes_sdf.select("ds", "nodes", "id", "case_id"). \
            join(edges_sdf.select("edges", "id"), nodes_sdf.id == edges_sdf.id). \
            select("ds", "nodes", "edges", "case_id")
        # print(f"Merged nodes and edges df, size {merged.count()}")

        merged = merged.withColumn("node_size", F.size(merged.nodes)).withColumn("edge_size", F.size(merged.edges))
        print("Defined 2 cols of node and edge size")

        # print("Saving nodes and edgess before removing invalid")
        # merged.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\unfiltered.json", "w+"), indent=2, orient="records")
        # print("Saved nodes and edges before removing invalid")

        valid_sdf = merged.filter((merged.node_size >= 1) | (merged.edge_size >= 1))
        # print(f"removed invalid data, size {valid_sdf.count()}")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Removed invalid nodes & edges (Transformation)", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")).\
        #     select("nodes_exploded", "edges_exploded", "case_id", "ds", "node_row_id", "edge_row_id")
        # nodes_sdf = valid_sdf.select("nodes", "case_id", "ds").withColumn("nodes_exploded",  F.explode("nodes")).select("nodes_exploded", "case_id", "ds")
        # edges_sdf = valid_sdf.select("edges", "case_id", "ds").withColumn("edges_exploded",  F.explode("edges")).select("edges_exploded", "case_id", "ds")

        # print("Saving nodes and edgess before explode")
        # valid_sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\unexploded.json", "w+"), indent=2, orient="records")
        # print("Saved nodes and edges before explode")
        valid_sdf = valid_sdf.withColumn("nodes_exploded",  F.explode("nodes")).withColumn("edges_exploded",  F.explode("edges")). \
            select("nodes_exploded", "edges_exploded", "case_id", "ds")
        # valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"), "node_row_id", "edge_row_id")
        valid_sdf = valid_sdf.select("case_id", "ds", F.col("nodes_exploded").alias("nodes"), F.col("edges_exploded").alias("edges"))

        # valid_sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\exploded.json", "w+"), indent=2, orient="records")

        nodes_sdf = valid_sdf.select("case_id", "ds", "nodes")
        edges_sdf = valid_sdf.select("case_id", "ds", "edges")
        # print(f"After explosion, nodes: {nodes_sdf.count()} & edges: {edges_sdf.count()}")

        # print("Saving nodes and edgess before dedup")
        # nodes_sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\nodes.json", "w+"), indent=2, orient="records")
        # edges_sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\edges.json", "w+"), indent=2, orient="records")
        # print("Saved nodes and edges before dedup")

        list_to_str_udf = F.udf(lambda x: json.dumps(x), StringType())
        nodes_sdf = nodes_sdf.withColumn("nodes", list_to_str_udf("nodes"))
        print("Converted node maps to string")

        unique_identifier_udf = udf(generate_identifier, StringType())
        nodes_sdf = nodes_sdf.withColumn("identifier", unique_identifier_udf(array("nodes", "ds")))
        dedup_node_sdf = nodes_sdf.dropDuplicates(['identifier'])

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Nodes deduplicated (Transformation)", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # nodes_sdf = dedup_node_sdf.select("nodes", "ds", "case_id", F.col("row_id").alias("node_id"))
        # nodes_sdf = nodes_sdf.withColumn("node_id", monotonically_increasing_id())
        #
        # edges_sdf = edges_sdf.select("edges", "ds", "case_id")
        # edges_sdf = edges_sdf.withColumn("edge_id", monotonically_increasing_id())
        #
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Node & Edge IDs generated (Transformation)", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        nodes_sdf = dedup_node_sdf.withColumn("element_type", F.lit("node"))
        edges_sdf = edges_sdf.withColumn("element_type", F.lit("edge"))

        # node_id_updater = udf(update_node_id, StringType())
        # edge_id_updater = udf(update_edge_id, StringType())
        #
        # nodes_sdf = nodes_sdf.withColumn("nodes", node_id_updater(array("nodes", "node_id")))
        # edges_sdf = edges_sdf.withColumn("edges", edge_id_updater(array("edges", "edge_id")))
        #
        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status="Node & Edge ID Updated (Transformation)", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # node_id_generator = udf(generate_node_id, StringType())
        # edge_id_generator = udf(generate_edge_id, StringType())
        # nodes_sdf = nodes_sdf.withColumn("nodes_id_gen", node_id_generator(array("nodes", "node_id")))
        # edges_sdf = edges_sdf.withColumn("edges_id_gen", edge_id_generator(array("edges", "edge_id")))

        # nodes_sdf = nodes_sdf.select("case_id", "ds", F.col("element").alias("element_type"), F.col("nodes").alias("element"), F.col("nodes_id_gen").alias("element_id"))
        nodes_sdf = nodes_sdf.select("case_id", "ds", "element_type", F.col("nodes").alias("element"))
        nodes_sdf = nodes_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # edges_sdf = edges_sdf.select("case_id", "ds", F.col("element").alias("element_type"), F.col("edges").alias("element"), F.col("edges_id_gen").alias("element_id"))
        edges_sdf = edges_sdf.select("case_id", "ds", "element_type", F.col("edges").alias("element"))
        edges_sdf = edges_sdf.withColumn("processing_dttm", F.lit(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        edges_sdf = edges_sdf.withColumn("element", list_to_str_udf("element"))
        print("Converted edge maps to string")
        final_sdf = nodes_sdf.union(edges_sdf)

        # final_pdf = final_sdf.toPandas()
        # print(f"After process is over, nodes size: {final_pdf[final_pdf['element_type'] == 'node'].shape} & "
        #       f"edge size: {final_pdf[final_pdf['element_type'] == 'edge'].shape}")
        # final_pdf.to_csv("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\final_pdf.csv")
        # print(f"After other process, size: {final_sdf.count()}")

        # final_sdf.toPandas().to_csv("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\final.csv")
        # print("Saved edges df to D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\final.csv")

        output_table = self.credentials.additionalParameters["src_transformed_tbl"]
        options = {
            "sfUrl": self.credentials.url,
            "sfAccount": self.credentials.account,
            "sfUser": self.credentials.user,
            "sfPassword": self.credentials.password,
            "sfDatabase": self.credentials.database,
            "sfSchema": self.credentials.schema,
            "sfWarehouse": self.credentials.warehouse
        }
        # options['sfDatabase'] = "snowflake_graph_test"
        # options["sfSchema"] = "graph_test",
        print(f"Writing data to snowflake table {output_table} under DB: {options['sfDatabase']} and schema: {options['sfSchema']} @ {dt.datetime.now()}")

        final_sdf = final_sdf.select("element", "element_type", "case_id", "ds", "processing_dttm")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Loading transformed data to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        final_sdf.write.format("snowflake").options(**options).option("dbtable", output_table).mode("append").save()
        print(f"Saved data to snowflake table @ {dt.datetime.now()}")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Transformed data loaded to {output_table}", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        params = graphdb_pb2.ProcedureParams()
        # params.procedure = "SP_GENERATE_NODE_AND_EDGE_IDS"
        params.procedure = self.credentials.additionalParameters["node_edge_id_generator_stored_procedure"]
        order = self.credentials.additionalParameters["node_edge_id_generator_stored_procedure_order"].split(",")
        params.order[:] = order

        print(params)
        print("xxxxxx")
        params.parameters["CASE_ID_VAL"] = case_id
        params.parameters["SRC_TRANSFORMED_TBL"] = self.credentials.additionalParameters["src_transformed_tbl"]
        params.parameters["TARGET_TRANSFORMED_TBL"] = self.credentials.additionalParameters["target_transformed_tbl"]
        print(params)
        self.CORE_CLIENT.ExecuteStoredProcedure(params)
        print("Updated node_ids and edge_ids for transformed data")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status=f"Node and Edge IDs created for transformed data", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        # nodes_pdf = valid_sdf.select("nodes").toPandas()
        # nodes_pdf = final_sdf.filter(final_sdf.element_type == 'node').toPandas()
        # nodes_json = json.loads(nodes_pdf.to_json(orient="records"))
        # print(f"Created nodes json for parameter to loader class @ {dt.datetime.now()} of size {len(nodes_json)}")

        # nodes_proto = []
        # for row in nodes_json:
        #     node = json.loads(row["element"])
        #
        #     elem = graphdb_pb2.Node()
        #     for k, v in node.items():
        #         vv = Commons._convert_value_to_struct_value_(v)
        #         elem.properties[k].CopyFrom(vv)
        #     nodes_proto.append(elem)
        #
        # print("Generated nodes list of proto Node")

        # procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        # status = graphdb_pb2.CaseLoadingStatus(status=f"Transformation completed", caseId=case_id, processingTime=procTime)
        # self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
        print("Transformation completed")
        print("Data load started")

        table = graphdb_pb2.TransformedDataTable(table=output_table, caseId=case_id)
        self.LOADER_CLIENT.EnsureGraphInSnowFromFromTable(table)

    def TransformExtractedDataFromIntermediateTable(self, request, context):
        case_id = request.caseId
        table = request.table

        print("Going to start transformation")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Reading in snowflake table")
        st = dt.datetime.now()

        dbi = graphdb_pb2.DataBaseIdentifier(database="tenant5", schema="enriched", caller="python")
        credentials = self.CORE_CLIENT.GetSnowFlakeCredentials(dbi)
        enriched_options = {
            "sfUrl": credentials.url,
            "sfAccount": credentials.account,
            "sfUser": credentials.user,
            "sfPassword": credentials.password,
            "sfDatabase": credentials.database,
            "sfSchema": credentials.schema,
            "sfWarehouse": credentials.warehouse
        }

        if self.USE_SPARK:
            sdf = self.spark.read.format("snowflake").options(**enriched_options).option("query", f"select data, ds, case_id from {table} where case_id = '{case_id}'").load()
            sdf = sdf.repartition(25)

            en = dt.datetime.now()
            status = f"Loaded extractor data in {(en-st).total_seconds()} sec"
            procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
            status = graphdb_pb2.CaseLoadingStatus(status=status, caseId=case_id, processingTime=procTime)
            self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
            print("Created spark dataframe and repartitions to 25 paritions")

            print("Going to start data transformation in thread using already built spark dataframe")

        # sdf.toPandas().to_json(open("D:\\Projects\\Freelancing\\Elysium Analytics\\snowgraph\\snowflake-graphdb\\incoming.json", "w+"), indent=2, orient="records")
        # print("Wrote to incoming.json")
        # exit(-1)

            t = threading.Thread(target=self.transform_data_from_spark_dataframe_2, kwargs={"sdf": sdf, "case_id": case_id})
            print("Created transformer thread")
            t.start()
        else:
            print("Reading into pandas")
            print(enriched_options)
            conn = URL(
                account=enriched_options["sfAccount"],
                user=enriched_options["sfUser"],
                password=enriched_options["sfPassword"],
                database=enriched_options["sfDatabase"],
                schema=enriched_options["sfSchema"],
                warehouse=enriched_options["sfWarehouse"]
            )
            print(conn)
            engine = create_engine(conn)
            print("Reading query", engine)
            pdf = pd.read_sql_query(f"select data::varchar as data, ds::varchar as ds, case_id::varchar as case_id \
             from {table} where case_id = '{case_id}'", engine.connect())
            print("Created pandas dataframe")
            t = threading.Thread(target=self.transform_data_using_pandas_dataframe, kwargs={"pdf": pdf, "case_id": case_id})
            print("Created transformer thread")
            t.start()

        print("Returning back to GraphExtractor with empty")

        return graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

    def TransformStreamDataOnDataBricks(self, request_iterator, context):
        print("Going to start transformation")

        extracted_data = []
        case_id = None
        initial_update = True

        records = []
        for record in request_iterator:
            records.append(record)

            case_id = record.caseId

            if initial_update:
                procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
                status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id, processingTime=procTime)
                self.CORE_CLIENT.UpdateCaseLoadingStatus(status)
                initial_update = False

            data_type = record.WhichOneof('data')
            if data_type == "windowsRecord":
                extracted_data.append([json.dumps(MessageToDict(getattr(record, data_type))), "windows", case_id])
            elif data_type == "exchangeRecord":
                extracted_data.append([json.dumps(MessageToDict(getattr(record, data_type))), "msexchange", case_id])
            elif data_type == "sysmonRecord":
                extracted_data.append([json.dumps(MessageToDict(getattr(record, data_type))), "sysmon", case_id])
            elif data_type == "sepcRecord":
                extracted_data.append([json.dumps(MessageToDict(getattr(record, data_type))), "sepc", case_id])
            else:
                extracted_data.append([json.dumps(MessageToDict(getattr(record, data_type))), "watchguard", case_id])

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        status = graphdb_pb2.CaseLoadingStatus(status="Tranaformation data aggregated", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(status)

        print("Aggregated the data into single list")
        sdf = self.spark.createDataFrame(extracted_data, ["data", "ds", "case_id"])
        sdf = sdf.repartition(25)
        print("Created spark dataframe and repartitions to 25 paritions")

        print("Going to start data transformation in thread after data aggregation is over")
        t = threading.Thread(target=self.transform_data_from_spark_dataframe, kwargs={"sdf": sdf, "case_id": case_id})
        print("Created transformer thread")
        t.start()
        print("Returning back to GraphExtractor with empty")

        return graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

    def TransformStreamRawDataToGraph(self, request_iterator, context):
        case_id = None
        st = dt.datetime.now()
        if self.MINI_STREAM:
            graph = self.mini_stream_data_transformation(request_iterator, case_id, st)
        else:
            graph = self.batch_data_transformation(request_iterator, case_id, st)

        print("Going to start loading of nodes in Graph")

        nodes_in_record_it = Commons.node_list_to_case_node_iterator(graph["nodes"], case_id)
        self.CORE_CLIENT.UpdateNodesForCase(nodes_in_record_it)
        print("Loaded the nodes for the case in snowflake")

        print(f"Going to stream data to GraphLoader for no nodes: {len(graph['nodes'])} edges: {len(graph['edges'])}")
        self.LOADER_CLIENT.EnsureGraphInSnowFlakeStream(self.loader_data_proto_iterator(graph, case_id))
        print("Streamed data to GraphLoader")

        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return empty

    def TransformRawDataToGraph(self, request, context):
        case_id = request.caseId
        print("Transformation started for case " + str(case_id))

        # f = open(f"../../resources/dumps/Case_{case_id}_incoming_data.bin", "wb")
        # f.write(request.SerializeToString())
        # f.close()
        print("Saved the incoming message as binary")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
        print("Transformation started")

        data = MessageToDict(request)

        print(data.keys())

        windows = data["windowsRecords"] if "windowsRecords" in data else []
        msexchange = data["exchangeRecords"] if "exchangeRecords" in data else []
        sysmon = data["sysmonRecords"] if "sysmonRecords" in data else []
        wgtraffic = data["networkRecords"] if "networkRecords" in data else []
        sepc = data["sepcRecords"] if "sepcRecords" in data else []
        print("Incoming msg to dict")

        # json.dump(windows, open(f"../../resources/dumps/Case_{case_id}_windows_incoming_data.json", "w+"), indent=2)
        print("windows of len ", len(windows))

        # json.dump(msexchange, open(f"../../resources/dumps/Case_{case_id}_exchange_incoming_data.json", "w+"), indent=2)
        print("msexchange of len ", len(msexchange))

        # json.dump(sysmon, open(f"../../resources/dumps/Case_{case_id}_sysmon_incoming_data.json", "w+"), indent=2)
        print("sysmon of len ", len(sysmon))

        # json.dump(wgtraffic, open(f"../../resources/dumps/Case_{case_id}_wgtraffic_incoming_data.json", "w+"), indent=2)
        print("wgtraffic of len ", len(wgtraffic))

        # json.dump(sepc, open(f"../../resources/dumps/Case_{case_id}_sepc_incoming_data.json", "w+"), indent=2)
        print("symantec of len ", len(sepc))
        print("Dumped the incoming data to resources/dumps file for the case")

        convertor = IncomingDataToGraphTransformer(data)
        graph = convertor.convert()
        print("Converted Incoming data to Graph")

        # json.dump(graph, open(f"../../resources/dumps/Case_{case_id}_graph_data.json", "w+"), indent=2)
        print("Dumped the graph data to resources/dumps json for the case")

        # graph_proto = Commons.convert_graph_dict_to_protobuf_graph(graph, case_id)
        # print("Converted graph to graph proto")

        # f = open(f"../../resources/dumps/Case_{case_id}_graph_data.bin", "wb+")
        # f.write(graph_proto.SerializeToString())
        # f.close()
        print("Saved the graph output as binary")

        procTime = Commons.convert_python_time_to_proto_time(dt.datetime.now())
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Completed", caseId=case_id, processingTime=procTime)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)
        print("Going to start loading of nodes in Graph")

        nodes_in_record_it = Commons.node_list_to_case_node_iterator(graph["nodes"], case_id)
        self.CORE_CLIENT.UpdateNodesForCase(nodes_in_record_it)

        print("Loaded the nodes generated for the case")
        print("Going to save the dataset to filesystem")
        # path = f'../../resources/dumps/{case_id}_graph.json'
        # json.dump(graph, open(path, "w+"), indent=1)
        # print(f"Saved file to {os.path.abspath(path)}")

        # self.LOADER_CLIENT.EnsureGraphInSnowFlake(graph_proto)
        print(f"Going to stream data to GraphLoader for no nodes: {len(graph['nodes'])} edges: {len(graph['edges'])}")
        self.LOADER_CLIENT.EnsureGraphInSnowFlakeStream(self.loader_data_proto_iterator(graph, case_id))
        print("Streamed data to GraphLoader")

        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return empty

    def TransformAndLoadData(self, request, context):

        case_id = request.caseId
        print("Transformation started for case " + str(case_id))

        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Started", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        import json
        incoming_data = MessageToDict(request)
        # json.dump(incoming_data, open(f"../../resources/dumps/Case_{case_id}_incoming_data.json", "w+"), indent=2)
        print("Dumped the data to resources/dumps file for the case")

        # print("Starting generation of sample data")
        # generator = SampleDataGenerator()
        # generator.extract()
        # data = generator.generate()
        sleep(180)
        print("Data transformation over")
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Transformation Complete", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        sleep(30)

        loading_status = graphdb_pb2.CaseLoadingStatus(status="Loading Started", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        # response = graphdb_pb2.DummyMessageStatus()
        # response.message = " and came to loader"
        # response.status = "Returning from Loader"
        # response.source = "GraphLoader"
        # response.current.append("GraphLoader-Python")
        #
        # print("Proof that I'm at transformer")
        #
        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

        # executor = Loader()
        # executor.with_data(data)
        # executor.extract()
        # executor.transform()

        print("Starting data loading now")
        sleep(120)
        print("Data loading over")

        loading_status = graphdb_pb2.CaseLoadingStatus(status="Loading Complete", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        sleep(60)
        loading_status = graphdb_pb2.CaseLoadingStatus(status="Export Complete", caseId=case_id)
        self.CORE_CLIENT.UpdateCaseLoadingStatus(loading_status)

        print("Returning back from graph transformer with empty msg")
        print("============")

        return empty

    def TestAPI(self, request, context):
        msg = request.message
        source = request.source
        current = request.current

        print("I'm inside servicer")

        response = graphdb_pb2.DummyMessageStatus()
        response.message = msg + " and came to loader"
        response.status = "Returning from Loader"
        response.source = "GraphLoader"
        print(request)
        response.current.append("GraphLoader-Python")
        print("=====")
        print(response)
        return response

# support@cleartax.in
