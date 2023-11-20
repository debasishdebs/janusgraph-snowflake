package com.sstech.graphdb.transformer.client;

import java.util.Random;
import java.util.logging.Logger;
import com.sstech.graphdb.grpc.*;
import com.sstech.graphdb.transformer.utils.ConnectionProperties;
import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;

public class TransformerClient {
    private static final Logger logger = Logger.getLogger(TransformerClient.class.getName());

    private final ServicesToGraphLoaderGrpc.ServicesToGraphLoaderBlockingStub graphLoaderStub;

    private Random random = new Random();

    public TransformerClient() {
        String graphLoaderTarget = String.format("%s:%d",
                ConnectionProperties.SERVER_HOST, ConnectionProperties.GRAPH_LOADER_PORT);
        String graphCoreTarget = String.format("%s:%d",
                ConnectionProperties.SERVER_HOST, ConnectionProperties.GRAPH_CORE_PORT);

        Channel graphCoreChannel = ManagedChannelBuilder.forTarget(graphLoaderTarget).usePlaintext().build();

        graphLoaderStub = ServicesToGraphLoaderGrpc.newBlockingStub(graphCoreChannel);

    }

    public TransformerClient(String URL) {
        this(ManagedChannelBuilder.forTarget(URL).usePlaintext().build());
    }

    /** Construct client for accessing RouteGuide server using the existing channel. */
    public TransformerClient(Channel channel) {
        graphLoaderStub = ServicesToGraphLoaderGrpc.newBlockingStub(channel);
    }

    public void pingDummyMessageToLoader(String msg) {
        System.out.println("Sending ping to sink");

        DummyMessage message = DummyMessage.newBuilder().
                setMessage(msg).
                setSource("TransformerClient").build();

        System.out.println(String.format("Source: %s and Message %s", message.getSource(), message.getMessage()));

        DummyMessageStatus returnMessage = graphLoaderStub.testAPI(message);

        System.out.println("Succesfully received hook back from GraphLoader with results");
        System.out.println(String.format("Status: %s Message %s Source %s",
                returnMessage.getStatus(), returnMessage.getMessage(), returnMessage.getSource()));
    }

    public static void main(String[] args) {
        String host = "localhost";
        Integer javaPort = 1010;
        Integer pythonPort = 1020;

        TransformerClient client = new TransformerClient(String.format("%s:%s", host, javaPort));
        client.pingDummyMessageToLoader("Debasish");
    }

}
