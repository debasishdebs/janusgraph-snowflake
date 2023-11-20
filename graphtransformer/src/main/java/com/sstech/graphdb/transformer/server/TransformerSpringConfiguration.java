package com.sstech.graphdb.transformer.server;

import com.sstech.graphdb.transformer.client.CoreGrpcClient;
import com.sstech.graphdb.transformer.client.LoaderGrpcClient;
import com.sstech.graphdb.transformer.client.TransformerGrpcClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Configuration
public class TransformerSpringConfiguration {
    @Bean
    TransformerGrpcClient createConnectionToGraphTransformer() {
        return new TransformerGrpcClient();
    }

    @Bean
    CoreGrpcClient createConnectionToGraphCore() {
        return new CoreGrpcClient();
    }

    @Bean
    LoaderGrpcClient createConnectionToGraphLoader() {
        return new LoaderGrpcClient();
    }
}
