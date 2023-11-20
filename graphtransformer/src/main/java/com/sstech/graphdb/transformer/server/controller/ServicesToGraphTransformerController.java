package com.sstech.graphdb.transformer.server.controller;

import com.sstech.graphdb.transformer.client.CoreGrpcClient;
import com.sstech.graphdb.transformer.client.LoaderGrpcClient;
import com.sstech.graphdb.grpc.DummyMessage;
import com.sstech.graphdb.grpc.DummyMessageStatus;
import com.sstech.graphdb.grpc.ServicesToGraphTransformerGrpc;
import com.sstech.graphdb.transformer.client.TransformerGrpcClient;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.beans.factory.annotation.Autowired;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;


@GrpcService
public class ServicesToGraphTransformerController extends ServicesToGraphTransformerGrpc.ServicesToGraphTransformerImplBase {
    // This class receives signal from GraphExtractor using ServicesToGraphTransformer service
    @Autowired
    private LoaderGrpcClient loaderGrpcClient;
    @Autowired
    private CoreGrpcClient coreGrpcClient;
    @Autowired
    private TransformerGrpcClient transformerGrpcClient;

    @Override
    public void testAPI(DummyMessage request, StreamObserver<DummyMessageStatus> responseObserver) {

        Object service = loaderGrpcClient.connect();
        if (service == null)
            try {
                throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
                        "HOST/PORT isn't defined in application.properties in extractor");
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }

        DummyMessageStatus resp =
                loaderGrpcClient.pingGraphLoaderWithDummySignalMono(request.getMessage() + " sent from TransformerServer");

        System.out.println("Printing response from graphLoader");
        System.out.println(resp);
        System.out.println("===============");

        DummyMessageStatus response = DummyMessageStatus.newBuilder().
                setMessage(resp.getMessage() + " inside TransformerGrpcServer").
                setStatus("Computed inside TransformerServer").
                setSource(this.getClass().toGenericString()).
                addAllCurrent(resp.getCurrentList()).addCurrent("Transformer").build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

}
