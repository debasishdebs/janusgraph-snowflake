package com.sstech.graphdb.transformer.client;


import com.sstech.graphdb.grpc.DummyMessage;
import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphTransformerGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

public class GrpcClient {
    ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 0000)
            .usePlaintext()
            .build();

    ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub routerService =
            ServicesToGraphTransformerGrpc.newBlockingStub(channel);

    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
        DummyMessage request = DummyMessage.newBuilder().
                    setMessage(message).
                    setSource(this.getClass().toGenericString()).
                build();

        DummyMessageStatus response = routerService.testAPI(request);

        return response;
    }
}
