import sys
import pkg_resources
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
                                  for i in installed_packages])
print(installed_packages_list)
print(sys.executable)
print(sys.path)
import grpc
from concurrent import futures
import os
# print(os.listdir("/miniconda/envs/snowflake-graphdb/lib/python3.7/site-packages"))
print(os.getcwd())
sys.path.append(os.path.abspath(os.getcwd() + "../../"))
print(sys.path[-2:])

# import the generated classes
from gen import graphdb_pb2_grpc
from server.GraphTransformerController import GraphTransformerController
from utils.constants import Commons, APPLICATION_PROPERTIES


class GraphTransformerServer:
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
        graphdb_pb2_grpc.add_ServicesToGraphTransformerServicer_to_server(
            GraphTransformerController(), server)
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
    server = GraphTransformerServer(config)
    server.start()
