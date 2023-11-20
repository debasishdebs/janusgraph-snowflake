package com.sstech.graphdb.extractor.client;

import com.google.protobuf.Empty;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.grpc.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.time.LocalDateTime;

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

//        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
//                .usePlaintext()
//                .build();

        String URL = String.format("%s:%s", host, port);
        System.out.println("Connecting to Core server at " + URL);
        ManagedChannel channel = ManagedChannelBuilder.forTarget(URL)
                .usePlaintext()
                .build();

        routerService = ServicesToGraphCoreGrpc.newBlockingStub(channel);
        return routerService;
    }

    public Credentials getSnowFlakeCredentials(String database, String schema) {
        return routerService.getSnowFlakeCredentials(
                DataBaseIdentifier.newBuilder().setDatabase(database).setSchema(schema).setCaller("java").build());
    }

    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
        throw new NotImplementedException();
    }

    public CaseLoadingStatus updateCaseLoadingStatus(String status, CaseSubmissionPayload caseInfo, String caseId) {
        LocalDateTime currTime = java.time.LocalDateTime.now();

        CaseInformation info = ConstantsAndUtils.convertCaseSubmissionPayloadToCaseInformation(caseInfo);
        Time processingTime = ConstantsAndUtils.convertJavaTimeToProtoTime(currTime);

        CaseLoadingStatus caseStatus = CaseLoadingStatus.newBuilder().setStatus(status).setQuery(info).
                setCaseId(caseId).setProcessingTime(processingTime).build();

        System.out.printf("CaseId with %s and status %s being updated %n", caseStatus.getCaseId(), caseStatus.getStatus());

        return routerService.updateCaseLoadingStatus(caseStatus);
    }

    public Empty updateCaseLoadingProperties(CaseLoadingProperties properties) {
        return routerService.updateCaseLoadingProperties(properties);
    }
}
