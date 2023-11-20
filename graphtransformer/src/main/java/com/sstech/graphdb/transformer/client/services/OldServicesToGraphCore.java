package com.sstech.graphdb.transformer.client.services;

import com.sstech.graphdb.grpc.CaseLoadingStatus;
import com.sstech.graphdb.grpc.ServicesToGraphCoreGrpc;
import io.grpc.stub.StreamObserver;

public class OldServicesToGraphCore extends ServicesToGraphCoreGrpc.ServicesToGraphCoreImplBase {
    @Override
    public void updateCaseLoadingStatus(CaseLoadingStatus request,
                                        StreamObserver<CaseLoadingStatus> responseObserver) {
        responseObserver.onCompleted();
    }
}
