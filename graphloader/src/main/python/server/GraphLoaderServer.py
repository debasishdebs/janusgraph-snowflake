import grpc
from concurrent import futures
import sys, os
print(os.getcwd())
sys.path.append(os.path.abspath(os.getcwd() + "../../"))
print(sys.path[-2:])

# import the generated classes
from gen import graphdb_pb2_grpc
from server.GraphLoaderController import GraphLoaderController
from utils.constants import Commons, APPLICATION_PROPERTIES


class GraphLoaderServer:
    def __init__(self, config):
        self.config = config

    def start(self):
        host = self.config["grpc.server.host"]
        port = self.config["grpc.server.port"]

        print(f"The host is {host} and port is {port}")

        MAX_MESSAGE_LENGTH = 250 * 1024 * 1024
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_metadata_size', MAX_MESSAGE_LENGTH)
        ]

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(self.config["grpc.server.workers"])), options=options)
        print("Attached server")
        graphdb_pb2_grpc.add_ServicesToGraphLoaderServicer_to_server(
            GraphLoaderController(), server)
        print("Attached service")
        server.add_insecure_port(f'{host}:{port}')
        print("Created channel")
        server.start()
        print("Started server")
        server.wait_for_termination()
        print("Waiting to terminate")
        return self


if __name__ == '__main__':
    # config = load_properties("/app/src/main/resources/application.properties")
    config = Commons.load_properties(APPLICATION_PROPERTIES)

    # print(f'Starting server. Listening on {host}:{port}.')
    # start_server(host, port)
    server = GraphLoaderServer(config)
    server.start()
