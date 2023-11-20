package com.sstech.graphdb.extractor.bean;

import com.sstech.graphdb.extractor.client.CoreGrpcClient;
//import com.sstech.graphdb.extractor.server.SnowflakeConfig;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.grpc.Credentials;
import org.apache.commons.dbcp2.BasicDataSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.PropertySource;
import org.springframework.core.env.Environment;

import java.io.IOException;
import java.io.InputStream;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Properties;

//@PropertySource({ "classpath:credentials.properties" })
public class SnowFlakeConnectionPool {

    private static BasicDataSource ds = new BasicDataSource();

//    static String resourceName = "credentials.properties"; // could also be a constant
//    static ClassLoader loader = Thread.currentThread().getContextClassLoader();

    static int MINIMUM_POOL_SIZE = 10;
    static int MAXIMUM_POOL_SIZE = 20;
    static int MAXIMUM_PREPARED_STATEMENT = 30;
    static int IDLE_TIMEOUT_EVICTION = 10;

    static {
        Credentials credentials = ConstantsAndUtils.getSnowflakeCredentials();

        ds.setDriverClassName("com.snowflake.client.jdbc.SnowflakeDriver");
        ds.setUrl(credentials.getUrl());
        ds.setUsername(credentials.getUser());
        ds.setPassword(credentials.getPassword());

        Properties connectionProperties = new Properties();
        connectionProperties.put("url", credentials.getUrl());
        connectionProperties.put("user", credentials.getUser());
        connectionProperties.put("password", credentials.getPassword());
        connectionProperties.put("account", credentials.getAccount());
        connectionProperties.put("db", credentials.getDatabase());
        connectionProperties.put("schema", credentials.getSchema());
        connectionProperties.put("role", credentials.getRole());
        connectionProperties.put("warehouse", credentials.getWarehouse());

        ArrayList<String> propertiesStrings = new ArrayList<>();
        for (Object o : connectionProperties.keySet()) {
            String key = (String) o;
            String value = (String) connectionProperties.get(key);
            String keyValue = String.format("%s=%s", key, value);
            propertiesStrings.add(keyValue);
        }
        String properties = String.join(";", propertiesStrings);
        System.out.printf("Additional connection parameters to snowflake db is %s%n", properties);

        ds.setConnectionProperties(properties);
        ds.setMinIdle(MINIMUM_POOL_SIZE);
        ds.setMaxIdle(MAXIMUM_POOL_SIZE);
        ds.setMaxOpenPreparedStatements(MAXIMUM_PREPARED_STATEMENT);
        ds.setRemoveAbandonedTimeout(IDLE_TIMEOUT_EVICTION);
    }
//
//    static {
//        Properties props = new Properties();
//        try(InputStream resourceStream = loader.getResourceAsStream(resourceName)) {
//            props.load(resourceStream);
//        } catch (IOException e) {
//            e.printStackTrace();
//        }
//        System.out.println(props);
//
//        ds.setDriverClassName("com.snowflake.client.jdbc.SnowflakeDriver");
//        ds.setUrl(props.getProperty("app.datasource.url"));
//        ds.setUsername(props.getProperty("app.datasource.user"));
//        ds.setPassword(props.getProperty("app.datasource.password"));
//
//        Properties connectionProperties = new Properties();
//        connectionProperties.put("url", props.getProperty("app.datasource.url"));
//        connectionProperties.put("user", props.getProperty("app.datasource.user"));
//        connectionProperties.put("password", props.getProperty("app.datasource.password"));
//        connectionProperties.put("account", props.getProperty("app.datasource.account"));
//        connectionProperties.put("db", props.getProperty("app.datasource.db"));
//        connectionProperties.put("schema", props.getProperty("app.datasource.schema"));
//        connectionProperties.put("role", props.getProperty("app.datasource.role"));
//        connectionProperties.put("warehouse", props.getProperty("app.datasource.warehouse"));
//
//        ArrayList<String> propertiesStrings = new ArrayList<>();
//        for (Object o : connectionProperties.keySet()) {
//            String key = (String) o;
//            String value = (String) connectionProperties.get(key);
//            String keyValue = String.format("%s=%s", key, value);
//            propertiesStrings.add(keyValue);
//        }
//        String properties = String.join(";", propertiesStrings);
//        System.out.printf("Additional connection parameters to snowflake db is %s%n", properties);
//
//        ds.setConnectionProperties(properties);
//
//        ds.setMinIdle(10);
//        ds.setMaxIdle(20);
//        ds.setMaxOpenPreparedStatements(30);
//        ds.setRemoveAbandonedTimeout(10);
//    }

    public static SnowFlakeConnection getConnection() throws SQLException {
        return new SnowFlakeConnection(ds.getConnection());
    }

    private SnowFlakeConnectionPool(){ }
}
