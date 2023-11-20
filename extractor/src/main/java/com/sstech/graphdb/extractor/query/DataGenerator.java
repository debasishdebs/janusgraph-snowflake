package com.sstech.graphdb.extractor.query;

import com.elysum.springboot.service.SnowflakeQueryService;
import com.sstech.graphdb.extractor.client.CoreGrpcClient;

import java.util.*;

public class DataGenerator {
    private String TABLE_NAME;
    private ArrayList<String> TABLE_COL;
    private HashMap<String, ArrayList<String >> COL_FILTERS;
    private HashMap<String, String> TIME_FILLERS;
    private SnowflakeQueryService queryService;

//    private HashMap<String, ArrayList<String>> pairsDict = new HashMap<String, ArrayList<String>>() {
//        {
//            put("user_name", new ArrayList<String>() {{ add("src_user_name"); add("dst_user_name"); }});
//            put("host", new ArrayList<String>() {{ add("src_host"); add("dst_host"); }});
//            put("ip", new ArrayList<String>() {{ add("src_ip"); }});
//        }
//    };

    private HashMap<String, HashMap<String, List<String>>> pairsDict = new HashMap<String, HashMap<String, List<String>>>() {{
        put("MS_WIN_SECURITYAUDITING_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("subjectusername", "targetusername"));
            put("host", Arrays.asList("hostname")); put("ip", Arrays.asList("ipaddress"));
        }});
        put("MS_WIN_SECURITYAUDITING_NETTRAFFIC_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Collections.emptyList());
            put("host", Arrays.asList("hostname")); put("ip", Arrays.asList("sourceaddress", "destaddress"));
        }});
        put("MS_WIN_SYSMON_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("user"));
            put("host", Arrays.asList("destinationhostname", "hostname", "sourcehostname"));
            put("ip", Arrays.asList("destinationip", "sourceip"));
        }});
        /* put("MS_EXCH_AGENT", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("recipient"));
            put("host", Arrays.asList("hostname"));
            put("ip", Arrays.asList("dst_ip", "src_ip"));
        }}); */
        put("MS_EXCH_CONNECTIVITY_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("destination"));
            put("host", Arrays.asList("hostname"));
            put("ip", Collections.emptyList());
        }});
        put("MS_EXCH_MESSAGETRACKING_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("sender_address", "recipient_address"));
            put("host", Arrays.asList("client_hostname", "hostname", "server_hostname"));
            put("ip", Arrays.asList("original_server_ip", "original_client_ip", "client_ip", "server_ip"));
        }});
        put("WG_FW_EVENTSALARMS_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("user_name"));
            put("host", Arrays.asList("syslog_host"));
            put("ip", Arrays.asList("ip_dst_addr", "ip_src_addr"));
        }});
        put("WG_FW_NETWORKTRAFFIC_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("src_user", "dst_user"));
            put("host", Arrays.asList("syslog_host"));
            put("ip", Arrays.asList("ip_dst_addr", "ip_src_addr"));
        }});
        put("WG_FW_NETFLOW_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Collections.emptyList());
            put("host", Collections.emptyList());
            put("ip", Arrays.asList("ipv4_src_addr", "ipv4_dst_addr", "host"));
        }});
        put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", new HashMap<String, List<String>>() {{
            put("user_name",Collections.emptyList());
            put("host", Arrays.asList("hostname"));
            put("ip", Collections.emptyList());
        }});
        put("SYM_ES_NETWORKPROTECTION_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Collections.emptyList());
            put("host", Arrays.asList("hostname"));
            put("ip", Collections.emptyList());
        }});
    }};

    private int LEVEL;
    private String timeColumn;
    private ArrayList<ArrayList<Map<String, Object>>> datasets = new ArrayList();
    private ArrayList<HashMap<String, ArrayList<String>>> customDataStructures = new ArrayList<>();
    private int BATCH = 25000;
    private int limit = 100000;
    private CoreGrpcClient coreClient = null;
    private String caseId = null;

    public DataGenerator(String tbl, ArrayList<String> columns, SnowflakeQueryService queryService,
                          HashMap<String, ArrayList<String >> columnFilter, HashMap<String, String> timeFilter, int LVL, String timeCol) {
//        System.out.println("Inside query datagenerator and level is " + LVL);

        this.TABLE_NAME = tbl;
        this.TABLE_COL = columns;
        this.COL_FILTERS = columnFilter;
        this.TIME_FILLERS = timeFilter;
        this.queryService = queryService;
        this.LEVEL = LVL;
        this.timeColumn = timeCol;

        System.out.println(String.format("The filter is %s and keyName is %s", columnFilter, this.pairsDict.get(tbl)));
    }

    public void setCoreClient(CoreGrpcClient client) {
        this.coreClient = client;
    }

    public void setSetCaseId(String caseId) {
        this.caseId = caseId;
    }

    public void generate() throws Exception {
        List<Object> level0Results = this.level0_query_generator();

        this.customDataStructures.add(this.convertData(level0Results));
        this.datasets.add(this.convertDataToRows(level0Results));

        for (int i = 1; i < this.LEVEL; i++) {
//            System.out.println("Level " + i);
            this.leveln_query_generator(this.customDataStructures.get(this.customDataStructures.size()-1), i);
        }
    }

    private ArrayList<Map<String, Object>> mergeDatasets() {
        ArrayList<Map<String, Object>> mergedDataset = new ArrayList<>();
        for (ArrayList<Map<String, Object>> dataset : this.datasets) {
            mergedDataset.addAll(dataset);
        }
        return mergedDataset;
    }

    public ArrayList<Map<String, Object>> getDataset() {
        return this.mergeDatasets();
    }

    private HashMap<String, ArrayList<String>> convertData(List<Object> data) {
//        ArrayList<String> columns = new ArrayList<>();
//
//        for (Object o : data) {
//            Map<String,Object> row =  (Map<String, Object>) o;
//            row.forEach( (k, v) -> {
//                columns.add(k);
//            });
//            break;
//        }

        HashMap<String, ArrayList<String >> convertedData = new HashMap<>();
        for (Object o : data) {
            Map<String,Object> row =  (Map<String, Object>) o;
            row.forEach( (k, v) -> {
                ArrayList<String> existing = convertedData.get(k);
                if (existing != null) {
                    existing.add((String) v);
                }
                else {
//                    System.out.println(String.format("Got null existing value for col: %s val: %s", k, v));
                    existing = new ArrayList<String>() {{
                        add((String) v);
                    }};
                }
                convertedData.put(k.toLowerCase(), existing);
            });
        }
        return convertedData;
    }

    private ArrayList<Map<String, Object>> convertDataToRows(List<Object> data) {
        ArrayList<Map<String, Object>> convertedData = new ArrayList<>();

        for (Object o : data) {
            Map<String,Object> row =  (Map<String, Object>) o;
            convertedData.add(row);
        }
        return convertedData;
    }

    private void leveln_query_generator(HashMap<String, ArrayList<String>> data, int lvl) throws Exception {
//        System.out.println("Privious iteration data is ");
//        System.out.println(data);
//        System.out.println(data.keySet());

        HashMap<String, ArrayList<String>> new_query_dict = new HashMap();
        Set<String> pairsKeys = this.pairsDict.get(this.TABLE_NAME).keySet();

        for (String pairsKey : pairsKeys) {
            List<String> pairValue = this.pairsDict.get(this.TABLE_NAME).get(pairsKey);
//            System.out.println("The pairs for pairKey " + pairsKey + " and table " + this.TABLE_NAME + " are " + pairValue);
            ArrayList<String> val_list = new ArrayList<String>();

            for (String col : pairValue) {
//                [val_list.append(str(val)) for val in pdf[col].unique() if (val not in ['-',None] + column_filter[col])]
                ArrayList<String> columnData = data.get(col);
//                System.out.println(String.format("For col %s, the existing data is %s", col, columnData));
                if (columnData != null) {
                    HashSet<String> uniqueColumnData = new HashSet<String>(columnData);
//                    System.out.println(uniqueColumnData);
                    for (String val : uniqueColumnData) {
                        ArrayList<String> valueSkip = new ArrayList<String>() {{
                            add("-"); add(null); add("SYSTEM"); add("system"); add(""); add(" ");
                            add("BDLOGWatch2.sstech.internal"); add("NAM12-MW2-obe.outbound.protection.outlook.com");
                            add("EXCHSRVRTPA03"); add("EXCHSRVRTPA03"); add("d135953.o.ess.barracudanetworks.com");
                            add("fe80::65e6:bfc1:28bb:6757, ff02::fb"); add("fe80::819f:69f6:ffae:90ca%10");
                            add("fe80::4295:bdff:fe05:712c"); add("fe80::65e6:bfc1:28bb:6757");
                            add("ff02:0:0:0:0:0:1:2"); add("fe80:0:0:0:65e6:bfc1:28bb:6757");
                            add("SSTECH_TPA_XTM_525"); add("::1"); add("localhost"); add("127.0.0.1");
                            add("destination"); add("hostname"); add("SSTECH_Dallas_XTM5"); add("SSDLWTSIEM.sstech.internal");
                            add("noreply@yupptvemails.com"); add("NAM11-BN8-obe.outbound.protection.outlook.com");
                            add("confluence@mail-us.atlassian.net"); add("destination"); add("hostname");
                        }};

                        if (this.COL_FILTERS.get(col) != null)
                            valueSkip.addAll(this.COL_FILTERS.get(col));
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

//        System.out.println("In Level n generator executing for lvl " + lvl + " by calling level0");
        System.out.println("And the query dict is " + new_query_dict + " for next iteration");
        List<Object> levelNData = this.level0_query_generator(new_query_dict, lvl);

        ArrayList<Map<String, Object>> convertedData = this.convertDataToRows(levelNData);
        HashMap<String, ArrayList<String>> customDataStructure = this.convertData(levelNData);

        this.datasets.add(convertedData);
        this.customDataStructures.add(customDataStructure);
    }

    private List<Object> level0_query_generator(HashMap<String, ArrayList<String >> columnFilter, int lvl) throws Exception {
        ArrayList<String> col_filter_lst = new ArrayList<>();
        int filter_counter = 0;

        String select_query = "select distinct " + String.join(", ", this.TABLE_COL) + ", " + lvl + " as level from " + this.TABLE_NAME;
        String count_select = "select count(*) as count from " + this.TABLE_NAME;
        String where_clause = " where " + this.timeColumn + " between '" + this.TIME_FILLERS.get("start_time") + "' and '" + this.TIME_FILLERS.get("end_time") + "'";

        Set<String> keys = columnFilter.keySet();
        List<Object> executeQryList = new ArrayList<>();

        if (keys.size() == 0)
            // Initialize as empty list if no filters are provided
            executeQryList = new ArrayList<>();
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

            List<Object> countValue = queryService.executeQuery(countQuery);
            int numRows = Integer.parseInt((String) ((Map<String, Object>)countValue.get(0)).get("COUNT"));
            System.out.println("Number of rows is " + numRows);

            if (numRows < this.BATCH) {
                System.out.println("In Level " + lvl + " custom generator executor from inside leveln");
                System.out.println(query);
                System.out.println("===================");

                long startTime = System.currentTimeMillis();
                executeQryList = queryService.executeQuery(query);
                Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;
//                String status = String.format("Extracted Level: %d, TBL: %s, ALL (Rows < Batch), Filter: %s, Duration (Sec): %f, Rows: %d, QUERY: [ %s ]",
//                        lvl, TABLE_NAME, col_filter_lst.toString(), duration, numRows, query);
//                coreClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

            } else {
                int iter = 1;
                System.out.println("The number of rows " + numRows + " is greater than specified batch size " + this.BATCH + " so going to execute in batches");

                if (this.limit != -1 && numRows > this.limit)
                    numRows = this.limit;
                System.out.println("Updated number of rows after applying conditions of limit and batch size is " + numRows);

                for (int i = 0; i < numRows; i+=this.BATCH) {
                    String pageQuery;
                    if (i == 0)
                        pageQuery = String.format(" limit %s ", this.BATCH);
                    else
                        pageQuery = String.format(" limit %s offset %s ", this.BATCH, i+1);

                    String tmpQuery = query + pageQuery;

                    System.out.println("In Level " + lvl + " custom generator executor from inside leveln for batch " + iter + " between " + (i+1) + " and " + ((i+1)+this.BATCH));
                    System.out.println(tmpQuery);
                    System.out.println("===================");

                    long startTime = System.currentTimeMillis();
                    List<Object> tmp = queryService.executeQuery(tmpQuery);
                    Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;
//                    String status = String.format("Extracted Level: %d, TBL: %s, PAGE %d (%d to %d), Filter: %s, Duration (Sec): %f, Rows: %d, QUERY: [ %s ]",
//                            lvl, TABLE_NAME, iter,  i+1, BATCH,col_filter_lst.toString(), duration, tmp.size(), query);
//                    coreClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

                    executeQryList.addAll(tmp);
                    iter += 1;
                }
            }
//            query += " \n limit 250000";
//
//            System.out.println("In Level " + lvl + " custom generator executor from inside leveln");
//            System.out.println(query);
//            System.out.println("===================");
//
//            executeQryList = queryService.executeQuery(query);
        }
//        List<Object> executeQryList = Collections.emptyList();
        return new ArrayList<>(new HashSet<>(executeQryList));//executeQryList;
    }

    private List<Object> level0_query_generator() throws Exception {
        ArrayList<String> col_filter_lst = new ArrayList<>();
        int filter_counter = 0;

        String select_query = "select distinct " + String.join(", ", this.TABLE_COL) + " , 0 as level from " + this.TABLE_NAME;
        String count_select = "select count(*) as count from " + this.TABLE_NAME;
        String where_clause = " where " + this.timeColumn + " between '" + this.TIME_FILLERS.get("start_time") + "' and '" + this.TIME_FILLERS.get("end_time") + "'";

        List<Object> executeQryList = new ArrayList<>();
        Set<String> keys = this.COL_FILTERS.keySet();

        if (keys.size() == 0)
            // Initialize as empty list if no filters are provided
            executeQryList = new ArrayList<>();
        else {
            for (String key : keys) {
                ArrayList<String> value = this.COL_FILTERS.get(key);
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

            List<Object> countValue = queryService.executeQuery(countQuery);
            int numRows = Integer.parseInt((String) ((Map<String, Object>)countValue.get(0)).get("COUNT"));
            System.out.println("Number of rows is " + numRows);
            if (this.limit != -1 && numRows > this.limit)
                numRows = this.limit;

            if (numRows < this.BATCH) {
                System.out.println("In Level 0 generator executing");
                System.out.println(query);
                System.out.println("===================");

                long startTime = System.currentTimeMillis();
                executeQryList = queryService.executeQuery(query);
                Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;
//                String status = String.format("Extracted Level: 0, TBL: %s, ALL (Rows < Batch), Filter: %s, Duration (Sec): %f, Rows: %d, QUERY: [ %s ]",
//                        TABLE_NAME, col_filter_lst.toString(), duration, numRows, query);
//                coreClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

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
                    List<Object> tmp = queryService.executeQuery(tmpQuery);
                    Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;
//                    String status = String.format("Extracted Level: 0, TBL: %s, PAGE %d (%d to %d), Filter: %s, Duration (Sec): %f, Rows: %d, QUERY: [ %s ]",
//                            TABLE_NAME, iter,  i+1, BATCH, col_filter_lst.toString(), duration, tmp.size(), query);
//                    coreClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

                    executeQryList.addAll(tmp);
                    iter += 1;
                }
            }

//            query += " \n limit 250000";
//
//            System.out.println("In Level 0 generator executing");
//            System.out.println(query);
//            System.out.println("===================");

//        List<Object> executeQryList = Collections.emptyList();
//            executeQryList = queryService.executeQuery(query);
        }
//        System.out.println("The datagen is " + executeQryList);
        return new ArrayList<>(new HashSet<>(executeQryList));
    }
}
