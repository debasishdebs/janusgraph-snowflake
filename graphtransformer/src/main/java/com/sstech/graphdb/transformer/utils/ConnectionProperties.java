package com.sstech.graphdb.transformer.utils;

import org.springframework.beans.factory.annotation.Value;

public class ConnectionProperties {
    @Value("${server.host:#{null}}")
    public static String SERVER_HOST;

    @Value("${grpc.loader.server.port:#{null}}")
    public static Integer GRAPH_LOADER_PORT;

    @Value("${grpc.core.server.port:#{null}}")
    public static Integer GRAPH_CORE_PORT;
}
