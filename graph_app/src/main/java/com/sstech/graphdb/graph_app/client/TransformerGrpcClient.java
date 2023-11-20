package com.sstech.graphdb.graph_app.client;

import com.sstech.graphdb.grpc.DummyMessage;
import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphTransformerGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;

public class TransformerGrpcClient {
    @Value("${grpc.transformer.server.host:#{null}}")
    private String host;
    @Value("${grpc.transformer.server.port:#{null}}")
    private Integer port;

    public TransformerGrpcClient() {
    }

    ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub routerService;

    public ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphTransformerGrpc.newBlockingStub(channel);

        return routerService;
    }

    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
        DummyMessage request = DummyMessage.newBuilder().
                setMessage(message).
                setSource(this.getClass().toGenericString()).
                build();

        DummyMessageStatus response = routerService.testAPI(request);

        return response;
    }
}
