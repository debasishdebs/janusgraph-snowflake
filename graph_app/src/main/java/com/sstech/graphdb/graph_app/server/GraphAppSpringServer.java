package com.sstech.graphdb.graph_app.server;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

@SpringBootApplication
@EnableWebMvc
public class GraphAppSpringServer extends SpringBootServletInitializer {
	// mvn clean install dependency:copy-dependencies package
	// ./mvnw spring-boot:run
	// ./mvnw clean compile package

	public static void main(String[] args) {
		SpringApplication.run(GraphAppSpringServer.class, args);
	}


	@Override
	protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
		return application.sources(GraphAppSpringServer.class);
	}

}
