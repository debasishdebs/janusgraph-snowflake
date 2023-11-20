from grpc_tools import protoc


if __name__ == '__main__':
    proto_include = protoc.pkg_resources.resource_filename('grpc_tools', '_proto')

    protoc.main((
        __file__,
        '--proto_path={}'.format(proto_include),
        '-I../../../proto',
        '--python_out=../gen',
        '--grpc_python_out=../gen',
        '../../../proto/graphdb.proto',
    ))
