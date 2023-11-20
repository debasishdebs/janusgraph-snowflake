package com.sstech.graphdb.extractor.server;

import org.springframework.beans.factory.DisposableBean;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.data.jpa.JpaRepositoriesAutoConfiguration;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

import java.io.File;
//160281_sstech_2439_6424350738525
// 160285_sstech_8139_149005889893
// TODO
// Optimize the way we write multiple updates to case table in beginning of case. Should reduce 1-2 min
// Optimize loading of nodes for the case added by making use of stored procedure once data is loaded. (remove toPandas). Should reduce 4-5min
// Optimize the number of calls we do to graph core to further reduce execution time by 1-2min
// Try to increase heap size, and other possibilities of new data structures to increase the size of records we read from SF without going above 4gb heap size (max 8 in VM)
// Try to make docker work, setup new azure vm and run as compose from there. 16 core 32/64 gb ram.
// Develop fallback method to check case existence using nodes column in addition to query column.
// We should have credential file only in graph_core. Based on request we should return the credentials else its difficult to maintain
// Write a cron job which will call our API every 1 hour with startTime as curr time -- 1hr and endTime as curr time for near real time data export.
// Add support for 'all' as input query so that it can be used in real time stream
// Add more and more generic valuesToSkip to reduce data explosion based on business understanding.
// 160289_sstech_8899_757297039032 [all & FLTER MIXED], 160290_sstech_113_31103491783142 [ALL Pure]
//@SpringBootApplication
@SpringBootApplication(scanBasePackages = { "com.elysum.springboot","com.sstech",},exclude = JpaRepositoriesAutoConfiguration.class)
public class ExtractorSpringServer implements DisposableBean, CommandLineRunner {

    public static void main(String[] args) {
        SpringApplication.run(ExtractorSpringServer.class, args);
    }

    @Override
    public void run(String... args) {
        String pidFile = System.getProperty("pidfile");
        if (pidFile != null) {
            new File(pidFile).deleteOnExit();
        }
    }

    @Override
    public void destroy() {
    }
}
