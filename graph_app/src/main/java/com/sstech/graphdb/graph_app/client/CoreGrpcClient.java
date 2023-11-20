package com.sstech.graphdb.graph_app.client;

import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphAppGrpc;
import com.sstech.graphdb.grpc.ServicesToGraphCoreGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

public class CoreGrpcClient {
    @Value("${grpc.core.server.host:#{null}}")
    private String host;
    @Value("${grpc.core.server.port:#{null}}")
    private Integer port;

    public CoreGrpcClient() {
    }

    ServicesToGraphCoreGrpc.ServicesToGraphCoreBlockingStub routerService;

    public ServicesToGraphCoreGrpc.ServicesToGraphCoreBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphCoreGrpc.newBlockingStub(channel);
        return routerService;
    }

    public DummyMessageStatus pingGraphCoreWithDummySignalMono(String message) {
        throw new NotImplementedException();
    }
}
