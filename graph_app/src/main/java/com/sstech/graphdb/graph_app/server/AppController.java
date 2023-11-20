package com.sstech.graphdb.graph_app.server;

import com.google.protobuf.Empty;
import com.sstech.graphdb.graph_app.apis.Greetings;
import com.sstech.graphdb.graph_app.beans.*;
import com.sstech.graphdb.graph_app.client.CoreGrpcClient;
import com.sstech.graphdb.graph_app.client.ExtractorGrpcClient;
import com.sstech.graphdb.graph_app.client.LoaderGrpcClient;
import com.sstech.graphdb.graph_app.client.TransformerGrpcClient;
import com.sstech.graphdb.grpc.*;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.net.ConnectException;
import java.util.Calendar;
import java.util.Date;
import java.util.concurrent.atomic.AtomicLong;

@RestController
public class AppController {
    private static final String template = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();

//    @Autowired
//    private ExtractorRSocketRequester extractorRSocketRequester;

    @Autowired
    private LoaderGrpcClient loaderGrpcClient;
    @Autowired
    private CoreGrpcClient coreGrpcClient;
    @Autowired
    private TransformerGrpcClient transformerGrpcClient;
    @Autowired
    private ExtractorGrpcClient extractorGrpcClient;

    @GetMapping("/requestresponse")
    public Mono<String> requestResponse(@RequestParam(value = "name", defaultValue = "World") String request) throws IllegalAccessException {
        System.out.println("I'm inside requestResponse controller");

//        RSocketRequester requester = extractorRSocketRequester.get();
//        if (requester == null)
//            throw new IllegalAccessException("HOST/PORT for rsocket extractor isn't defined. Please see application.properties");
//
//        return requester
//                .route("/requestresponse").data(request).retrieveMono(String.class);

        return Mono.just("Hello " + request);
    }

    @GetMapping("/dummyStream")
    public Flux dummyStream(@RequestParam(value = "name", defaultValue = "World") String request) throws IllegalAccessException {
        System.out.println("I'm inside requestResponse controller");

//        ArrayList<String> response = new ArrayList<>();

//        rSocket.route("/dummyStream").data(request).retrieveFlux(DummyMessageBean.class).doOnNext(
//                resp -> {
//                    System.out.println("Retrieved response " + resp);
//                    response.add(resp);
//                }
//        );

//        RSocketRequester requester = extractorRSocketRequester.get();
//        if (requester == null)
//            throw new IllegalAccessException("HOST/PORT for rsocket extractor isn't defined. Please see application.properties");
//
//        Flux response = requester
//                .route("/dummyStream").data(request).retrieveFlux(DummyMessageBean.class);
//
//        System.out.println("Finally back inside AppController for dummyStream");

        throw new NotImplementedException();

//        return response;
    }

    @GetMapping("/dummyMono")
    public Mono dummyMono(@RequestParam(value = "name", defaultValue = "World") String request) throws IllegalAccessException {
        System.out.println("I'm inside requestResponse controller");

//        RSocketRequester requester = extractorRSocketRequester.get();
//        if (requester == null)
//            throw new IllegalAccessException("HOST/PORT for rsocket extractor isn't defined. Please see application.properties");
//
//        Mono resp = requester
//                .route("/dummyMono").data(request).retrieveMono(DummyMessageBean.class);
//
//        DummyMessageBean response = convertMonoToDummyMessageBean(resp).addCurrent("GraphCore");
//
//        System.out.println("Finally back inside AppController for dummyMono");
//        return Mono.just(response);

        Object service = extractorGrpcClient.connect();
        if (service == null) {
            try {
                throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
                        "HOST/PORT isn't defined in application.properties in extractor");
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }

        DummyMessageStatus resp =
                extractorGrpcClient.pingGraphExtractorWithDummySignalMono(request + " is inside AppController");

        DummyMessageBean response = convertStatusToDummyMessageBean(resp).addCurrent("GraphApp");

        System.out.println("Finally back inside AppController for dummyMono");
        return Mono.just(response);
    }

    @GetMapping("/greetings")
    public Greetings greetings(@RequestParam(value = "name", defaultValue = "World") String name) {
        System.out.println("I'm inside greetings controller");
        return new Greetings(counter.incrementAndGet(), String.format(template, name));
    }

    @RequestMapping(value = "/startCaseExport", method = RequestMethod.POST)
    public ResponseEntity<Object> startCaseExport(@RequestBody CaseExportPayloadBean exportPayloadBean) throws ConnectException {
        System.out.println("Starting to call GraphExporter service from GraphApp to GraphExtractor");

        Object service = extractorGrpcClient.connect();
        if (service == null) {
            try {
                throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
                        "HOST/PORT isn't defined in application.properties in extractor");
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }

        extractorGrpcClient.startCaseExport(exportPayloadBean);
        return new ResponseEntity<>("Successfully started export of case", HttpStatus.ACCEPTED);
    }

    @RequestMapping(value = "/products", method = RequestMethod.POST)
    public ResponseEntity<Object> createProduct(@RequestBody ProductBean product) {
        return new ResponseEntity<>("Product is created successfully", HttpStatus.CREATED);
    }

    private DummyMessageBean convertMonoToDummyMessageBean(Mono bean) {
        DummyMessageBean obj = (DummyMessageBean) bean.block();
        return obj;
    }

    private DummyMessageBean convertStatusToDummyMessageBean(DummyMessageStatus msg) {
        DummyMessageBean obj = new DummyMessageBean();
        obj.setMessage(msg.getMessage());
        obj.setSource(msg.getSource());
        obj.setStatus(msg.getStatus());
        msg.getCurrentList().forEach(obj::setCurrent);
        return obj;
    }
}
