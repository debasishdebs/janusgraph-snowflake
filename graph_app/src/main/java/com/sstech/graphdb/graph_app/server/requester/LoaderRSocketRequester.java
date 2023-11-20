//package com.sstech.graphdb.graph_app.server.requester;
//
//import org.springframework.beans.factory.annotation.Value;
//import org.springframework.messaging.rsocket.RSocketRequester;
//import org.springframework.messaging.rsocket.RSocketStrategies;
//
//public class LoaderRSocketRequester {
//
//    @Value("${rsocket.extractor.server.host:#{null}}")
//    private String host;
//    @Value("${rsocket.extractor.server.port:#{null}}")
//    private Integer port;
//
//    private RSocketStrategies strategies;
//
//
//    public LoaderRSocketRequester() {
//    }
//
//    public LoaderRSocketRequester withStrategies(RSocketStrategies stratergies) {
//        this.strategies = stratergies;
//        return this;
//    }
//
//    public RSocketRequester get() {
//        if (host == null && port == null)
//            return null;
//
//        System.out.println(String.format("Connecting to rSocket Server (Loader) with Host %s and Port %s", host, port));
//
//        return RSocketRequester.builder()
//                .rsocketStrategies(strategies)
//                .connectTcp(host, port)
//                .block();
//    }
//}
