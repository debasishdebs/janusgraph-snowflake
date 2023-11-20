//package com.sstech.graphdb.extractor.server;
//
//import com.sstech.graphdb.extractor.bean.DummyMessageBean;
//import com.sstech.graphdb.extractor.client.TransformerGrpcClient;
//import com.sstech.graphdb.extractor.client.CoreGrpcClient;
//import com.sstech.graphdb.extractor.client.LoaderGrpcClient;
//import com.sstech.graphdb.grpc.DummyMessageStatus;
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.messaging.handler.annotation.MessageMapping;
//import org.springframework.stereotype.Controller;
//import reactor.core.publisher.Mono;
//
//
//@Controller
//public class ExtractorSpringController {
//
//    @Autowired
//    private TransformerGrpcClient transformerGrpcClient;
//    @Autowired
//    private CoreGrpcClient coreGrpcClient;
//    @Autowired
//    private LoaderGrpcClient loaderGrpcClient;
//
//    @MessageMapping("/requestresponse")
//    public Mono<String> requestResponse(String request) {
//        System.out.println("I'm inside responder in GraphExtractor for requestresponse");
//        return Mono.just(request + " Is there");
//    }
//
//    @MessageMapping("/dummyMono")
//    public Mono<DummyMessageBean> requestDummyMono(String request) throws IllegalAccessException {
//        System.out.println("I'm inside responder in GraphExtractor for dummyMono");
//
//        Object service = transformerGrpcClient.connect();
//        if (service == null)
//            throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
//                    "HOST/PORT isn't defined in application.properties in extractor");
//
//        DummyMessageStatus msg;
//        msg = transformerGrpcClient.pingGraphTransformerWithDummySignalMono(request + " Is there");
//
//        System.out.println(msg.getMessage() + " & " + msg.getSource() + " & " + msg.getStatus());
//        System.out.println("Returning back with result as " + msg.toString());
//
//        return Mono.just(this.convertToBeanFromStatus(msg));
//    }
//
//    private DummyMessageBean convertToBeanFromStatus(DummyMessageStatus msg) {
//        DummyMessageBean m = new DummyMessageBean();
//        m.setMessage(msg.getMessage()).
//                setSource(msg.getSource()).
//                setStatus(msg.getStatus()).
//                setCurrent(msg.getCurrentList().toArray(new String[0])).addCurrent("Extractor");
//        return m;
//    }
//
//}
