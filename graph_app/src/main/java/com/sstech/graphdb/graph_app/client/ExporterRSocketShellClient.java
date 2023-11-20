//package com.sstech.graphdb.graphextractor.client;
//
//import com.sstech.graphdb.graphextractor.beans.CaseMetadataBean;
//import io.rsocket.SocketAcceptor;
//import lombok.extern.slf4j.Slf4j;
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.messaging.handler.annotation.MessageMapping;
//import org.springframework.messaging.rsocket.RSocketRequester;
//import org.springframework.messaging.rsocket.RSocketStrategies;
//import org.springframework.messaging.rsocket.annotation.support.RSocketMessageHandler;
//import org.springframework.shell.standard.ShellComponent;
//import org.springframework.shell.standard.ShellMethod;
//import reactor.core.Disposable;
//import reactor.core.publisher.Flux;
//
//import javax.annotation.PreDestroy;
//import java.time.Duration;
//import java.util.UUID;
//
//@Slf4j
//@ShellComponent
//public class ExporterRSocketClient {
//
//    private final RSocketRequester rsocketRequester;
//    private static Disposable disposable;
//    private Logger log = LoggerFactory.getLogger(this.getClass());
//
//    @Autowired
//    public ExporterRSocketClient(RSocketRequester.Builder rsocketRequesterBuilder, RSocketStrategies strategies) {
//        String client = UUID.randomUUID().toString();
//        log.info("Connecting using client ID: {}", client);
//
//        SocketAcceptor responder = RSocketMessageHandler.responder(strategies, new ClientHandler());
//
//        this.rsocketRequester = rsocketRequesterBuilder
//                .setupRoute("shell-client")
//                .setupData(client)
//                .rsocketStrategies(strategies)
//                .rsocketConnector(connector -> connector.acceptor(responder))
//                .connectTcp("localhost", 7000)
//                .block();
//
//        this.rsocketRequester.rsocket()
//                .onClose()
//                .doOnError(error -> log.warn("Connection CLOSED"))
//                .doFinally(consumer -> log.info("Client DISCONNECTED"))
//                .subscribe();
//    }
//
//    @PreDestroy
//    void shutdown() {
//        rsocketRequester.rsocket().dispose();
//    }
//
//    @ShellMethod("Update CaseStatus")
//    public void updateCaseStatus(CaseMetadataBean status) throws InterruptedException {
//        log.info("\nRequest-Response. Sending one request. Expect no response (check server console log)...");
//        this.rsocketRequester
//                .route("update-case-status")
//                .data(status)
//                .retrieveMono(CaseMetadataBean.class)
//                .block();
//    }
//
//    @ShellMethod("Transform Case")
//    public void transformCase(CaseMetadataBean status) throws InterruptedException {
//        log.info("\nFire-Forget. Sending one request. Expect no response (check server console log)...");
//        this.rsocketRequester
//                .route("transform-case-to-graph")
//                .data(status)
//                .retrieveMono(CaseMetadataBean.class)
//                .block();
//    }
//}
//
//@Slf4j
//class ClientHandler {
//    @MessageMapping("client-status")
//    public Flux<String> statusUpdate(String status) {
////        log.info("Connection {}", status);
//        return Flux.interval(Duration.ofSeconds(5)).map(index -> String.valueOf(Runtime.getRuntime().freeMemory()));
//    }
//}