from sqlalchemy.ext.declarative import declarative_base
from snowflake.sqlalchemy import VARIANT, ARRAY
from sqlalchemy import Column, Integer, Text, Sequence, inspect, DATETIME
from utils.common_resources import Commons
from utils.utils import Utilities as U, APPLICATION_PROPERTIES
from gen.graphdb_pb2 import CaseLoadingStatus, NodesInCase, CaseStatus, Node, StructureValue
import json
import pandas as pd
import datetime as dt
from multipledispatch import dispatch


class CaseStatusObject:
    def __init__(self, case_ids: list, query=None, engine=None):
        # application_properties = "../../resources/application.properties"
        # self.APPLICATION_PROPERTIES = Commons.load_properties(application_properties)
        #
        # connection = SnowGraphConnection(self.APPLICATION_PROPERTIES)
        connection = Commons.get_connection()
        sf_config = U.load_properties(U.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])

        print("Connection inside case object is ", connection)

        self.CASE_IDS = case_ids
        self.Base = declarative_base()
        self.QUERY = query

        self.TBL = sf_config["case_tbl"]

        self.engine = connection.SNOWFLAKE_ENGINE if engine is None else engine
        self.session = connection.SNOWFLAKE_SESSION

        class CaseMetadata(self.Base):
            __tablename__ = self.TBL

            id = Column("id", Integer,  Sequence('id_seq'), primary_key=True,autoincrement=True, unique=True)
            case_id = Column("case_id", Text, nullable=False, unique=True)
            nodes = Column("nodes", VARIANT)
            hops = Column("hops", Integer)
            status = Column("status", Text)
            query = Column("query", VARIANT)
            START_TIME = Column("START_TIME", DATETIME)
            QUERY_START_TIME = Column("QUERY_START_TIME", DATETIME)
            QUERY_END_TIME = Column("QUERY_END_TIME", DATETIME)
            PROCESSING_TIME = Column("PROCESSING_TIME", DATETIME)
            DATASOURCES = Column("DATASOURCES", ARRAY)
            QUERY_TRACKER = Column("QUERY_TRACKER", ARRAY)

        print("Engine is ", self.engine)
        print("Session is ", self.session)

        self.CASEMETADATA = CaseMetadata
        self.Base.metadata.create_all(bind=self.engine)

        print("Created case table if absent")

    @staticmethod
    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    def get_case_id(self, query):
        session = self.session()
        assert self.CASE_IDS == []
        results = session.query(self.CASEMETADATA).filter(self.CASEMETADATA.query == query)
        case_ids = []
        for case in results:
            case_ids.append(self.object_as_dict(case)["case_id"])

        assert len(case_ids) <= 1
        session.commit()
        session.close()
        return case_ids[0] if len(case_ids) == 1 else "Not Found"

    def read(self, all=False):
        session = self.session()

        data = []
        if all:
            reslist = session. \
                query(self.CASEMETADATA)

            case_list = []
            for case in reslist:
                case_list.append(self.object_as_dict(case))

            data = case_list

        else:
            for case_id in self.CASE_IDS:
                reslist = session.\
                    query(self.CASEMETADATA).\
                    filter(self.CASEMETADATA.case_id == case_id)

                case_list = []
                for case in reslist:
                    case_list.append(self.object_as_dict(case))

                # print(len(case_list))
                assert len(case_list) <= 1
                if len(case_list) > 0:
                    data.append(case_list[0])
        session.close()
        return data

    def write(self, case_info):
        session = self.session()

        case_id = case_info["case_id"]
        hops = case_info["hops"] if "hops" in case_info else 3
        # query = case_info["query"] if "query" in case_info else None
        query = None

        assert case_id in self.CASE_IDS

        case = self.CASEMETADATA(case_id=case_id, hops=hops, status="Initialized", query=query) if query is not None \
            else self.CASEMETADATA(case_id=case_id, hops=hops, status="Initialized")

        cases = self.read()
        assert len(cases) == 0

        session.add(case)
        session.commit()
        session.close()

        print("Wrote")
        return True

    def generate_case_info_dict(self, col_name, col_val, case_id):
        case_info = {
            "case_id": case_id,
            col_name: col_val,
            "status": "NA"
        }

        if self.QUERY is not None:
            case_info["query"] = self.QUERY
        return case_info

    @staticmethod
    def convert_data_to_json_str(df, cols):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, dt.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            raise TypeError("Type %s not serializable" % type(obj))

        def convert_to_json(x):
            return json.dumps(x, default=json_serial)

        for col in cols:
            df[col] = df[col].apply(convert_to_json)
        return df

    def update_tracker(self, status, time):
        tracker = {status: time}
        cases = self.read()
        # print(f"While updating the tracker, the cases are {cases} and len {len(cases)}")
        assert len(cases) == 1
        cases = cases[0]
        existing_tracker_val = cases["QUERY_TRACKER"]
        existing_tracker_val = [] if existing_tracker_val is None else json.loads(existing_tracker_val)
        # print(f"Existing tracking value {existing_tracker_val} and type {type(existing_tracker_val)}")
        existing_tracker_val.append(tracker)
        # print(self.CASEMETADATA.QUERY_TRACKER.__str__())
        # print(f"Going to update tracker with {existing_tracker_val}")
        return self.update("QUERY_TRACKER", existing_tracker_val)

    @dispatch(dict)
    def update(self, data):
        print(f"I'm updating all data in single go for value: {data}")
        print(self.CASE_IDS)
        case_id = self.CASE_IDS[0]

        cases = self.read()

        session = self.session()
        if len(cases) == 0:
            self.write(data)

        print(f"I'm updating case table with {data}")

        session.query(self.CASEMETADATA). \
            filter(self.CASEMETADATA.case_id == case_id). \
            update(data)

        print("Updated")

        session.commit()
        session.close()
        return True

    @dispatch(object, object)
    def update(self, col_name, col_val):
        print("Update is always one element at a time")
        if col_name == "nodes":
            print(f"Number of nodes t update {len(col_val)}")
        print(self.CASE_IDS)
        case_id = self.CASE_IDS[0]

        cases = self.read()

        if isinstance(col_val, list) or isinstance(col_val, dict):
            connection = self.engine.connect()

            col_name = col_name.lower()

            df = pd.read_sql_query(f"select distinct * from {self.CASEMETADATA.__tablename__} where case_id = '{case_id}'", connection)
            df[col_name] = [col_val]
            # print("conversion ti write to tbl started")
            # print(df)

            df_new = self.convert_data_to_json_str(df, [col_name])
            # print(df_new.dtypes)
            df_new.to_sql(f"{self.CASEMETADATA.__tablename__}_TMP", con=connection, index=False, if_exists="append", method="multi", chunksize=500)
            print(f"loaded to {self.CASEMETADATA.__tablename__}_TMP")

            # print("truncating the row now")
            connection.execute(f"delete from {self.CASEMETADATA.__tablename__} where case_id = '{case_id}'")
            print("truncated original case table")

            tbl_variant_cols = ["NODES", "QUERY", "DATASOURCES", "QUERY_TRACKER"]
            # tbl_variant_cols = tbl_variant_cols + ["query"] if col_name != "query" else tbl_variant_cols
            tbl_cols = df_new.columns.tolist()
            tbl_cols = [x.upper() for x in tbl_cols]

            print("variant cols are ", tbl_variant_cols)
            print("tbl cols are ", tbl_cols)

            node_output_tbl = self.CASEMETADATA.__tablename__
            node_cols_merged = ",".join(["\"{}\"".format(x.upper()) if x not in tbl_variant_cols else "\"{}\"".format(x) for x in tbl_cols])
            node_cols_with_parse = ",".join(["\"{}\"".format(x.upper()) if x not in tbl_variant_cols else "parse_json(\"{}\")".format(x) for x in tbl_cols])
            node_src_tbl = f"{self.CASEMETADATA.__tablename__}_TMP"

            print("Created conversion query")
            migration_stmt = '''
            insert into {output_tbl} ({cols})
            select {src_cols_with_parse} from {src_tbl}
            '''

            sql = migration_stmt.format(output_tbl=node_output_tbl, cols=node_cols_merged, src_cols_with_parse=node_cols_with_parse, src_tbl=node_src_tbl)

            print(sql)
            connection.execute(sql)
            print("converted to variants")

            # print(f"Nodes added for case {case_id} is")
            # print(pd.read_sql_query(f"select array_size(nodes) from {node_output_tbl} where case_id = '{case_id}'", self.connection))

            print("Truncating the temp table now")
            connection.execute(f"delete from {node_src_tbl} where case_id = '{case_id}'")
            connection.execute("commit")

            connection.close()

        else:
            session = self.session()
            if len(cases) == 0:
                print("Im writing the case to table")
                self.write(self.generate_case_info_dict(col_name, col_val, case_id))

            print(f"I'm updating case table with col: {col_name} and val: {col_val}")

            session.query(self.CASEMETADATA). \
                filter(self.CASEMETADATA.case_id == case_id). \
                update({col_name: col_val})

            print("Updated")

            session.commit()
            session.close()

        return True

    def status(self):
        statuses = self.property("status")
        if len(statuses) > 0:
            assert len(statuses) == 1
            return statuses[0]
        else:
            return "Not Initialized"

    def read_all(self, all=False):
        cases = self.read(all)
        filtered_cases = []
        for case in cases:
            filtered_cases.append(case)
        return filtered_cases

    def read_and_get_status(self):
        cases = self.read_all(False)
        print("Read all cases ")
        print(cases)

        case_id = []
        status = ["Not Available" for x in cases]
        nodes = []
        hops = []
        queries = []
        query_start_times = []
        query_proc_time = []
        data_sources = []
        start_times = []
        end_times = []
        query_trackers = []
        for i in range(len(cases)):

            status[i] = cases[i]["status"]
            nodes.append(json.loads(cases[i]["nodes"]) if cases[i]["nodes"] is not None else {})
            hops.append(cases[i]["hops"])
            queries.append(json.loads(cases[i]["query"] if cases[i]["query"] is not None else "{}"))
            case_id.append(cases[i]["case_id"])
            query_start_times.append(cases[i]["START_TIME"] if cases[i]["START_TIME"]
                                                               is not None else dt.datetime(1970, 1, 1, 0, 0, 0))
            query_proc_time.append(cases[i]["PROCESSING_TIME"]
                                   if cases[i]["PROCESSING_TIME"] is not None else dt.datetime(1970, 1, 1, 0, 0, 0))
            data_sources.append(json.loads(cases[i]["DATASOURCES"]
                                           if cases[i]["DATASOURCES"] is not None else "[]"))
            start_times.append(cases[i]["QUERY_START_TIME"]
                               if cases[i]["QUERY_START_TIME"] is not None else dt.datetime(1970, 1, 1, 0, 0, 0))
            # print(start_times)
            end_times.append(cases[i]["QUERY_END_TIME"]
                             if cases[i]["QUERY_END_TIME"] is not None else dt.datetime(1970, 1, 1, 0, 0, 0))
            query_trackers.append(json.loads(cases[i]["QUERY_TRACKER"] if cases[i]["QUERY_TRACKER"] is not None else []))

        # print("Read all objects from cases")
        # print(f"with num nodes {len(nodes)}")
        # print(case_id, status, len(nodes), hops, queries)

        assert len(case_id) == len(status) == len(nodes) == len(hops) == len(queries)

        case_status = {}
        for i in range(len(cases)):
            case = cases[i]
            st = status[i]
            nn = nodes[i]
            hop = hops[i]
            query = U.convert_query_dict_to_case_info_proto(queries[i])
            export_time = U.convert_python_time_to_proto_time(query_start_times[i])
            ds = data_sources[i]
            proc_time = U.convert_python_time_to_proto_time(query_proc_time[i])
            case_id = case["case_id"]
            start_time = U.convert_python_time_to_proto_time(start_times[i])
            end_time = U.convert_python_time_to_proto_time(end_times[i])

            if len(nodes) > 0:
                case_info = CaseLoadingStatus(caseId=str(case_id), status=st, dataSources=ds,
                                              queryExportTime=export_time, processingTime=proc_time,
                                              startTime=start_time, endTime=end_time, query=query)
                case_info.others["hops"] = str(hop)

                case_nodes = NodesInCase()
                for node in nn:
                    n = Node()
                    for p, v in node.items():
                        n.properties[p].CopyFrom(StructureValue(string_value=str(v)))
                    case_nodes.nodes.append(n)

                case_info.nodes.CopyFrom(case_nodes)

                case_status[case_id] = case_info
            else:
                case_status[case_id] = \
                    CaseLoadingStatus(caseId=case_id, status="Not Started", nodes=NodesInCase(nodes=[Node(properties={})]))

        return CaseStatus(status=case_status)

    def property(self, prop):
        cases = self.read()
        filtered_cases = []
        for case in cases:
            filtered_cases.append(case[prop])
        return filtered_cases
