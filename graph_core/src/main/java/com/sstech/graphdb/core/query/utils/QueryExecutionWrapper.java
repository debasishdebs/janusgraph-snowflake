package com.sstech.graphdb.core.query.utils;

import com.sstech.graphdb.core.query.QueryExecutor;
import com.sstech.graphdb.grpc.ByteCode;
import com.sstech.graphdb.grpc.GenericStructure;
import com.sstech.graphdb.grpc.QueryResponse;
import com.sstech.graphdb.grpc.StructureValue;
import com.sun.org.apache.xpath.internal.operations.Bool;

import javax.xml.transform.Result;
import java.sql.Array;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;

public class QueryExecutionWrapper {
    ByteCode query;
    ArrayList<ResultSet> results;
    Boolean queryStatus = false;

    public QueryExecutionWrapper(ByteCode query) {
        this.query = query;
    }

    public void execute() {
        QueryExecutor executor = new QueryExecutor(query);
        try {
            results = executor.execute();
            queryStatus = true;
        } catch (Exception e) {
            e.printStackTrace();
            queryStatus = false;
        }
    }

    public ArrayList<QueryResponse> convert() {
        ArrayList<HashMap<String, Object>> results = new ArrayList<>();

        try {
            for (ResultSet result : this.results) {
                ArrayList<HashMap<String, Object>> resultPart = new ArrayList<>();

                ResultSetMetaData md = result.getMetaData();
                int columnCount = md.getColumnCount();

                while (result.next()) {
                    HashMap<String, Object> row = new HashMap<>(columnCount);
                    for (int i = 1; i <= columnCount; ++i) {
//                        System.out.println("Column is " + md.getColumnName(i));
                        row.put(md.getColumnName(i), result.getObject(i));
                    }
                    resultPart.add(row);
                }
                results.addAll(resultPart);
            }
        } catch (SQLException e) {
            e.printStackTrace();
            results = null;
        }

        ArrayList<QueryResponse> responses = new ArrayList<>();

        if (results == null) {
            QueryResponse errorResponse = QueryResponse.newBuilder().setMapFormat(
                    GenericStructure.newBuilder().putFields(
                            "error", StructureValue.newBuilder().setStringValue("Error in executing query check console").build()
                            )
            ).build();

            responses.add(errorResponse);
            return responses;
        }
        for (HashMap<String, Object> result : results) {
            QueryResponse row = QueryResponse.newBuilder().setMapFormat(
                    GenericStructure.newBuilder().putAllFields(hashMapToStructuredValue(result)).build()
            ).build();
            responses.add(row);
        }

        return responses;
    }

    private HashMap<String, StructureValue> hashMapToStructuredValue(HashMap<String, Object> obj) {
        HashMap<String, StructureValue> returnObj = new HashMap<>();

        obj.forEach( (key, value) -> {
            if (value instanceof String)
                returnObj.put(key, StructureValue.newBuilder().setStringValue((String) value).build());

            if (value instanceof Double)
                returnObj.put(key, StructureValue.newBuilder().setNumberValue((Double) value).build());

            if (value instanceof Boolean)
                returnObj.put(key, StructureValue.newBuilder().setBoolValue((Boolean) value).build());

            if (value instanceof Integer)
                returnObj.put(key, StructureValue.newBuilder().setIntValue((Integer) value).build());

            if (value instanceof Byte)
                returnObj.put(key, StructureValue.newBuilder().setNumberValue((Byte) value).build());

            if (value instanceof HashMap || value instanceof Array)
                throw new IllegalArgumentException("Currently no support added for HashMap and List type in response cell");

//            System.out.println(key);
//            System.out.println(value.toString() + value.getClass());
//            System.out.println("====");
        });

        return returnObj;
    }
}
