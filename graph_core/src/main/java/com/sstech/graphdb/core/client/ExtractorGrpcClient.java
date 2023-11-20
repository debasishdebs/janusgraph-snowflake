package com.sstech.graphdb.core.client;

import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphExtractorGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

public class ExtractorGrpcClient {
    @Value("${grpc.extractor.server.host:#{null}}")
    private String host;
    @Value("${grpc.extractor.server.port:#{null}}")
    private Integer port;

    public ExtractorGrpcClient() {
    }

    ServicesToGraphExtractorGrpc.ServicesToGraphExtractorBlockingStub routerService;

    public ServicesToGraphExtractorGrpc.ServicesToGraphExtractorBlockingStub connect() {

        if (host == null && port == null)
            return null;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphExtractorGrpc.newBlockingStub(channel);
        return routerService;
    }

    public DummyMessageStatus pingGraphExtractorWithDummySignalMono(String message) {
        throw new NotImplementedException();
    }
}
