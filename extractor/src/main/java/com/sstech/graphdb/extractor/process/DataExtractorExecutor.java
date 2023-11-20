package com.sstech.graphdb.extractor.process;

import com.sstech.graphdb.extractor.bean.SnowFlakeConnection;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;

import java.sql.SQLException;
import java.util.*;
import java.util.concurrent.Callable;

public class DataExtractorExecutor implements Callable<HashMap<String, ArrayList<Map<String, Object>>>> {

    private final String tableName;
    private final List<String> columnNames;
    private HashMap<String, String> timeFilter;
    private String timeColumn;
    private Integer levels;
    private HashMap<String, ArrayList<String >> columnFilter;
    private SnowFlakeConnection snowflakeConnection;

    private int BATCH = 100000;
    private int limit = 300000;

    private final ArrayList<HashMap<String, ArrayList<String>>> customDataStructures = new ArrayList<>();
    private final ArrayList<ArrayList<Map<String, Object>>> datasets = new ArrayList<>();

    public DataExtractorExecutor(String table, List<String> columns) {
        this.tableName = table;
        this.columnNames = columns;
    }

    public DataExtractorExecutor setTimeFilter(HashMap<String, String> timeFilter, String timeColumn) {
        this.timeFilter = timeFilter;
        this.timeColumn = timeColumn;
        return this;
    }

    public DataExtractorExecutor setLevels(Integer levels) {
        this.levels = levels;
        return this;
    }

    public DataExtractorExecutor setConnection (SnowFlakeConnection conn) {
        this.snowflakeConnection = conn;
        return this;
    }

    public DataExtractorExecutor setColumnFilter(HashMap<String, ArrayList<String >> columnFilter) {
        this.columnFilter = columnFilter;
        return this;
    }

    public DataExtractorExecutor setLimitAndBatchSize(Integer limit, Integer batchSize) {
        this.limit = limit;
        this.BATCH = batchSize;
        return this;
    }

    public HashMap<String, ArrayList<Map<String, Object>>> call() {
        try {
            List<HashMap<String, Object>> level0Results = this.level0_query_generator();

            this.customDataStructures.add(this.convertData(level0Results));
            this.datasets.add(new ArrayList<>(level0Results));

            for (int level = 1; level < this.levels; level++) {
                this.leveln_query_generator(this.customDataStructures.get(this.customDataStructures.size() - 1), level);
            }
        } catch (SQLException e) {
            e.printStackTrace();
            System.out.println("ERROR: Couldn't execute queries");
        }

        close();
        return new HashMap<String, ArrayList<Map<String, Object>>>(){{
            put(tableName, mergeDatasets());
        }};
    }

    public void close() {
        snowflakeConnection.close();
        this.customDataStructures.clear();
        this.columnFilter.clear();
        this.timeFilter.clear();
        this.columnNames.clear();
    }

    private ArrayList<Map<String, Object>> mergeDatasets() {
        ArrayList<Map<String, Object>> mergedDataset = new ArrayList<>();
        for (ArrayList<Map<String, Object>> dataset : this.datasets) {
            mergedDataset.addAll(dataset);
        }
        return mergedDataset;
    }

    private HashMap<String, ArrayList<String>> convertData(List<HashMap<String, Object>> data) {
        HashMap<String, ArrayList<String >> convertedData = new HashMap<>();
        for (HashMap<String, Object> row : data) {
            row.forEach( (k, v) -> {
                ArrayList<String> existing = convertedData.get(k);
                if (existing != null) {
                    existing.add((String) v);
                }
                else {
                    existing = new ArrayList<String>() {{
                        add((String) v);
                    }};
                }
                convertedData.put(k.toLowerCase(), existing);
            });
        }
        return convertedData;
    }

    private List<HashMap<String, Object>> level0_query_generator() throws SQLException {
        ArrayList<String> col_filter_lst = new ArrayList<>();
        int filter_counter = 0;

        String select_query = "select distinct " + String.join(", ", columnNames) + " , 0 as level from " + tableName;
        String count_select = "select count(*) as count from " + tableName;
        String where_clause = " where " + this.timeColumn + " between '" + timeFilter.get("start_time") + "' and '" + timeFilter.get("end_time") + "'";

        List<HashMap<String, Object>> queryResults = new ArrayList<>();
        Set<String> keys = columnFilter.keySet();

        if (keys.size() == 0)
            // Initialize as empty list if no filters are provided
            queryResults = new ArrayList<>();
        else {
            for (String label : keys) {
                ArrayList<String> value = columnFilter.get(label);
                if (value.size() > 0) {
                    if (value.size() == 1 && value.get(0).toLowerCase().equals("all"))
                        continue;

                    col_filter_lst.add(label + " in ('" + String.join("','", value) + "')");
                    filter_counter += 1;
                }
            }

            String col_where_clause = "";
            if (filter_counter > 0) {
                col_where_clause = " and (" + String.join(" or ", col_filter_lst) + ")";
            }
            String query = select_query + where_clause + col_where_clause;
            String countQuery = count_select + where_clause + col_where_clause;

            List<HashMap<String, Object>> countValue = snowflakeConnection.executeQuery(countQuery).getResults();
            int numRows = Integer.parseInt((String) countValue.get(0).get("COUNT"));
            System.out.println("Number of rows is " + numRows);

            if (this.limit != -1 && numRows > this.limit)
                numRows = this.limit;

            if (numRows < this.BATCH) {
                System.out.println("In Level 0 generator executing");
                System.out.println(query);
                System.out.println("===================");

                long startTime = System.currentTimeMillis();
                System.out.printf("Executing query %s\n", query);
                queryResults = snowflakeConnection.executeQuery(query).getResults();
                Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;

            } else {
                System.out.println("The number of rows " + numRows + " is greater than specified batch size " + this.BATCH + " so going to execute in batches");

                int iter = 1;
                for (int i = 0; i < numRows; i+=this.BATCH) {
                    String pageQuery;
                    if (i == 0)
                        pageQuery = String.format(" limit %s ", this.BATCH);
                    else
                        pageQuery = String.format(" limit %s offset %s ", this.BATCH, i+1);
                    String tmpQuery = query + pageQuery;

                    System.out.println("In Level 0 generator executing for batch " + iter + " between " + (i+1) + " and " + ((i+1)+this.BATCH));
                    System.out.println(tmpQuery);
                    System.out.println("===================");

                    long startTime = System.currentTimeMillis();
                    List<HashMap<String, Object>> batchedResults = snowflakeConnection.executeQuery(tmpQuery).getResults();
                    Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;

                    queryResults.addAll(batchedResults);
                    iter += 1;
                }
            }
        }
        return new ArrayList<>(new HashSet<>(queryResults));
    }

    private List<HashMap<String, Object>> level0_query_generator(HashMap<String, ArrayList<String >> columnFilter, int lvl) throws SQLException {
        ArrayList<String> col_filter_lst = new ArrayList<>();
        int filter_counter = 0;

        String select_query = "select distinct " + String.join(", ", columnNames) + ", " + lvl + " as level from " + tableName;
        String count_select = "select count(*) as count from " + tableName;
        String where_clause = " where " + this.timeColumn + " between '" + timeFilter.get("start_time") + "' and '" + timeFilter.get("end_time") + "'";

        Set<String> keys = columnFilter.keySet();
        List<HashMap<String, Object>> queryResults = new ArrayList<>();

        if (keys.size() == 0)
            // Initialize as empty list if no filters are provided
            queryResults = new ArrayList<>();
        else {
            for (String key : keys) {
                ArrayList<String> value = columnFilter.get(key);
                if (value.size() > 0) {
                    col_filter_lst.add(key + " in ('" + String.join("','", value) + "')");
                    filter_counter += 1;
                }
            }

            String col_where_clause = "";
            if (filter_counter > 0) {
                col_where_clause = " and (" + String.join(" or ", col_filter_lst) + ")";
            }
            String query = select_query + where_clause + col_where_clause;
            String countQuery = count_select + where_clause + col_where_clause;

            List<HashMap<String, Object>> countValue = snowflakeConnection.executeQuery(countQuery).getResults();
            int numRows = Integer.parseInt((String) ((Map<String, Object>) countValue.get(0)).get("COUNT"));
            System.out.println("Number of rows is " + numRows);

            if (numRows < this.BATCH) {
                System.out.println("In Level " + lvl + " custom generator executor from inside leveln");
                System.out.println(query);
                System.out.println("===================");

                long startTime = System.currentTimeMillis();
                queryResults = snowflakeConnection.executeQuery(query).getResults();
                Double duration = (System.currentTimeMillis() - startTime) / (double) 1000;

            } else {
                int iter = 1;
                System.out.println("The number of rows " + numRows + " is greater than specified batch size " + this.BATCH + " so going to execute in batches");

                if (this.limit != -1 && numRows > this.limit)
                    numRows = this.limit;
                System.out.println("Updated number of rows after applying conditions of limit and batch size is " + numRows);

                for (int i = 0; i < numRows; i += this.BATCH) {
                    String pageQuery;
                    if (i == 0)
                        pageQuery = String.format(" limit %s ", this.BATCH);
                    else
                        pageQuery = String.format(" limit %s offset %s ", this.BATCH, i + 1);
                    String batchQuery = query + pageQuery;

                    System.out.println("In Level " + lvl + " custom generator executor from inside leveln for batch " + iter + " between " + (i + 1) + " and " + ((i + 1) + this.BATCH));
                    System.out.println(batchQuery);
                    System.out.println("===================");

                    long startTime = System.currentTimeMillis();
                    List<HashMap<String, Object>> batchResults = snowflakeConnection.executeQuery(batchQuery).getResults();
                    Double duration = (System.currentTimeMillis() - startTime) / (double) 1000;

                    queryResults.addAll(batchResults);
                    iter += 1;
                }
            }
        }
        return new ArrayList<>(new HashSet<>(queryResults));
    }

    private void leveln_query_generator(HashMap<String, ArrayList<String>> data, int lvl) throws SQLException {
        HashMap<String, ArrayList<String>> new_query_dict = new HashMap<>();
        Set<String> pairs = ConstantsAndUtils.columnPairsPerLabelDict.get(tableName).keySet();

        for (String pairsKey : pairs) {
            List<String> pairValue = ConstantsAndUtils.columnPairsPerLabelDict.get(tableName).get(pairsKey);
            ArrayList<String> val_list = new ArrayList<>();

            for (String col : pairValue) {
                ArrayList<String> columnData = data.get(col);
                if (columnData != null) {
                    HashSet<String> uniqueColumnData = new HashSet<>(columnData);
                    for (String val : uniqueColumnData) {
                        ArrayList<String> valueSkip = ConstantsAndUtils.valueToSkip;

                        if (columnFilter.get(col) != null)
                            valueSkip.addAll(columnFilter.get(col));
                        if (!valueSkip.contains(val)) {
                            val_list.add(val);
                        }
                    }
                    if (val_list.size()> 0) {
                        new_query_dict.put(col, val_list);
                    }
                }
            }
        }

        System.out.println("And the query dict is " + new_query_dict + " for next iteration");
        List<HashMap<String, Object>> levelNData = this.level0_query_generator(new_query_dict, lvl);

        ArrayList<Map<String, Object>> convertedData = new ArrayList<>(levelNData);
        HashMap<String, ArrayList<String>> customDataStructure = this.convertData(levelNData);

        this.datasets.add(convertedData);
        this.customDataStructures.add(customDataStructure);
    }
}
