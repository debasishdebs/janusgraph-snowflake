package com.sstech.graphdb.extractor.process;

import com.sstech.graphdb.extractor.bean.SnowFlakeConnectionPool;
import com.sstech.graphdb.extractor.client.CoreGrpcClient;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.grpc.CaseSubmissionPayload;
import com.sstech.graphdb.grpc.EntityQuery;
import com.sstech.graphdb.grpc.EntityTypeQuery;
import com.sstech.graphdb.grpc.Time;

import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class QueryDataExtractor {
    private final CaseSubmissionPayload QUERY;
    private final String startTime;
    private final String endTime;
    private HashMap<String, List<String>> tablesToQuery;
    private Set<String> allTables;

    private CoreGrpcClient coreGrpcClient;
    private String caseId;

    private ThreadPoolExecutor executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(5);
    private final List<Future<HashMap<String, ArrayList<Map<String, Object>>>>> tasksQueue = new ArrayList<>();

    List<String> failedTables = new ArrayList<>();
    List<String> successTables = new ArrayList<>();

    private int LEVEL = 3;

    public QueryDataExtractor(CaseSubmissionPayload query) {
        this.QUERY = query;
        this.startTime = this.protoTimeToString(query.getStartDate());
        this.endTime = this.protoTimeToString(query.getEndDate());
    }

    public QueryDataExtractor addTablesToQuery(HashMap<String, List<String>> tablesToQuery) {
        this.tablesToQuery = tablesToQuery;
        return this;
    }

    public QueryDataExtractor setCaseId(String caseId) {
        this.caseId = caseId;
        return this;
    }

    public QueryDataExtractor setLevels(int levels) {
        LEVEL = levels;
        return this;
    }

    public QueryDataExtractor setNumberOfThreads(int numberOfThreads) {
        executor.shutdown();
        executor.shutdownNow();
        try {
            executor.awaitTermination(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.printf("Execution shutdown and starting new executorService with threads %d", numberOfThreads);

        executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(numberOfThreads);
        return this;
    }

    public QueryDataExtractor setTables(Set<String> tables) {
        allTables = tables;
        return this;
    }

    public QueryDataExtractor setCoreGrpcClient(CoreGrpcClient client) {
        this.coreGrpcClient = client;
        return this;
    }

    private String protoTimeToString(Time time) {
        int year = time.getYear();
        int month = time.getMonth();
        int day = time.getDay();
        int hour = time.getHour();
        int min = time.getMinutes();
        int sec = time.getSeconds();

        return String.format("%s-%s-%s %s:%s:%s", year, month, day, hour, min, sec);
    }

    private void execute() {
        Set<String> tables = this.tablesToQuery.keySet();
        Set<String> nodeLabels = this.QUERY.getQueryMap().keySet();

        for (String table : tables) {
            System.out.printf("Queuing table %s", table);

            List<String> tableCols = this.tablesToQuery.get(table);
            HashMap<String, ArrayList<String>> columnFilters = new HashMap<>();
            for (String nodeLabel : nodeLabels) {
                EntityTypeQuery q = this.QUERY.getQueryMap().get(nodeLabel);

                List<EntityQuery> queries = q.getEntityQueryList();
                ArrayList<String> filterValues = new ArrayList<>();
                for (EntityQuery entityQuery : queries) {
                    filterValues.add(entityQuery.getValue());
                }

                List<String> colsForCombo = ConstantsAndUtils.nodeTypeToTableMappings.get(nodeLabel).get(table);
                for (String col : colsForCombo) {
                    System.out.println("Column filter being used as " + col + " and value " + filterValues);
                    columnFilters.put(col, filterValues);
                }
            }

            HashMap<String, String> timeFilter = new HashMap<>();
            timeFilter.put("start_time", this.startTime);
            timeFilter.put("end_time", this.endTime);

            DataExtractorExecutor dataExtractor = new DataExtractorExecutor(table, new ArrayList<>(tableCols));
            dataExtractor.setTimeFilter(timeFilter, ConstantsAndUtils.timeFilterColPerTable.get(table));
            dataExtractor.setLevels(this.LEVEL);
            try {
                dataExtractor.setConnection(SnowFlakeConnectionPool.getConnection());
                successTables.add(table);
            } catch (SQLException e) {
                e.printStackTrace();
                failedTables.add(table);
            }
            dataExtractor.setColumnFilter(columnFilters);

            tasksQueue.add(executor.submit(dataExtractor));
        }
        String successTable = String.join(",", successTables);
        String failedTable = String.join(",", failedTables);
        String status = String.format("Queried table. Success: [%s] & Failed: [%s]", successTable, failedTable);
        coreGrpcClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);
    }

    public HashMap<String, ArrayList<Map<String, Object>>> get() throws Exception {
        HashMap<String, ArrayList<Map<String, Object>>> datasets = new HashMap<>();

        StringBuilder status = new StringBuilder();
        execute();

        for (Future<HashMap<String, ArrayList<Map<String, Object>>>> task : tasksQueue) {
            HashMap<String, ArrayList<Map<String, Object>>> resultForTable = task.get();
            String tableName = resultForTable.keySet().toArray(new String[0])[0];
            datasets.put(tableName, resultForTable.get(tableName));

            allTables.remove(tableName);

            String statusMsg = String.format("Extracted %s (SZ: %s). Remaining: [%s], Time: %s\n", tableName,
                    resultForTable.get(tableName).size(), String.join(",", allTables), getCurrentLocalDateTimeStamp());
            status.append(statusMsg);
        }
        if (failedTables.size() > 0) {
            System.out.printf("ERROR: Couldn't execute tables %s", failedTables);
        }
        coreGrpcClient.updateCaseLoadingStatus(status.toString(), CaseSubmissionPayload.getDefaultInstance(), caseId);
        return datasets;
    }

    private String getCurrentLocalDateTimeStamp() {
        return LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"));
    }

    public void close() {
        executor.shutdownNow();
        tasksQueue.clear();
        failedTables.clear();
        try {
            executor.awaitTermination(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
