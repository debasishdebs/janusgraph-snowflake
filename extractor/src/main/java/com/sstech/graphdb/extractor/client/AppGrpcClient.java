package com.sstech.graphdb.extractor.client;

import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphAppGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

public class AppGrpcClient {
    @Value("${grpc.app.server.host:#{null}}")
    private String host;
    @Value("${grpc.app.server.port:#{null}}")
    private Integer port;

    public AppGrpcClient() {
    }

    ServicesToGraphAppGrpc.ServicesToGraphAppBlockingStub routerService;

    public ServicesToGraphAppGrpc.ServicesToGraphAppBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphAppGrpc.newBlockingStub(channel);
        return routerService;
    }

    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
        throw new NotImplementedException();
    }
}
