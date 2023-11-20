package com.sstech.graphdb.extractor.server;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.support.PropertySourcesPlaceholderConfigurer;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import javax.sql.DataSource;
import java.util.Properties;

@Configuration
//@PropertySource({ "classpath:application.properties" })
@PropertySource({ "classpath:credentials.properties" })
//@ConfigurationProperties(prefix="app.datasource")
public class SnowflakeConfig {
	@Autowired
	private Environment env;

    @Bean
    public static PropertySourcesPlaceholderConfigurer propertyConfigurer() {
        return new PropertySourcesPlaceholderConfigurer();
    }

	@Primary
	@Bean
	public DataSource snowflakeDataSource() {
		DriverManagerDataSource dataSource = new DriverManagerDataSource();

		dataSource.setDriverClassName("com.snowflake.client.jdbc.SnowflakeDriver");
        dataSource.setUrl(env.getProperty("app.datasource.url")); //ik55883.east-us-2.azure
        dataSource.setUsername(env.getProperty("app.datasource.user"));
        dataSource.setPassword(env.getProperty("app.datasource.password"));
        Properties connectionProperties = new Properties();
        connectionProperties.put("url", env.getProperty("app.datasource.url"));
        connectionProperties.put("user", env.getProperty("app.datasource.user"));
        connectionProperties.put("password", env.getProperty("app.datasource.password"));
        connectionProperties.put("account", env.getProperty("app.datasource.account"));
        connectionProperties.put("db", env.getProperty("app.datasource.db"));
        connectionProperties.put("schema", env.getProperty("app.datasource.schema"));
        connectionProperties.put("role", env.getProperty("app.datasource.role"));
        connectionProperties.put("warehouse", env.getProperty("app.datasource.warehouse"));
        dataSource.setConnectionProperties(connectionProperties);
		return dataSource;
	}

	public String getDataSourceURL() {
	    return env.getProperty("app.datasource.url");
    }

    public String getUser() {
	    return env.getProperty("app.datasource.user");
    }

    public String getPassword() {
	    return env.getProperty("app.datasource.password");
    }

    public String getAccount() {
	    return env.getProperty("app.datasource.account");
    }

    public String getSnowFlakeDB() {
        return env.getProperty("app.datasource.db");
    }

    public String getSnowFlakeSchema() {
	    return env.getProperty("app.datasource.schema");
    }

    public String getSnowFlakeRole() {
	    return env.getProperty("app.datasource.role");
    }

    public String getSnowFlakeWarehouse() {
	    return env.getProperty("app.datasource.warehouse");
    }

    public String getDriverClassName() {
        System.out.println("Going to return driver");
	    return "com.snowflake.client.jdbc.SnowflakeDriver";
    }

}
