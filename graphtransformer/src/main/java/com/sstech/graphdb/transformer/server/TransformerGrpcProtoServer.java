package com.sstech.graphdb.transformer.server;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;

@SpringBootApplication
public class TransformerGrpcProtoServer extends SpringBootServletInitializer {

    public static void main(String[] args) {

        new SpringApplicationBuilder(TransformerGrpcProtoServer.class)
                .web(WebApplicationType.NONE) // .REACTIVE, .SERVLET
                .run(args);

//        SpringApplication.run(TransformerGrpcProtoServer.class, args);

//		Server server = ServerBuilder
//				.forPort(8080)
//				.addService(new HelloServiceImpl()).build();
//
//		server.start();
//		server.awaitTermination();
    }

}
