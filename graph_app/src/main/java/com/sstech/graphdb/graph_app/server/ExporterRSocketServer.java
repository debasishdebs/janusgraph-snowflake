//package com.sstech.graphdb.graphextractor.server;
//
//import com.sstech.graphdb.graphextractor.beans.CaseBean;
//import org.apache.logging.slf4j.SLF4JLogger;
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;
//import org.slf4j.Marker;
//import org.springframework.messaging.Message;
//import org.springframework.messaging.handler.annotation.MessageMapping;
//import org.springframework.messaging.handler.annotation.Payload;
//import org.springframework.messaging.rsocket.RSocketRequester;
//import lombok.extern.slf4j.Slf4j;
//import org.springframework.stereotype.Controller;
//import org.springframework.messaging.rsocket.annotation.ConnectMapping;
//import reactor.core.publisher.Mono;
//
//import javax.annotation.PreDestroy;
//import java.util.ArrayList;
//import java.util.List;
//
//@Slf4j
//@Controller
//public class ExporterRSocketServer {
//    private final List<RSocketRequester> CLIENTS = new ArrayList<>();
//    private Logger log = LoggerFactory.getLogger(this.getClass());
//
//    @PreDestroy
//    void shutdown() {
//        log.info("Detaching all remaining clients...");
//        CLIENTS.stream().forEach(requester -> requester.rsocket().dispose());
//        log.info("Shutting down.");
//    }
//
//    @ConnectMapping("shell-client")
//    void connectShellClientAndAskForTelemetry(RSocketRequester requester, @Payload String client) {
//
//        requester.rsocket()
//                .onClose()
//                .doFirst(() -> {
//                    // Add all new clients to a client list
//                    log.info("Client: {} CONNECTED.", client);
//                    CLIENTS.add(requester);
//                })
//                .doOnError(error -> {
//                    // Warn when channels are closed by clients
//                    log.warn("Channel to client {} CLOSED", client);
//                })
//                .doFinally(consumer -> {
//                    // Remove disconnected clients from the client list
//                    CLIENTS.remove(requester);
//                    log.info("Client {} DISCONNECTED", client);
//                })
//                .subscribe();
//
//        // Callback to client, confirming connection
//        requester.route("client-status")
//                .data("OPEN")
//                .retrieveFlux(String.class)
//                .doOnNext(s -> log.info("Client: {} Free Memory: {}.", client, s))
//                .subscribe();
//    }
//
//    /**
//     * This @MessageMapping is intended to be used "fire --> forget" style. with route name export-case
//     * When a new CommandRequest is received, nothing is returned (void)
//     *
//     * @param request
//     * @return
//     */
//    @MessageMapping("export-case")
//    public Mono<CaseBean> exportCaseAndForget(final CaseBean request) {
//        log.info("Received fire-and-forget request for starting export of case: {}", request);
//        System.out.println("Received fire-and-forget request for starting export of case: {}" + request.toString());
//        return Mono.just(new CaseBean(request.getCaseInformation() + " Modified"));
//    }
//}
