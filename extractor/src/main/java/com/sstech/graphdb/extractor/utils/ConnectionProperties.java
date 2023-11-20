package com.sstech.graphdb.extractor.utils;

import org.springframework.beans.factory.annotation.Value;

public class ConnectionProperties {
    @Value("${grpc.loader.transformer.port:#{null}}")
    public static Integer GRAPH_TRANSFORMER_GRPC_PORT = 8001;
}
