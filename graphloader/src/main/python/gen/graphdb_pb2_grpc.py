# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import gen.graphdb_pb2 as graphdb__pb2


class ServicesToGraphLoaderStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.EnsureGraphInSnowFlake = channel.unary_unary(
                '/ServicesToGraphLoader/EnsureGraphInSnowFlake',
                request_serializer=graphdb__pb2.GraphFormat.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.TestAPI = channel.unary_unary(
                '/ServicesToGraphLoader/TestAPI',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )
        self.EnsureGraphInSnowFlakeStream = channel.stream_unary(
                '/ServicesToGraphLoader/EnsureGraphInSnowFlakeStream',
                request_serializer=graphdb__pb2.GraphLoaderDataFormat.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.EnsureGraphInSnowFromFromTable = channel.unary_unary(
                '/ServicesToGraphLoader/EnsureGraphInSnowFromFromTable',
                request_serializer=graphdb__pb2.TransformedDataTable.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class ServicesToGraphLoaderServicer(object):
    """Missing associated documentation comment in .proto file"""

    def EnsureGraphInSnowFlake(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TestAPI(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def EnsureGraphInSnowFlakeStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def EnsureGraphInSnowFromFromTable(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesToGraphLoaderServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'EnsureGraphInSnowFlake': grpc.unary_unary_rpc_method_handler(
                    servicer.EnsureGraphInSnowFlake,
                    request_deserializer=graphdb__pb2.GraphFormat.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'TestAPI': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAPI,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
            'EnsureGraphInSnowFlakeStream': grpc.stream_unary_rpc_method_handler(
                    servicer.EnsureGraphInSnowFlakeStream,
                    request_deserializer=graphdb__pb2.GraphLoaderDataFormat.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'EnsureGraphInSnowFromFromTable': grpc.unary_unary_rpc_method_handler(
                    servicer.EnsureGraphInSnowFromFromTable,
                    request_deserializer=graphdb__pb2.TransformedDataTable.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServicesToGraphLoader', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ServicesToGraphLoader(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def EnsureGraphInSnowFlake(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphLoader/EnsureGraphInSnowFlake',
            graphdb__pb2.GraphFormat.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TestAPI(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphLoader/TestAPI',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def EnsureGraphInSnowFlakeStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/ServicesToGraphLoader/EnsureGraphInSnowFlakeStream',
            graphdb__pb2.GraphLoaderDataFormat.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def EnsureGraphInSnowFromFromTable(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphLoader/EnsureGraphInSnowFromFromTable',
            graphdb__pb2.TransformedDataTable.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class ServicesToGraphCoreStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UpdateCaseLoadingStatus = channel.unary_unary(
                '/ServicesToGraphCore/UpdateCaseLoadingStatus',
                request_serializer=graphdb__pb2.CaseLoadingStatus.SerializeToString,
                response_deserializer=graphdb__pb2.CaseLoadingStatus.FromString,
                )
        self.UpdateCaseLoadingProperties = channel.unary_unary(
                '/ServicesToGraphCore/UpdateCaseLoadingProperties',
                request_serializer=graphdb__pb2.CaseLoadingProperties.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.UpdateNodesForCase = channel.stream_unary(
                '/ServicesToGraphCore/UpdateNodesForCase',
                request_serializer=graphdb__pb2.CaseNode.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.IsCaseExported = channel.unary_unary(
                '/ServicesToGraphCore/IsCaseExported',
                request_serializer=graphdb__pb2.CaseSubmissionPayload.SerializeToString,
                response_deserializer=graphdb__pb2.CaseExportStatus.FromString,
                )
        self.GetCaseIds = channel.unary_stream(
                '/ServicesToGraphCore/GetCaseIds',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=graphdb__pb2.CaseExportStatus.FromString,
                )
        self.GetCaseLoadingStatus = channel.unary_unary(
                '/ServicesToGraphCore/GetCaseLoadingStatus',
                request_serializer=graphdb__pb2.CaseInfo.SerializeToString,
                response_deserializer=graphdb__pb2.CaseStatus.FromString,
                )
        self.ExecuteByteCode = channel.unary_unary(
                '/ServicesToGraphCore/ExecuteByteCode',
                request_serializer=graphdb__pb2.ByteCode.SerializeToString,
                response_deserializer=graphdb__pb2.QueryResponse.FromString,
                )
        self.TestAPI = channel.unary_unary(
                '/ServicesToGraphCore/TestAPI',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )
        self.ExecuteStoredProcedure = channel.unary_unary(
                '/ServicesToGraphCore/ExecuteStoredProcedure',
                request_serializer=graphdb__pb2.ProcedureParams.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.GetSnowFlakeCredentials = channel.unary_unary(
                '/ServicesToGraphCore/GetSnowFlakeCredentials',
                request_serializer=graphdb__pb2.DataBaseIdentifier.SerializeToString,
                response_deserializer=graphdb__pb2.Credentials.FromString,
                )


class ServicesToGraphCoreServicer(object):
    """Missing associated documentation comment in .proto file"""

    def UpdateCaseLoadingStatus(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateCaseLoadingProperties(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateNodesForCase(self, request_iterator, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IsCaseExported(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCaseIds(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCaseLoadingStatus(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteByteCode(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TestAPI(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteStoredProcedure(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSnowFlakeCredentials(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesToGraphCoreServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UpdateCaseLoadingStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateCaseLoadingStatus,
                    request_deserializer=graphdb__pb2.CaseLoadingStatus.FromString,
                    response_serializer=graphdb__pb2.CaseLoadingStatus.SerializeToString,
            ),
            'UpdateCaseLoadingProperties': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateCaseLoadingProperties,
                    request_deserializer=graphdb__pb2.CaseLoadingProperties.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'UpdateNodesForCase': grpc.stream_unary_rpc_method_handler(
                    servicer.UpdateNodesForCase,
                    request_deserializer=graphdb__pb2.CaseNode.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'IsCaseExported': grpc.unary_unary_rpc_method_handler(
                    servicer.IsCaseExported,
                    request_deserializer=graphdb__pb2.CaseSubmissionPayload.FromString,
                    response_serializer=graphdb__pb2.CaseExportStatus.SerializeToString,
            ),
            'GetCaseIds': grpc.unary_stream_rpc_method_handler(
                    servicer.GetCaseIds,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=graphdb__pb2.CaseExportStatus.SerializeToString,
            ),
            'GetCaseLoadingStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCaseLoadingStatus,
                    request_deserializer=graphdb__pb2.CaseInfo.FromString,
                    response_serializer=graphdb__pb2.CaseStatus.SerializeToString,
            ),
            'ExecuteByteCode': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteByteCode,
                    request_deserializer=graphdb__pb2.ByteCode.FromString,
                    response_serializer=graphdb__pb2.QueryResponse.SerializeToString,
            ),
            'TestAPI': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAPI,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
            'ExecuteStoredProcedure': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteStoredProcedure,
                    request_deserializer=graphdb__pb2.ProcedureParams.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'GetSnowFlakeCredentials': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSnowFlakeCredentials,
                    request_deserializer=graphdb__pb2.DataBaseIdentifier.FromString,
                    response_serializer=graphdb__pb2.Credentials.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServicesToGraphCore', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ServicesToGraphCore(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def UpdateCaseLoadingStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/UpdateCaseLoadingStatus',
            graphdb__pb2.CaseLoadingStatus.SerializeToString,
            graphdb__pb2.CaseLoadingStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateCaseLoadingProperties(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/UpdateCaseLoadingProperties',
            graphdb__pb2.CaseLoadingProperties.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateNodesForCase(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/ServicesToGraphCore/UpdateNodesForCase',
            graphdb__pb2.CaseNode.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IsCaseExported(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/IsCaseExported',
            graphdb__pb2.CaseSubmissionPayload.SerializeToString,
            graphdb__pb2.CaseExportStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetCaseIds(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ServicesToGraphCore/GetCaseIds',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            graphdb__pb2.CaseExportStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetCaseLoadingStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/GetCaseLoadingStatus',
            graphdb__pb2.CaseInfo.SerializeToString,
            graphdb__pb2.CaseStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ExecuteByteCode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/ExecuteByteCode',
            graphdb__pb2.ByteCode.SerializeToString,
            graphdb__pb2.QueryResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TestAPI(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/TestAPI',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ExecuteStoredProcedure(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/ExecuteStoredProcedure',
            graphdb__pb2.ProcedureParams.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetSnowFlakeCredentials(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphCore/GetSnowFlakeCredentials',
            graphdb__pb2.DataBaseIdentifier.SerializeToString,
            graphdb__pb2.Credentials.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class ServicesToGraphTransformerStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.TestAPI = channel.unary_unary(
                '/ServicesToGraphTransformer/TestAPI',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )
        self.TransformRawDataToGraph = channel.unary_unary(
                '/ServicesToGraphTransformer/TransformRawDataToGraph',
                request_serializer=graphdb__pb2.IncomingDataFormat.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.TransformStreamRawDataToGraph = channel.stream_unary(
                '/ServicesToGraphTransformer/TransformStreamRawDataToGraph',
                request_serializer=graphdb__pb2.GraphTransformerDataFormat.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.TransformAndLoadData = channel.unary_unary(
                '/ServicesToGraphTransformer/TransformAndLoadData',
                request_serializer=graphdb__pb2.IncomingDataFormat.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class ServicesToGraphTransformerServicer(object):
    """Missing associated documentation comment in .proto file"""

    def TestAPI(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TransformRawDataToGraph(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TransformStreamRawDataToGraph(self, request_iterator, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TransformAndLoadData(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesToGraphTransformerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'TestAPI': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAPI,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
            'TransformRawDataToGraph': grpc.unary_unary_rpc_method_handler(
                    servicer.TransformRawDataToGraph,
                    request_deserializer=graphdb__pb2.IncomingDataFormat.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'TransformStreamRawDataToGraph': grpc.stream_unary_rpc_method_handler(
                    servicer.TransformStreamRawDataToGraph,
                    request_deserializer=graphdb__pb2.GraphTransformerDataFormat.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'TransformAndLoadData': grpc.unary_unary_rpc_method_handler(
                    servicer.TransformAndLoadData,
                    request_deserializer=graphdb__pb2.IncomingDataFormat.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServicesToGraphTransformer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ServicesToGraphTransformer(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def TestAPI(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphTransformer/TestAPI',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TransformRawDataToGraph(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphTransformer/TransformRawDataToGraph',
            graphdb__pb2.IncomingDataFormat.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TransformStreamRawDataToGraph(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/ServicesToGraphTransformer/TransformStreamRawDataToGraph',
            graphdb__pb2.GraphTransformerDataFormat.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TransformAndLoadData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphTransformer/TransformAndLoadData',
            graphdb__pb2.IncomingDataFormat.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class ServicesToGraphAppStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.TestAPI = channel.unary_unary(
                '/ServicesToGraphApp/TestAPI',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )
        self.StartGraphETL = channel.unary_unary(
                '/ServicesToGraphApp/StartGraphETL',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )


class ServicesToGraphAppServicer(object):
    """Missing associated documentation comment in .proto file"""

    def TestAPI(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartGraphETL(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesToGraphAppServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'TestAPI': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAPI,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
            'StartGraphETL': grpc.unary_unary_rpc_method_handler(
                    servicer.StartGraphETL,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServicesToGraphApp', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ServicesToGraphApp(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def TestAPI(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphApp/TestAPI',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StartGraphETL(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphApp/StartGraphETL',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class ServicesToGraphExtractorStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StartGraphExtraction = channel.unary_unary(
                '/ServicesToGraphExtractor/StartGraphExtraction',
                request_serializer=graphdb__pb2.CaseSubmissionPayload.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.TestAPI = channel.unary_unary(
                '/ServicesToGraphExtractor/TestAPI',
                request_serializer=graphdb__pb2.DummyMessage.SerializeToString,
                response_deserializer=graphdb__pb2.DummyMessageStatus.FromString,
                )


class ServicesToGraphExtractorServicer(object):
    """Missing associated documentation comment in .proto file"""

    def StartGraphExtraction(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TestAPI(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesToGraphExtractorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StartGraphExtraction': grpc.unary_unary_rpc_method_handler(
                    servicer.StartGraphExtraction,
                    request_deserializer=graphdb__pb2.CaseSubmissionPayload.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'TestAPI': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAPI,
                    request_deserializer=graphdb__pb2.DummyMessage.FromString,
                    response_serializer=graphdb__pb2.DummyMessageStatus.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ServicesToGraphExtractor', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ServicesToGraphExtractor(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def StartGraphExtraction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphExtractor/StartGraphExtraction',
            graphdb__pb2.CaseSubmissionPayload.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TestAPI(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ServicesToGraphExtractor/TestAPI',
            graphdb__pb2.DummyMessage.SerializeToString,
            graphdb__pb2.DummyMessageStatus.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
