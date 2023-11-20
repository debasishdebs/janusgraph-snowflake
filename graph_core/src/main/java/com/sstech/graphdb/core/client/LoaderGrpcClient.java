package com.sstech.graphdb.core.client;

import com.sstech.graphdb.grpc.DummyMessage;
import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphLoaderGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;

public class LoaderGrpcClient {
    @Value("${grpc.loader.server.host:#{null}}")
    private String host;
    @Value("${grpc.loader.server.port:#{null}}")
    private Integer port;

    public LoaderGrpcClient() {
    }

    public LoaderGrpcClient(String host, Integer port) {
        this.host = host;
        this.port = port;
    }

    ServicesToGraphLoaderGrpc.ServicesToGraphLoaderBlockingStub routerService;

    public ServicesToGraphLoaderGrpc.ServicesToGraphLoaderBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        System.out.println("Connected to " + host + " : " + port);

        routerService = ServicesToGraphLoaderGrpc.newBlockingStub(channel);
        return routerService;
    }

    public DummyMessageStatus pingGraphLoaderWithDummySignalMono(String message) {
        DummyMessage request = DummyMessage.newBuilder().
                setMessage(message).
                setSource(this.getClass().toGenericString()).
                build();

        DummyMessageStatus response = routerService.testAPI(request);

        return response;
    }
}
