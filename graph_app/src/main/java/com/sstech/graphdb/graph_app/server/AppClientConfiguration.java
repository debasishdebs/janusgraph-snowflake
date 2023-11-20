package com.sstech.graphdb.graph_app.server;

import com.sstech.graphdb.graph_app.client.CoreGrpcClient;
import com.sstech.graphdb.graph_app.client.ExtractorGrpcClient;
import com.sstech.graphdb.graph_app.client.LoaderGrpcClient;
import com.sstech.graphdb.graph_app.client.TransformerGrpcClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Configuration
public class AppClientConfiguration {
//    public RSocket rSocket(@Value("${spring.rsocket.server.port}") Integer serverPort)
//    @Bean
//    public RSocket rSocket() {
//        return RSocketFactory.connect()
//                .mimeType(MimeTypeUtils.APPLICATION_JSON_VALUE, MimeTypeUtils.APPLICATION_JSON_VALUE)
//                .frameDecoder(PayloadDecoder.ZERO_COPY).transport(TcpClientTransport.create("localhost", 7001))
//                .start().block();
//
//        return RSocketFactory.connect()
//                .mimeType(MetadataExtractor.ROUTING.toString(), MimeTypeUtils.APPLICATION_JSON_VALUE)
//                .frameDecoder(PayloadDecoder.ZERO_COPY)
//                .transport(TcpClientTransport.create(new InetSocketAddress(7500)))
//                .start()
//                .block();
//    }

//    @Bean
//    RSocketRequester rSocketRequester(RSocketStrategies rSocketStrategies) {
////        return RSocketRequester.wrap(rSocket, MimeTypeUtils.APPLICATION_JSON, MimeTypeUtils.APPLICATION_JSON,
////                rSocketStrategies);
//        return RSocketRequester.builder()
//                .rsocketStrategies(rSocketStrategies)
//                .connectTcp("localhost", 7001)
//                .block();
//    }

//    @Bean
//    TransformerRSocketRequester createConnectionToGraphTransformer(RSocketStrategies rSocketStrategies) {
//        return new TransformerRSocketRequester().withStrategies(rSocketStrategies);
//    }
//
//    @Bean
//    ExtractorRSocketRequester createConnectionToGraphExtractor(RSocketStrategies rSocketStrategies) {
//        return new ExtractorRSocketRequester().withStrategies(rSocketStrategies);
//    }
//
//    @Bean
//    LoaderRSocketRequester createConnectionToGraphLoader(RSocketStrategies rSocketStrategies) {
//        return new LoaderRSocketRequester().withStrategies(rSocketStrategies);
//    }

    @Bean
    TransformerGrpcClient createConnectionToGraphTransformer() {
        return new TransformerGrpcClient();
    }

    @Bean
    LoaderGrpcClient createConnectionToGraphLoader() {
        return new LoaderGrpcClient();
    }

    @Bean
    CoreGrpcClient createConnectionToGraphApp() {
        return new CoreGrpcClient();
    }

    @Bean
    ExtractorGrpcClient createConnectionToGraphExtractor() {
        return new ExtractorGrpcClient();
    }
}
