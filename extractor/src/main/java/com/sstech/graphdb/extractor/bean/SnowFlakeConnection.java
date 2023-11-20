package com.sstech.graphdb.extractor.bean;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class SnowFlakeConnection {
    Connection snowflakeConnection;
    Statement snowflakeStatement;
    ResultSet result;

    public SnowFlakeConnection(Connection jdbcConnection) throws SQLException {
        this.snowflakeConnection = jdbcConnection;
        this.snowflakeStatement = jdbcConnection.createStatement();
    }

    public SnowFlakeConnection executeQuery(String query) throws SQLException {
        result = snowflakeStatement.executeQuery(query);
        return this;
    }

    public List<HashMap<String, Object>> getResults() throws SQLException {
        List<HashMap<String, Object>> results = new ArrayList<>();

        ResultSetMetaData resultSetMetaData = result.getMetaData();
        int columnCount = resultSetMetaData.getColumnCount();
        List<String> columns = new ArrayList<>(columnCount);

        for (int counter = 1; counter <= columnCount; counter++) {
            columns.add(resultSetMetaData.getColumnLabel(counter));
        }

        while (result.next()) {
            HashMap<String, Object> row = new HashMap<>(columnCount);
            for (String column : columns) {
                row.put(column, result.getString(column));
            }
            results.add(row);
        }
        return results;
    }

    public void close() {
        try{
            if (!snowflakeStatement.isClosed())
                snowflakeStatement.close();
            if (!snowflakeConnection.isClosed())
                snowflakeConnection.close();
        } catch (SQLException e) {
            System.out.println("ERROR: Error closing out connection");
        }
    }
}
