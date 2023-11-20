package com.sstech.graphdb.core.server;

import com.sstech.graphdb.core.client.AppGrpcClient;
import com.sstech.graphdb.core.client.ExtractorGrpcClient;
import com.sstech.graphdb.core.client.LoaderGrpcClient;
import com.sstech.graphdb.core.client.TransformerGrpcClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Configuration
public class CoreSpringConfiguration {
    @Bean
    TransformerGrpcClient createConnectionToGraphTransformer() {
        return new TransformerGrpcClient();
    }

    @Bean
    LoaderGrpcClient createConnectionToGraphLoader() {
        return new LoaderGrpcClient();
    }

    @Bean
    AppGrpcClient createConnectionToGraphApp() {
        return new AppGrpcClient();
    }

    @Bean
    ExtractorGrpcClient createConnectionToGraphExtractor() {
        return new ExtractorGrpcClient();
    }
}
