package com.sstech.graphdb.graph_app.client;

import com.google.protobuf.Empty;
import com.sstech.graphdb.graph_app.beans.CaseExportPayloadBean;
import com.sstech.graphdb.graph_app.beans.EntityQueryBean;
import com.sstech.graphdb.graph_app.beans.EntityTypeQueryBean;
import com.sstech.graphdb.grpc.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.net.ConnectException;
import java.util.Calendar;
import java.util.Date;

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

    private CaseSubmissionPayload convertToGrpcPayloadForCaseSubmission(CaseExportPayloadBean payloadBean) {

        CaseSubmissionPayload.Builder payload = CaseSubmissionPayload.newBuilder();

        if (payloadBean.getURLs() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getURLs();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("URLs", builder.build());
        }

        if (payloadBean.getUser() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getUser();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();

                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("user", builder.build());
        }

        if (payloadBean.getIP() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getIP();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("IPs", builder.build());
        }

        if (payloadBean.getHosts() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getHosts();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("hosts", builder.build());
        }

        if (payloadBean.getChildProcesses() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getChildProcesses();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("childProcess", builder.build());
        }

        if (payloadBean.getProcesses() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getProcesses();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("process", builder.build());
        }

        if (payloadBean.getEmails() != null) {
            EntityTypeQuery.Builder builder = EntityTypeQuery.newBuilder();

            EntityTypeQueryBean queries = payloadBean.getEmails();
            for (EntityQueryBean entityQuery : queries.getEntityQueries()) {
                EntityQuery.Builder innerBuilder = EntityQuery.newBuilder();
                if (entityQuery.getValue() != null)
                    innerBuilder.setValue(entityQuery.getValue());
                if (entityQuery.getDataSource() != null)
                    innerBuilder.setDataSource(entityQuery.getDataSource());
                if (entityQuery.getStartDate() != null)
                    innerBuilder.setStartDate(convertJavaDateToGrpcTime(entityQuery.getStartDate()));
                if (entityQuery.getEndDate() != null)
                    innerBuilder.setEndDate(convertJavaDateToGrpcTime(entityQuery.getEndDate()));

                builder.addEntityQuery(innerBuilder.build());
            }
            payload.putQuery("email", builder.build());
        }

        return payload.build();
    }

    private Time convertJavaDateToGrpcTime(Date time) {
        Calendar c = Calendar.getInstance();
        c.setTime(time);
        return Time.newBuilder().
                setDay(c.get(Calendar.DATE)).setMinutes(c.get(Calendar.MONTH)).setYear(c.get(Calendar.YEAR)).
                setHour(c.get(Calendar.HOUR)).setMinutes(c.get(Calendar.MINUTE)).setSeconds(c.get(Calendar.SECOND)).
                build();
    }

    public DummyMessageStatus pingGraphExtractorWithDummySignalMono(String message) {
        DummyMessage request = DummyMessage.newBuilder().
                setMessage(message).
                setSource(this.getClass().toGenericString()).
                build();

        DummyMessageStatus response = routerService.testAPI(request);

        return response;
    }

    public Empty startCaseExport(CaseExportPayloadBean payloadBean) throws ConnectException {
        System.out.println("Connecting to " + host + " : " + port.toString());
        return routerService.startGraphExtraction(convertToGrpcPayloadForCaseSubmission(payloadBean));
    }
}
