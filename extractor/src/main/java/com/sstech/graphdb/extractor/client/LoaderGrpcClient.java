package com.sstech.graphdb.extractor.client;

import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphLoaderGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.env.Environment;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

public class LoaderGrpcClient {
    @Value("${grpc.loader.server.host:#{null}}")
    private String host;
    @Value("${grpc.loader.server.port:#{null}}")
    private Integer port;

    public LoaderGrpcClient() {
    }

    ServicesToGraphLoaderGrpc.ServicesToGraphLoaderBlockingStub routerService;

    public ServicesToGraphLoaderGrpc.ServicesToGraphLoaderBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphLoaderGrpc.newBlockingStub(channel);
        return routerService;
    }

    public DummyMessageStatus pingGraphLoaderWithDummySignalMono(String message) {
        throw new NotImplementedException();
    }
}
