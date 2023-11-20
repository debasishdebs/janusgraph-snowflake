import grpc
from concurrent import futures
import sys, os
print(os.getcwd())
sys.path.append(os.path.abspath(os.getcwd() + "../../"))
print(sys.path[-2:])
# import the generated classes
from gen import graphdb_pb2_grpc
from server.GraphCoreController import GraphCoreController
from utils.utils import Utilities, APPLICATION_PROPERTIES, RESOURCES_PREFIX
from utils.common_resources import Commons
from utils.SnowGraphConnection import SnowGraphConnection


class GraphCoreServer:
    def __init__(self, config):
        self.config = config
        self.APPLICATION_PROPERTIES = config

        database = config["database"]
        schema = config["schema"]

        file_name = f"{database}-{schema}-credentials.properties"
        full_fname = f"{RESOURCES_PREFIX}/resources/{file_name}"
        credential_dict = Utilities.load_properties(full_fname)

        self.CONNECTION = SnowGraphConnection(credential_dict).initialize_snowflake()
        Commons.put_connection(self.CONNECTION)
        Commons.put_properties(config)
        print("Initialized connection")

    def start(self):
        host = self.config["grpc.server.host"]
        port = self.config["grpc.server.port"]

        print(f"The host is {host} and port is {port}")

        MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
        ]

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(self.config["grpc.server.workers"])), options=options)
        print("Attached server")

        graphdb_pb2_grpc.add_ServicesToGraphCoreServicer_to_server(
            GraphCoreController(), server)
        print("Attached service")

        server.add_insecure_port(f'{host}:{port}')
        print("Created channel")

        server.start()
        print("Started server")

        server.wait_for_termination()
        print("Waiting to terminate")
        return self


if __name__ == '__main__':
    # create a gRPC server
    config = Utilities.load_properties(APPLICATION_PROPERTIES)

    server = GraphCoreServer(config)
    server.start()
