package com.sstech.graphdb.transformer.client.services;

import com.sstech.graphdb.transformer.client.TransformerClient;
import com.sstech.graphdb.grpc.*;
import io.grpc.stub.StreamObserver;

public class OldServicesToGraphLoader extends ServicesToGraphLoaderGrpc.ServicesToGraphLoaderImplBase {


    @Override
    public void testAPI(DummyMessage request,
                                StreamObserver<DummyMessageStatus> responseObserver) {

        System.out.println("Sending ping to sink by passing processing in Transformer");
        System.out.println(String.format("Source: %s and Message %s", request.getSource(), request.getMessage()));

        DummyMessageStatus response = DummyMessageStatus.newBuilder().
                setMessage(request.getMessage() + " inside ServicesTransformer").
                setStatus("Computed inside TransformerServer").
                setSource(this.getClass().toGenericString()).
                addCurrent("Transformer").build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}
