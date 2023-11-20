//package com.sstech.graphdb.extractor.client;
//
//import com.sstech.graphdb.extractor.utils.ConnectionProperties;
//import com.sstech.graphdb.grpc.DummyMessage;
//import com.sstech.graphdb.grpc.DummyMessageStatus;
//import com.sstech.graphdb.grpc.ServicesToGraphTransformerGrpc;
//import io.grpc.ManagedChannel;
//import io.grpc.ManagedChannelBuilder;
//
//public class GrpcClient {
//    ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", ConnectionProperties.GRAPH_TRANSFORMER_GRPC_PORT)
//            .usePlaintext()
//            .build();
//
//    ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub routerService =
//            ServicesToGraphTransformerGrpc.newBlockingStub(channel);
//
//    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
//        DummyMessage request = DummyMessage.newBuilder().
//                    setMessage(message).
//                    setSource(this.getClass().toGenericString()).
//                build();
//
//        DummyMessageStatus response = routerService.checkSignalSentMono(request);
//
//        return response;
//    }
//}
