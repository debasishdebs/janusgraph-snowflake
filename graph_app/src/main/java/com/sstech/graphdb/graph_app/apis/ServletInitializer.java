package com.sstech.graphdb.graph_app.apis;

import com.sstech.graphdb.graph_app.server.GraphAppSpringServer;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;

public class ServletInitializer extends SpringBootServletInitializer {

	@Override
	protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
		return application.sources(GraphAppSpringServer.class);
	}

}
