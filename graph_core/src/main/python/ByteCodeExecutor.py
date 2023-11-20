from query.QueryParser import QueryParser
from query.QueryExecutor import QueryExecutor
from gen.graphdb_pb2 import StructureValue, ListFormat, QueryResponse, GenericStructure, ListValue
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
import pandas as pd
from json import loads as str_to_dict
from typing import Union
import utils.common_resources as common


class ByteCodeExecutor(object):

    def __init__(self, bytecode):
        self.FINAL_QUERY = None
        self.ERROR: dict = dict()
        self.ENGINE = None
        self.RESULT: Union[GenericStructure, ListFormat] = None
        self.RESPONSE: QueryResponse = None

        self.QUERY = bytecode
        self._create_connection_()

    def _create_connection_(self):
        connection = common.Commons.get_connection()
        self.ENGINE = connection.SNOWFLAKE_ENGINE
        return self

    def get_response(self) -> QueryResponse:
        print("Response Generated")
        response = QueryResponse()
        print("QueryResponse obj created")
        if isinstance(self.RESULT, ListFormat):
            response.list_format.CopyFrom(self.RESULT)
        else:
            response.map_format.CopyFrom(self.RESULT)

        self.RESPONSE = response
        print("Query response copied")
        return self.RESPONSE

    def execute(self):
        print("Parsing query")
        parser = QueryParser(self.QUERY)
        print("Parsed the bytecode, executing query now")
        executor = QueryExecutor().for_query(self.QUERY).for_parser(parser)
        executor.execute()

        error = executor.ERROR
        if executor.FINAL_QUERY is None:
            error["EXECUTOR"] = "Couldn't generate query due to error please check QueryExecutor class"

        self.ERROR = error
        self.FINAL_QUERY = executor.FINAL_QUERY

        print(f"Len of error is {len(self.ERROR)} and error is {self.ERROR}")

        if len(self.ERROR) > 0:
            response = self._generate_error_message_for_query_()
        else:
            result = self._generate_result_()
            response = self._convert_to_list_query_response_(result)

        self.RESULT = response

        return self

    def _generate_error_message_for_query_(self):
        print("Converting error to GenericStructure")

        error = GenericStructure()
        for err_type, err_val in self.ERROR.items():
            val = StructureValue(string_value=err_val)
            error.fields[err_type].CopyFrom(val)
        return error

    def _convert_value_to_struct_value_(self, v):
        # print(f"Converting {v} to Struct")
        if isinstance(v, str):
            s = StructureValue(string_value=v)
        elif isinstance(v, int):
            s = StructureValue(int_value=v)
        elif isinstance(v, float):
            s = StructureValue(number_value=v)
        elif isinstance(v, dict):
            s = self._python_dict_to_proto_generic_struct_value_(v)
            s = StructureValue(struct_value=s)
        elif isinstance(v, list):
            if len(v) > 1:
                l = ListValue()
                for vv in v:
                    ss = self._convert_value_to_struct_value_(vv)
                    l.values.append(ss)
                s = StructureValue(list_value=l)
            else:
                s = self._convert_value_to_struct_value_(v[0])
        else:
            self.ERROR["ResponseConverter"] = f"Supports only str/int/float/dict in response element type got{type(v)}  " \
                f"for {str(v)}"
            print(self.ERROR)
            return self

        return s

    def _python_dict_to_proto_generic_struct_value_(self, d: dict) -> GenericStructure:
        value = GenericStructure()
        for k, v in d.items():
            value.fields[k].CopyFrom(self._convert_value_to_struct_value_(v))
            #
            # if isinstance(v, str):
            #     value.fields[k].CopyFrom(StructureValue(string_value=v))
            # elif isinstance(v, int):
            #     value.fields[k].CopyFrom(StructureValue(int_value=v))
            # elif isinstance(v, float):
            #     value.fields[k].CopyFrom(StructureValue(number_value=v))
            # elif isinstance(v, dict):
            #     value.fields[k].CopyFrom(self._python_dict_to_proto_generic_struct_value_(v))
            #     # value.struct_value = self._python_dict_to_proto_generic_struct_value_(v)
            # elif isinstance(v, list):
            #     for vv in v:
            #         if isinstance(vv, str):
            #             value.fields[k].CopyFrom(StructureValue(string_value=vv))
            #         elif isinstance(vv, int):
            #             value.fields[k].CopyFrom(StructureValue(int_value=vv))
            #         elif isinstance(vv, float):
            #             value.fields[k].CopyFrom(StructureValue(number_value=vv))
            #         elif isinstance(vv, dict):
            #             value.fields[k].CopyFrom(self._python_dict_to_proto_generic_struct_value_(vv))
            #             # value.struct_value = self._python_dict_to_proto_generic_struct_value_(v)
            #         else:
            #             self.ERROR["ResponseConverter"] = f"Supports only str/int/float/dict in response element type got{type(vv)}  " \
            #                 f"for {str(vv)} with key {k}"
            #
            # else:
            #     self.ERROR["ResponseConverter"] = f"Supports only str/int/float/dict in response element type got{type(v)}  " \
            #         f"for {str(v)} with key {k}"

        return value

    def _convert_to_list_query_response_(self, results):
        print("Converting result to ListFormat")

        assert type(results) == list
        response = ListFormat()

        for result in results:
            response_row = GenericStructure()
            for k, v in result.items():
                component = StructureValue()

                if "properties" in k:
                    v = str_to_dict(v)

                if isinstance(v, str):
                    # print(f"Encountered str for {k} and value {v}")
                    component.string_value = v
                elif isinstance(v, int):
                    # print(f"Encountered int for {k} and value {v}")
                    component.int_value = v
                elif isinstance(v, float):
                    # print(f"Encountered float for {k} and value {v}")
                    component.number_value = v
                elif isinstance(v, dict):
                    # print(f"Encountered dict for {k} and value {v}")
                    ret = self._python_dict_to_proto_generic_struct_value_(v)
                    component.struct_value.CopyFrom(ret)
                else:
                    self.ERROR["ResponseConverter"] = f"Supports only str/int/float/dict in response element type got{type(v)}  " \
                        f"for {str(v)} with key {k}"

                response_row.fields[k].CopyFrom(component)
            response.rows.append(response_row)

        return response

    def _generate_result_(self):
        if len(self.FINAL_QUERY) == 1:
            df = pd.read_sql_query(self.FINAL_QUERY[0], self.ENGINE).to_dict(orient="index")
            results = []
            for k, v in df.items():
                results.append(v)
            print("Results of read query 1 len: ", len(df))
        else:
            df = pd.read_sql_query(self.FINAL_QUERY[0], self.ENGINE).to_dict(orient="index")
            print("EResults of write query 1 rows: ", len(df))
            df = pd.read_sql_query(self.FINAL_QUERY[1], self.ENGINE).to_dict(orient="index")
            results = []
            for k, v in df.items():
                results.append(v)
            # print("QUERY: " + self.FINAL_QUERY[1])
            # print("EResults of write query 2")
            # print(results)
        return results
