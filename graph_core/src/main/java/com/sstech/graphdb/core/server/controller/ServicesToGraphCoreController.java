package com.sstech.graphdb.core.server.controller;

import com.google.protobuf.*;
import com.sstech.graphdb.core.client.AppGrpcClient;
import com.sstech.graphdb.core.client.LoaderGrpcClient;
import com.sstech.graphdb.core.client.TransformerGrpcClient;
import com.sstech.graphdb.core.query.utils.QueryExecutionWrapper;
import com.sstech.graphdb.grpc.*;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.beans.factory.annotation.Autowired;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;


@GrpcService
public class ServicesToGraphCoreController extends ServicesToGraphCoreGrpc.ServicesToGraphCoreImplBase {
    // This class receives signal from GraphExtractor using ServicesToGraphTransformer service
    @Autowired
    private LoaderGrpcClient loaderGrpcClient;
    @Autowired
    private AppGrpcClient coreGrpcClient;
    @Autowired
    private TransformerGrpcClient transformerGrpcClient;

    @Override
    public void executeByteCode(ByteCode request, StreamObserver<QueryResponse> responseObserver) {

        System.out.println("I'm executing byte code");
        System.out.println(request);

        QueryExecutionWrapper executor = new QueryExecutionWrapper(request);
        executor.execute();
        ArrayList<QueryResponse> response = executor.convert();

        for (QueryResponse row : response) {
            responseObserver.onNext(row);
        }

        responseObserver.onCompleted();
    }

    private QueryResponse convertToQueryFromStep(MiddleMostByteCode step) {
        ListFormat.Builder stepsListBuilder = ListFormat.newBuilder();

        step.getMiddleLayerList().forEach( stepMetadata -> {
            // One StepMetadata is StructureValue in itself
            stepsListBuilder.addList(convertFromInnermostLayer(stepMetadata));
        });

        return QueryResponse.newBuilder().setListFormat(stepsListBuilder.build()).build();
    }

    private StructureValue convertFromInnermostLayer(InnerMostByteCode info) {
        StructureValue.Builder value = StructureValue.newBuilder();

        ListValue list = ListValue.newBuilder().addAllValues(
                convertFromProtoStringList(info.getInnerValuesList())).build();

        return value.setListValue(list).build();
    }

    private List<Value> convertFromProtoStringList(ProtocolStringList list) {
        List<Value> values = new ArrayList<>();
        for (String s : list) {
            values.add(
                    Value.newBuilder().setStringValue(s).build()
            );
        }
        return values;
    }

    @Override
    public void updateCaseLoadingStatus(CaseLoadingStatus request, StreamObserver<CaseLoadingStatus> responseObserver) {
        throw new NotImplementedException();
    }

}
