//package com.sstech.graphdb.transformer.server;
//
//
//import com.sstech.graphdb.transformer.grpc.*;
//import com.sstech.graphdb.transformer.grpc.ServicesToGraphTransformer;
//import com.sstech.graphdb.transformer.utils.ConnectionProperties;
//import io.netty.buffer.ByteBuf;
//import io.rsocket.RSocketFactory;
//import io.rsocket.SocketAcceptor;
//import io.rsocket.rpc.rsocket.RequestHandlingRSocket;
//import io.rsocket.transport.netty.server.TcpServerTransport;
//import lombok.extern.slf4j.Slf4j;
//import org.slf4j.Logger;
//import org.springframework.beans.factory.annotation.Autowired;
//import reactor.core.publisher.Flux;
//import reactor.core.publisher.Mono;
//
//import java.time.Duration;
//import java.util.ArrayList;
//import java.util.Optional;
//
//
//public class TransformerRSocketProtoServer {
//    public static void main(String[] args) throws InterruptedException {
//        ServicesToGraphTransformerServer extractorReceiver =
//                new ServicesToGraphTransformerServer(new ServicesToTransformer(), Optional.empty(), Optional.empty());
////        BlockingServicesToGraphTransformerServer blockingServer =
////                new BlockingServicesToGraphTransformerServer(new BlockingServicesToTransformer(), Optional.empty(), Optional.empty());
//
//        RSocketFactory
//                .receive()
//                .acceptor((setup, sendingSocket) -> Mono.just(
//                        new RequestHandlingRSocket(extractorReceiver)
//                ))
//                .transport(TcpServerTransport.create(ConnectionProperties.GRPC_SERVER_PORT))
//                .start()
//                .block();
//
////        RSocketFactory.receive().
////                acceptor(TransformerRSocketProtoServer.socketAcceptor(extractorReceiver, blockingServer))
////                .transport(TcpServerTransport.create(ConnectionProperties.GRPC_SERVER_PORT))
////                .start()
////                .block();
//
//        Thread.currentThread().join();
//    }
//
//    private static SocketAcceptor socketAcceptor(ServicesToGraphTransformerServer server, BlockingServicesToGraphTransformerServer blockingServer) {
//        RequestHandlingRSocket requestHandlingRSocket = new RequestHandlingRSocket(server, blockingServer);
//
//        return ((setup, sendingSocket) -> Mono.just(requestHandlingRSocket));
//    }
//
//    private static SocketAcceptor socketAcceptor(ServicesToGraphTransformerServer server) {
//        RequestHandlingRSocket requestHandlingRSocket = new RequestHandlingRSocket(server);
//
//        return ((setup, sendingSocket) -> Mono.just(requestHandlingRSocket));
//    }
//
//    static class BlockingServicesToTransformer implements BlockingServicesToGraphTransformer {
//
//        @Override
//        public Iterable<DummyMessageStatus> checkSignalSentStream(DummyMessage message, ByteBuf metadata) {
//            System.out.println("Got signal from " + message.getSource() + " in Stream  & Blocking and message is " + message.getMessage());
//            ArrayList<DummyMessageStatus> response = new ArrayList<>();
//            for (int i = 0; i < 5 ; i++) {
//                response.add(DummyMessageStatus.newBuilder()
//                        .setMessage("ID: " + i + " MSG: " + message.getMessage())
//                        .setStatus("Returning from Transformer in loop")
//                        .setSource(this.getClass().toGenericString()).build()
//                );
//            }
//            return response;
//        }
//
//        @Override
//        public DummyMessageStatus checkSignalSentMono(DummyMessage message, ByteBuf metadata) {
//            System.out.println("Got signal from " + message.getSource() + " in Mono & Blocking and message is " + message.getMessage());
//            System.exit(-100);
//
//            DummyMessageStatus status = DummyMessageStatus.newBuilder().
//                    setMessage(message.getMessage()).
//                    setStatus("Returning from TransformerRSocketProtoServer").
//                    setSource(this.getClass().toGenericString()).
//                    build();
//
//            return status;
//        }
//    }
//
//    @Slf4j
//    static class ServicesToTransformer implements ServicesToGraphTransformer {
//
//        @Override
//        public Flux<DummyMessageStatus> checkSignalSentStream(DummyMessage message, ByteBuf metadata) {
//            System.out.println("Got signal from " + message.getSource() + " in Stream and message is " + message.getMessage());
//
//            Flux<DummyMessageStatus> response =  Flux.interval(Duration.ofMillis(100)).onBackpressureDrop()
//                    .map(s -> DummyMessageStatus.newBuilder().setMessage(s + " got message " + message.getMessage()).
//                            setStatus("Returning from TransformerRSocketProtoServer").
//                            setSource(this.getClass().toGenericString()).build());
//
//            System.out.println("Returning from transformer checkSignalSentStream");
//            return response;
//
////            return
////                    Flux.interval(Duration.ofMillis(200))
////                            .onBackpressureDrop()
//////                    .map(i -> i + " - got message - " + message.getMessage())
////                            .map(s -> DummyMessageStatus.newBuilder().setMessage(s + " got message " + message.getMessage()).
////                                    setStatus("Returning from TransformerRSocketProtoServer").
////                                    setSource(this.getClass().toGenericString()).build());
//
//        }
//
//        @Override
//        public Mono<DummyMessageStatus> checkSignalSentMono(DummyMessage message, ByteBuf metadata) {
//            System.out.println("Got signal from " + message.getSource() + " in Mono and message is " + message.getMessage());
////            log.info("Received signal in checkSignalSentMono");
////            System.exit(-1);
//
//            DummyMessageStatus status = DummyMessageStatus.newBuilder().
//                    setMessage(message.getMessage()).
//                    setStatus("Returning from TransformerRSocketProtoServer").
//                    setSource(this.getClass().toGenericString()).
//                    build();
//
//            System.out.println("Returning from transformer checkSignalSentMono with " + status);
//            return Mono.just(status);
//        }
//    }
//
//}