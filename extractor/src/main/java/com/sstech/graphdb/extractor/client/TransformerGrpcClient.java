package com.sstech.graphdb.extractor.client;

import com.google.protobuf.Empty;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.grpc.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import org.springframework.beans.factory.annotation.Value;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;


public class TransformerGrpcClient {
    @Value("${grpc.transformer.server.host:#{null}}")
    private String host;
    @Value("${grpc.transformer.server.port:#{null}}")
    private Integer port;

    public TransformerGrpcClient() {
    }

    ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub routerService;
    ServicesToGraphTransformerGrpc.ServicesToGraphTransformerStub routerAsyncService;

    public ServicesToGraphTransformerGrpc.ServicesToGraphTransformerBlockingStub connect() {

        if (host == null && port == null)
            return null;

//        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
//                .usePlaintext().maxInboundMessageSize(100*1024*1024)
//                .build();
        String URL = String.format("%s:%s", host, port);
        System.out.println("Connecting to Transformer server at " + URL);
        ManagedChannel channel = ManagedChannelBuilder.forTarget(URL)
                .usePlaintext().maxInboundMessageSize(250*1024*1024)
                .build();

        routerService = ServicesToGraphTransformerGrpc.newBlockingStub(channel);
        routerAsyncService = ServicesToGraphTransformerGrpc.newStub(channel);

        return routerService;
    }

    // Create a function here to call TransformerServices by parsing the ResultSet from StoredProc and converting to IncomingDataFormat

    public DummyMessageStatus pingGraphTransformerWithDummySignalMono(String message) {
        DummyMessage request = DummyMessage.newBuilder().
                setMessage(message).
                setSource(this.getClass().toGenericString()).
                build();

        DummyMessageStatus response = routerService.testAPI(request);

        return response;
    }

    public Empty startTransformationAndLoadingOfGraph(IncomingDataFormat data) {
        routerService.transformAndLoadData(data);
        System.out.println("Returned from transformer");
        return Empty.getDefaultInstance();
    }

    public Empty startTransformationOfGraph(IncomingDataFormat data) {
        routerService.transformRawDataToGraph(data);
        System.out.println("Returned from transformer usng only transformation");
        return Empty.getDefaultInstance();
    }

    public Empty startGraphTransformationFromIntermediateTable(String caseId, CaseSubmissionPayload request) {
        Credentials credentials = ConstantsAndUtils.getSnowflakeCredentials();
        String extractionOutputTable = credentials.getAdditionalParametersOrThrow("extraction_output_tbl");

        ExportedDataInfo info = ExportedDataInfo.newBuilder().setCaseId(caseId).setTable(extractionOutputTable).build();
        return routerService.transformExtractedDataFromIntermediateTable(info);
    }

    public Empty streamDataForTransformationUsingSpark(List<WindowsRecord> windowsRecords,
                                                       List<WatchGuardRecord> watchGuardRecords,
                                                       List<MsExchangeRecord> exchangeRecords,
                                                       List<SysmonRecord> sysmonRecords,
                                                       List<SEPCRecord> sepcRecords, String caseId,
                                                       CoreGrpcClient coreClient, CaseSubmissionPayload request) {
        if (windowsRecords == null) {
            System.out.println("Windows record is null so initializing as blank");
            windowsRecords = new ArrayList<>();
        }
        if (watchGuardRecords == null) {
            System.out.println("watchguard record is null so initializing as blank");
            watchGuardRecords = new ArrayList<>();
        }
        if (exchangeRecords == null) {
            System.out.println("MsExchange record is null so initializing as blank");
            exchangeRecords = new ArrayList<>();
        }
        if (sysmonRecords == null) {
            System.out.println("Sysmon record is null so initializing as blank");
            sysmonRecords = new ArrayList<>();
        }
        if (sepcRecords == null) {
            System.out.println("SEPC record is null so initializing as blank");
            sepcRecords = new ArrayList<>();
        }

        final CountDownLatch finishLatch = new CountDownLatch(1);
        StreamObserver<Empty> responseObserver = new StreamObserver<Empty>() {
            @Override
            public void onNext(Empty response) {
                System.out.println("Finished sending a record to transformer");
            }

            @Override
            public void onError(Throwable t) {
                Status status = Status.fromThrowable(t);
                t.printStackTrace();

                StringWriter sw = new StringWriter();
                t.printStackTrace(new PrintWriter(sw));
                String exceptionAsString = sw.toString();
                System.out.println(String.format("Streaming data to Transformer failed %s", status));
                coreClient.updateCaseLoadingStatus(String.format("Streaming data to Transformer failed %s, " +
                        "\nStacktrace:\n%s", status, exceptionAsString), request, request.getCaseId());
                finishLatch.countDown();
            }

            @Override
            public void onCompleted() {
                System.out.println("Finished Transmitting data to GraphTransformer");
                finishLatch.countDown();
            }
        };

        StreamObserver<GraphTransformerDataFormat> requestObserver = routerAsyncService.
                withDeadlineAfter(100L, TimeUnit.MINUTES).transformStreamDataOnDataBricks(responseObserver);
        long STREAM_BATCH_SIZE = 150000;

        try {
            System.out.println("Streaming windows records");
            for (int i=0; i< windowsRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= windowsRecords.size())
                        break;
                    WindowsRecord record = windowsRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).
                            setWindowsRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed windows record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming MsExchange records");
            for (int i=0; i< exchangeRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= exchangeRecords.size())
                        break;
                    MsExchangeRecord record = exchangeRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).
                            setExchangeRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (exchangeRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed msexchange record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming SysMon records");
            for (int i=0; i< sysmonRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= sysmonRecords.size())
                        break;
                    SysmonRecord record = sysmonRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).
                            setSysmonRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (sysmonRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed sysmon record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming SEPC records");
            for (int i=0; i< sepcRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= sepcRecords.size())
                        break;
                    SEPCRecord record = sepcRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).
                            setSepcRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (sepcRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed windows record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming WgTraffic records");
            for (int i=0; i< watchGuardRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= watchGuardRecords.size())
                        break;
                    WatchGuardRecord record = watchGuardRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).
                            setNetworkRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (watchGuardRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed watchguard record for batch num %d of %d", batch_num, tot_batch));
            }
        } catch (RuntimeException e) {
            // Cancel RPC
            requestObserver.onError(e);
            throw e;
        }
        // Mark the end of requests
        requestObserver.onCompleted();
        // Receiving happens asynchronously
        try {
            finishLatch.await(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return Empty.getDefaultInstance();
    }

    public Empty streamDataForTransformation(List<WindowsRecord> windowsRecords, List<WatchGuardRecord> watchGuardRecords,
                                             List<MsExchangeRecord> exchangeRecords, List<SysmonRecord> sysmonRecords,
                                             List<SEPCRecord> sepcRecords, String caseId, CoreGrpcClient coreClient,
                                             TransformerGrpcClient transformerClient, CaseSubmissionPayload request) {

        if (windowsRecords == null) {
            System.out.println("Windows record is null so initializing as blank");
            windowsRecords = new ArrayList<>();
        }
        if (watchGuardRecords == null) {
            System.out.println("watchguard record is null so initializing as blank");
            watchGuardRecords = new ArrayList<>();
        }
        if (exchangeRecords == null) {
            System.out.println("MsExchange record is null so initializing as blank");
            exchangeRecords = new ArrayList<>();
        }
        if (sysmonRecords == null) {
            System.out.println("Sysmon record is null so initializing as blank");
            sysmonRecords = new ArrayList<>();
        }
        if (sepcRecords == null) {
            System.out.println("SEPC record is null so initializing as blank");
            sepcRecords = new ArrayList<>();
        }

//        final List<WindowsRecord> windows = windowsRecords;
//        final List<WatchGuardRecord> network = watchGuardRecords;
//        final List<SysmonRecord> sysmon = sysmonRecords;
//        final List<SEPCRecord> sepc = sepcRecords;
//        final List<MsExchangeRecord> exchange = exchangeRecords;

        final CountDownLatch finishLatch = new CountDownLatch(1);
        StreamObserver<Empty> responseObserver = new StreamObserver<Empty>() {
            @Override
            public void onNext(Empty response) {
                System.out.println("Finished sending a record to transformer");
            }

            @Override
            public void onError(Throwable t) {
                Status status = Status.fromThrowable(t);
                t.printStackTrace();

                StringWriter sw = new StringWriter();
                t.printStackTrace(new PrintWriter(sw));
                String exceptionAsString = sw.toString();
                System.out.println(String.format("Streaming data to Transformer failed %s", status));
                System.out.println("Going to fallback method of transferring data by batch");
                coreClient.updateCaseLoadingStatus(String.format("Streaming data to Transformer failed %s, \nStacktrace:\n%s", status, exceptionAsString), request, request.getCaseId());
//
//                coreClient.updateCaseLoadingStatus("Stream data as batch as fallback method", request, request.getCaseId());
//                IncomingDataFormat transformerFormat = IncomingDataFormat.newBuilder().
//                        setCaseId(caseId).
//                        addAllWindowsRecords(windows).
//                        addAllNetworkRecords(network).
//                        addAllExchangeRecords(exchange).
//                        addAllSepcRecords(sepc).
//                        addAllSysmonRecords(sysmon).
//                        build();
//                transformerClient.startTransformationOfGraph(transformerFormat);
                finishLatch.countDown();
            }

            @Override
            public void onCompleted() {
                System.out.println("Finished RecordRoute");
                finishLatch.countDown();
            }
        };

//        StreamObserver<GraphTransformerDataFormat> requestObserver = routerAsyncService.transformStreamRawDataToGraph(responseObserver);
        StreamObserver<GraphTransformerDataFormat> requestObserver = routerAsyncService.withDeadlineAfter(100L, TimeUnit.MINUTES).transformStreamRawDataToGraph(responseObserver);
        List<Object> totData = new ArrayList<>(Collections.singletonList(windowsRecords));
        totData.addAll(sepcRecords);
        totData.addAll(exchangeRecords);
        totData.addAll(watchGuardRecords);
        totData.addAll(sysmonRecords);
        int totDataSize = totData.size();
        long STREAM_BATCH_SIZE = 100000;
        try {
            System.out.println("Streaming windows records");
            for (int i=0; i< windowsRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= windowsRecords.size())
                        break;
                    WindowsRecord record = windowsRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setWindowsRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed windows record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming MsExchange records");
            for (int i=0; i< exchangeRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= exchangeRecords.size())
                        break;
                    MsExchangeRecord record = exchangeRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setExchangeRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed msexchange record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming SysMon records");
            for (int i=0; i< sysmonRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= sysmonRecords.size())
                        break;
                    SysmonRecord record = sysmonRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setSysmonRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed sysmon record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming SEPC records");
            for (int i=0; i< sepcRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= sepcRecords.size())
                        break;
                    SEPCRecord record = sepcRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setSepcRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed windows record for batch num %d of %d", batch_num, tot_batch));
            }
            System.out.println("Streaming WgTraffic records");
            for (int i=0; i< watchGuardRecords.size(); i+=STREAM_BATCH_SIZE) {
                for (int j=i; j<i+STREAM_BATCH_SIZE; ++j) {
                    if (j >= watchGuardRecords.size())
                        break;
                    WatchGuardRecord record = watchGuardRecords.get(j);
                    GraphTransformerDataFormat datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setNetworkRecord(record).build();
                    requestObserver.onNext(datanum);
                    try {
                        Thread.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (finishLatch.getCount() == 0) {
                        return null;
                    }
                }
                int batch_num = (int) (i/STREAM_BATCH_SIZE)+1;
                int tot_batch = (int) (windowsRecords.size()/STREAM_BATCH_SIZE)+1;
                System.out.println(String.format("Streamed watchguard record for batch num %d of %d", batch_num, tot_batch));
            }
        } catch (RuntimeException e) {
            // Cancel RPC
            requestObserver.onError(e);
            throw e;
        }

//        try {
//            // Send numPoints points randomly selected from the features list.
////            Random rand = new Random();
//            for (int i = 0; i < totDataSize; ++i) {
//                GraphTransformerDataFormat datanum = null;
//                if (i < windowsRecords.size()){
//                    int idx = i;
//                    datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setWindowsRecord(windowsRecords.get(idx)).build();
//                }
//                else if ((windowsRecords.size() <= i) && (i < sepcRecords.size())) {
//                    int idx = i - windowsRecords.size();
//                    datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setSepcRecord(sepcRecords.get(idx)).build();
//                }
//                else if (((windowsRecords.size()+sepcRecords.size()) <= i) && (i < exchangeRecords.size())) {
//                    int idx = i - (windowsRecords.size()+sepcRecords.size());
//                    datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setExchangeRecord(exchangeRecords.get(idx)).build();
//                }
//                else if (((windowsRecords.size()+sepcRecords.size()+exchangeRecords.size()) <= i) && (i < watchGuardRecords.size())) {
//                    int idx = i - (windowsRecords.size()+sepcRecords.size()+exchangeRecords.size());
//                    datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setNetworkRecord(watchGuardRecords.get(idx)).build();
//                }
//                else {
//                    int idx = i - (windowsRecords.size()+sepcRecords.size()+exchangeRecords.size()+watchGuardRecords.size());
//                    datanum = GraphTransformerDataFormat.newBuilder().setCaseId(caseId).setSysmonRecord(sysmonRecords.get(idx)).build();
//                }
//
//                requestObserver.onNext(datanum);
//                try {
//                    Thread.sleep(1);
//                } catch (InterruptedException e) {
//                    e.printStackTrace();
//                }
//                if (finishLatch.getCount() == 0) {
//                    // RPC completed or errored before we finished sending.
//                    // Sending further requests won't error, but they will just be thrown away.
//                    return null;
//                }
//            }
//        } catch (RuntimeException e) {
//            // Cancel RPC
//            requestObserver.onError(e);
//            throw e;
//        }
        // Mark the end of requests
        requestObserver.onCompleted();

        // Receiving happens asynchronously
        try {
            finishLatch.await(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        return Empty.getDefaultInstance();
    }
}
