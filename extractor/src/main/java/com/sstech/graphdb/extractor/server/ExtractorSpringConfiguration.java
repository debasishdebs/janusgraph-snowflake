package com.sstech.graphdb.extractor.server;

import com.sstech.graphdb.extractor.client.AppGrpcClient;
import com.sstech.graphdb.extractor.client.CoreGrpcClient;
import com.sstech.graphdb.extractor.client.LoaderGrpcClient;
import com.sstech.graphdb.extractor.client.TransformerGrpcClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Configuration
public class ExtractorSpringConfiguration {
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
    CoreGrpcClient createConnectionToGraphCore() {
        return new CoreGrpcClient();
    }

}