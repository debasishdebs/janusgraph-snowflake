from process.RawDataExtractor import RawDataExtractor
from process.RecordConverter import RecordConverter


class Loader:
    DATA = None
    EXTRACTED_DATA = None
    TRANSFORMED_DATA: dict = dict()

    def __init__(self):
        pass

    def with_data(self, data):
        print("Loading data into executor")
        self.DATA = data

    def extract(self):
        if self.DATA is None:
            raise AttributeError("Can't transform data if it has not been set. Please call with_data() first")

        print("Extracting data in executor")

        extractor = RawDataExtractor(self.DATA)
        extractor.extract()
        self.EXTRACTED_DATA = extractor.convert()
        return self

    def transform(self):
        if self.EXTRACTED_DATA is None:
            raise AttributeError("Can't transform data if its not yet extracted. Please call extract() first")

        print("Transforming data in executor")
        for ds, records in self.EXTRACTED_DATA.items():
            transformer = RecordConverter(records, ds)
            self.TRANSFORMED_DATA[ds] = transformer.convert()

        return self

    def to_json(self):
        from google.protobuf.json_format import MessageToJson

        for k, graph in self.TRANSFORMED_DATA.items():
            nodes_in_record = graph["nodes"]
            edges_in_record = graph["edges"]
            transformed_nodes = []
            transformed_edges = []

            for edges in edges_in_record:
                transformed_edges_in_record = []
                for edge in edges:
                    for p in edge.keys():
                        if p not in ["left", "right"] and not isinstance(edge[p], str):
                            edge[p] = (edge[p])
                    transformed_edges_in_record.append(edge)
                transformed_edges.append(transformed_edges_in_record)

            for nodes in nodes_in_record:
                transformed_nodes_in_record = []
                for node in nodes:
                    for p in node.keys():
                        if isinstance(node[p], list):
                            if not isinstance(node[p][0], str):
                                node[p] = {MessageToJson(node[p].replace("\n", ""))}
                        else:
                            if not isinstance(node[p], str):
                                node[p] = {MessageToJson(node[p].replace("\n", ""))}

                    transformed_nodes_in_record.append(node)
                transformed_nodes.append(transformed_nodes_in_record)

            graph["nodes"] = transformed_nodes
            graph["edges"] = transformed_edges

        return self

    def load(self):
        raise NotImplementedError("Not implemented loading of data into SnowGraph")


if __name__ == '__main__':
    from utils.sample_data_gen import SampleDataGenerator
    import pprint

    generator = SampleDataGenerator()
    generator.extract()
    data = generator.generate()

    print("Data generated")

    executor = Loader()
    executor.with_data(data)
    executor.extract()
    executor.transform()
    executor.to_json()

    print("Data converted")

    import json
    from gen.graphdb_pb2 import *
    from google.protobuf.json_format import MessageToJson

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (Time, GeoLocation)):
            return MessageToJson(obj)
        raise TypeError ("Type %s not serializable" % type(obj))


    json.dump(executor.TRANSFORMED_DATA, open("../../resources/graph_sample_2.json", "w+"), indent=2, default=json_serial)
