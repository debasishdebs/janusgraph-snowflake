package com.sstech.graphdb.transformer.server;

import com.sstech.graphdb.transformer.client.services.OldServicesToGraphCore;
import com.sstech.graphdb.transformer.client.services.OldServicesToGraphLoader;
import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

public class TestGrpcServer {
    private final Logger logger = Logger.getLogger(this.getClass().getSimpleName());

    private final int port;
    private final Server rpcServer;

    public TestGrpcServer(int port) {
        this(ServerBuilder.forPort(port), port);
    }

    public TestGrpcServer(ServerBuilder<?> serverBuilder, int port) {
        rpcServer = serverBuilder.
                addService(new OldServicesToGraphLoader()).
                addService(new OldServicesToGraphCore()).
                build();
        this.port = port;
    }

    /** Start serving requests. */
    public void start() throws IOException {
        rpcServer.start();
        logger.info("Server started, listening on " + port);
        System.out.println("Server started, listening on " + port);

        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC server since JVM is shutting down");
                try {
                    TestGrpcServer.this.stop();
                } catch (InterruptedException e) {
                    e.printStackTrace(System.err);
                }
                System.err.println("*** server shut down");
            }
        });
    }

    /** Stop serving requests and shutdown resources. */
    public void stop() throws InterruptedException {
        if (rpcServer != null) {
            rpcServer.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (rpcServer != null) {
            rpcServer.awaitTermination();
        }
    }

    public static void main(String[] args) throws Exception {
        TestGrpcServer server = new TestGrpcServer(1010);
        server.start();
        server.blockUntilShutdown();
    }
}
