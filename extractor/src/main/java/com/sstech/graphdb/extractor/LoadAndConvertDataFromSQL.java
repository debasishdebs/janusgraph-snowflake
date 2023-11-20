package com.sstech.graphdb.extractor;

import com.elysum.springboot.service.SnowflakeQueryService;
import com.google.common.base.Preconditions;
import com.sstech.graphdb.extractor.client.CoreGrpcClient;
import com.sstech.graphdb.extractor.client.TransformerGrpcClient;
import com.sstech.graphdb.extractor.process.QueryDataExtractor;
import com.sstech.graphdb.extractor.query.DataGenerator;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.grpc.*;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.util.*;

public class LoadAndConvertDataFromSQL {
    CoreGrpcClient coreGrpcClient;
    TransformerGrpcClient transformerGrpcClient;
    SnowflakeQueryService snowflakeQueryService;

    private List<WindowsRecord> windowsRecords = new ArrayList<>();
    private List<WatchGuardRecord> watchGuardRecords = new ArrayList<>();
    private List<MsExchangeRecord> exchangeRecords = new ArrayList<>();
    private List<SysmonRecord> sysmonRecords = new ArrayList<>();
    private List<SEPCRecord> sepcRecords = new ArrayList<>();
    private boolean status = false;
    HashMap<String, List<String>> dataToQuery = null;
    boolean useMultiThreaded = true;
    CaseSubmissionPayload query = null;

    HashMap<String, ArrayList<HashMap<String, Object>>> allTableData = new HashMap<>();

    private String TABLE = "graph_db_usecase";
    private ArrayList<String> TBL_COLS = new ArrayList<String>(){{
        add("src_user_name"); add("dst_user_name"); add("src_host"); add("dst_host"); add("src_ip");
    }};
    private HashMap<String, String> TIME_FILTER = new HashMap<>();
    private int LEVEL = 3;

//    HashMap<String, String> timeFilter = new HashMap<String, String>() {{
//        put("MS_WIN_SECURITYAUDITING", "event_time");
//        put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", "event_time");
//        put("MS_WIN_SYSMON", "event_time");
////        put("MS_EXCH_AGENT", "event_time");
//        put("MS_EXCH_CONNECTIVITY", "event_time");
//        put("MS_EXCH_MESSAGETRACKING", "event_time");
//        put("WG_FW_EVENTSALARMS", "syslog_event_datetime");
//        put("WG_FW_NETWORKTRAFFIC", "syslog_event_datetime");
//        put("WG_FW_NETFLOW", "event_time");
//        put("SYM_ES_ENDPOINTPROTECTIONCLIENT", "event_time");
//        put("SYM_ES_NETWORKPROTECTION", "event_time");
//    }};
//
//    HashMap<String, HashMap<String, List<String>>> labelTableMapping = new HashMap<String, HashMap<String, List<String>>>() {{
//        put("host", new HashMap<String, List<String>>() {{
//            put("MS_WIN_SECURITYAUDITING", Arrays.asList("hostname"));
//            put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", Arrays.asList("hostname"));
//            put("MS_WIN_SYSMON", Arrays.asList("destinationhostname", "sourcehostname", "hostname"));
////            put("MS_EXCH_AGENT", Arrays.asList("hostname"));
//            put("MS_EXCH_CONNECTIVITY", Arrays.asList("hostname"));
//            put("MS_EXCH_MESSAGETRACKING", Arrays.asList("client_hostname", "server_hostname", "hostname"));
//            put("WG_FW_EVENTSALARMS", Arrays.asList("syslog_host"));
//            put("WG_FW_NETWORKTRAFFIC", Arrays.asList("syslog_host"));
//            put("WG_FW_NETFLOW", Arrays.asList());
//            put("SYM_ES_ENDPOINTPROTECTIONCLIENT", Arrays.asList("hostname"));
//            put("SYM_ES_NETWORKPROTECTION", Arrays.asList("hostname"));
//        }});
//        put("user", new HashMap<String, List<String>>() {{
//            put("MS_WIN_SECURITYAUDITING", Arrays.asList("subjectusername", "targetusername"));
//            put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", Arrays.asList());
//            put("MS_WIN_SYSMON", Arrays.asList("user_name"));
////            put("MS_EXCH_AGENT", Arrays.asList("recipient"));
//            put("MS_EXCH_CONNECTIVITY", Arrays.asList());
//            put("MS_EXCH_MESSAGETRACKING", Arrays.asList("recipient_address", "sender_address"));
//            put("WG_FW_EVENTSALARMS", Arrays.asList());
//            put("WG_FW_NETWORKTRAFFIC", Arrays.asList("src_user", "dst_user"));
//            put("WG_FW_NETFLOW", Arrays.asList());
//            put("SYM_ES_ENDPOINTPROTECTIONCLIENT", Arrays.asList());
//            put("SYM_ES_NETWORKPROTECTION", Arrays.asList());
//        }});
//        put("IP", new HashMap<String, List<String>>() {{
//            put("MS_WIN_SECURITYAUDITING", Arrays.asList("ipaddress"));
//            put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", Arrays.asList("sourceaddress", "destaddress"));
//            put("MS_WIN_SYSMON", Arrays.asList("destinationip", "sourceip"));
////            put("MS_EXCH_AGENT", Arrays.asList("dst_ip", "src_ip"));
//            put("MS_EXCH_CONNECTIVITY", Arrays.asList());
//            put("MS_EXCH_MESSAGETRACKING", Arrays.asList("client_ip", "server_ip"));
//            put("WG_FW_EVENTSALARMS", Arrays.asList("ip_src_addr", "ip_dst_addr"));
//            put("WG_FW_NETWORKTRAFFIC", Arrays.asList("ip_src_addr", "ip_dst_addr"));
//            put("WG_FW_NETFLOW", Arrays.asList("ipv4_dst_addr", "ipv4_src_addr", "host"));
//            put("SYM_ES_ENDPOINTPROTECTIONCLIENT", Arrays.asList());
//            put("SYM_ES_NETWORKPROTECTION", Arrays.asList());
//        }});
//    }};
//
//    private HashMap<String, ArrayList<String>> dataSourceToTableMaps = new HashMap<String, ArrayList<String>>() {{
//        put("windows", new ArrayList<String>() {{
//            add("MS_WIN_SECURITYAUDITING");
//            add("MS_WIN_SECURITYAUDITING_NETTRAFFIC");
//        }});
//        put("sysmon", new ArrayList<String>() {{
//            add("MS_WIN_SYSMON");
//        }});
//        put("msexchange", new ArrayList<String>() {{ /*add("MS_EXCH_AGENT");*/
//            add("MS_EXCH_CONNECTIVITY");
//            add("MS_EXCH_MESSAGETRACKING");
//        }});
//        put("watchguard", new ArrayList<String>() {{
//            add("WG_FW_EVENTSALARMS");
//            add("WG_FW_NETFLOW");
//            add("WG_FW_NETWORKTRAFFIC");
//        }});
//        put("sepc", new ArrayList<String>() {{
//            add("SYM_ES_ENDPOINTPROTECTIONCLIENT");
//            add("SYM_ES_NETWORKPROTECTION");
//        }});
//    }};

    HashMap<String, String> timeFilter = new HashMap<String, String>() {{
        put("MS_WIN_SECURITYAUDITING_DEMO", "eventtime");
        put("MS_WIN_SYSMON_DEMO", "eventtime");
        put("MS_EXCH_MESSAGETRACKING_DEMO", "datetime");
        put("WG_FW_NETWORKTRAFFIC_DEMO", "timestamp");
        put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", "eventtime");
    }};

    HashMap<String, HashMap<String, List<String>>> labelTableMapping = new HashMap<String, HashMap<String, List<String>>>() {{
        put("host", new HashMap<String, List<String>>() {{
            put("MS_WIN_SECURITYAUDITING_DEMO", Arrays.asList("hostname"));
            put("MS_WIN_SYSMON_DEMO", Arrays.asList("destinationhostname", "sourcehostname", "hostname"));
            put("MS_EXCH_MESSAGETRACKING_DEMO", Arrays.asList("client_hostname", "server_hostname", "hostname"));
            put("WG_FW_NETWORKTRAFFIC_DEMO", Arrays.asList("syslog_host"));
            put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", Arrays.asList("hostname"));
        }});
        put("user", new HashMap<String, List<String>>() {{
            put("MS_WIN_SECURITYAUDITING_DEMO", Arrays.asList("subjectusername", "targetusername"));
            put("MS_WIN_SYSMON_DEMO", Arrays.asList("user"));
            put("MS_EXCH_MESSAGETRACKING_DEMO", Arrays.asList("recipient_address", "sender_address"));
            put("WG_FW_NETWORKTRAFFIC_DEMO", Arrays.asList("src_user", "dst_user"));
            put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", Arrays.asList());
        }});
        put("IP", new HashMap<String, List<String>>() {{
            put("MS_WIN_SECURITYAUDITING_DEMO", Arrays.asList("ipaddress"));
            put("MS_WIN_SYSMON_DEMO", Arrays.asList("destinationip", "sourceip"));
            put("MS_EXCH_MESSAGETRACKING_DEMO", Arrays.asList("client_ip", "server_ip"));
            put("WG_FW_NETWORKTRAFFIC_DEMO", Arrays.asList("ip_src_addr", "ip_dst_addr"));
            put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", Arrays.asList());
        }});
    }};

    private HashMap<String, ArrayList<String>> dataSourceToTableMaps = new HashMap<String, ArrayList<String>>() {{
        put("windows", new ArrayList<String>() {{
            add("MS_WIN_SECURITYAUDITING_DEMO");
            add("MS_WIN_SECURITYAUDITING_NETTRAFFIC_DEMO");
        }});
        put("sysmon", new ArrayList<String>() {{
            add("MS_WIN_SYSMON_DEMO");
        }});
        put("msexchange", new ArrayList<String>() {{ /*add("MS_EXCH_AGENT");*/
            add("MS_EXCH_CONNECTIVITY_DEMO");
            add("MS_EXCH_MESSAGETRACKING_DEMO");
        }});
        put("watchguard", new ArrayList<String>() {{
            add("WG_FW_EVENTSALARMS_DEMO");
            add("WG_FW_NETFLOW_DEMO");
            add("WG_FW_NETWORKTRAFFIC_DEMO");
        }});
        put("sepc", new ArrayList<String>() {{
            add("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO");
            add("SYM_ES_NETWORKPROTECTION_DEMO");
        }});
    }};

    private String caseId;

    private String getDataSourceFromTableName(String tbl) {
        Set<String> dss = this.dataSourceToTableMaps.keySet();
        for (String ds : dss) {
            ArrayList<String> tables = this.dataSourceToTableMaps.get(ds);
            if (tables.contains(tbl))
                return ds;
        }
        return null;
    }


    public LoadAndConvertDataFromSQL(CoreGrpcClient coreGrpcClient, TransformerGrpcClient transformerGrpcClient, SnowflakeQueryService snowflakeQueryService) {
        this.coreGrpcClient = coreGrpcClient;
        this.transformerGrpcClient = transformerGrpcClient;
        this.snowflakeQueryService = snowflakeQueryService;
//        System.out.println("Initialized the LoadAndConvertDataFromSQL constructor");
    }

    public void addTablesToExtract(HashMap<String, List<String>> dataToQuery) {
        this.dataToQuery = dataToQuery;
    }

    public void setQueryTime(Time startTime, Time endTime) {
        this.TIME_FILTER.put("start_time", this.protoTimeToString(startTime));
        this.TIME_FILTER.put("end_time", this.protoTimeToString(endTime));
    }

    public void setInformationToQuery(CaseSubmissionPayload query) {
        this.query = query;
    }

    private ArrayList<HashMap<String, Object>> mapDatasetToHashMap(ArrayList<Map<String, Object>> data) {
        ArrayList<HashMap<String, Object>> dataset = new ArrayList<>();
        for (Map<String, Object> datanum : data) {
            dataset.add(new HashMap<>(datanum));
        }
        return dataset;
    }

    private ArrayList<String> getColumnsForTable(ArrayList<HashMap<String, Object>> tbl) {
        ArrayList<String> columns = new ArrayList<>();
        for (HashMap<String, Object> row : tbl) {
            columns.addAll(row.keySet());
        }
        return new ArrayList<>(new HashSet<>(columns));
    }

    private void convertToProtoRecords(ArrayList<HashMap<String, Object>> windowsRecords,
                        ArrayList<HashMap<String, Object>> wgtrafficRecords,
                        ArrayList<HashMap<String, Object>> msexchangeRecords,
                        ArrayList<HashMap<String, Object>> sysmonRecords,
                        ArrayList<HashMap<String, Object>> sepcRecords) {

        List<WindowsRecord> wList = new ArrayList<>();
        List<WatchGuardRecord> wgList = new ArrayList<>();
        List<MsExchangeRecord> msexList = new ArrayList<>();
        List<SysmonRecord> sysmonList = new ArrayList<>();
        List<SEPCRecord> sepcList = new ArrayList<>();

        for (HashMap<String, Object> windowsRecord : windowsRecords) {
            WindowsRecord.Builder builder = WindowsRecord.newBuilder();
            Set<String> keys = windowsRecord.keySet();
            for (String key : keys) {
                builder = ConstantsAndUtils.addToWindowsRecord(builder, key, windowsRecord.get(key));
            }
            WindowsRecord record = builder.build();
            wList.add(record);
        }

        for (HashMap<String, Object> wgtrafficRecord : wgtrafficRecords) {
            WatchGuardRecord.Builder builder = WatchGuardRecord.newBuilder();
            Set<String> keys = wgtrafficRecord.keySet();
            for (String key : keys) {
                builder = ConstantsAndUtils.addToWGRecord(builder, key, wgtrafficRecord.get(key));
            }
            WatchGuardRecord record = builder.build();
            wgList.add(record);
        }

        for (HashMap<String, Object> exchangeRecord : msexchangeRecords) {
            MsExchangeRecord.Builder builder = MsExchangeRecord.newBuilder();
            Set<String> keys = exchangeRecord.keySet();
            for (String key : keys) {
                builder = ConstantsAndUtils.addToExchangeRecord(builder, key, exchangeRecord.get(key));
            }
            MsExchangeRecord record = builder.build();
            msexList.add(record);
        }

        for (HashMap<String, Object> sysmonRecord : sysmonRecords) {
            SysmonRecord.Builder builder = SysmonRecord.newBuilder();
            Set<String> keys = sysmonRecord.keySet();
            for (String key : keys) {
                builder = ConstantsAndUtils.addToSysmonRecord(builder, key, sysmonRecord.get(key));
            }
            SysmonRecord record = builder.build();
            sysmonList.add(record);
        }

        for (HashMap<String, Object> sepcRecord : sepcRecords) {
            SEPCRecord.Builder builder = SEPCRecord.newBuilder();
            Set<String> keys = sepcRecord.keySet();
            for (String key : keys) {
                builder = ConstantsAndUtils.addToSEPCRecord(builder, key, sepcRecord.get(key));
            }
            SEPCRecord record = builder.build();
            sepcList.add(record);
        }

        this.windowsRecords = wList;
        this.watchGuardRecords = wgList;
        this.exchangeRecords = msexList;
        this.sysmonRecords = sysmonList;
        this.sepcRecords = sepcList;
    }

    private void loadFromFileSystem() {
        System.out.println("Loading from file system");
        // This loads from file system
        try {
//            String rootPath = "D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\extractor\\src\\main\\resources\\data\\v4\\";
            String rootPath = "/app/src/main/resources/data/";
            System.out.println("The files in directory " + rootPath + " are");
            Files.list(new File(rootPath).toPath())
                    .limit(10)
                    .forEach(System.out::println);

//            File windowsFile = new File(rootPath + "windowsnxlog_phishing_attack_5d_2020_08_31.json");
//            File wgtrafficFile = new File(rootPath + "wgtraffic_phishing_attack_5d_2020_08_31.json");
//            File msexchangeFile = new File(rootPath + "msexchange_phishing_attack_5d_2020_09_01.json");
//            File sysmonFile = new File(rootPath + "sysmon_phishing_attack_1d_2020_08_31.json");
//            File sepcFIle = new File(rootPath + "symantecendpoint_phishing_attack_5d_2020_08_31.json");

            File windowsFile = new File(rootPath + "windowsnxlog_phishing_attack_7d_2020_09_10.json");
            File wgtrafficFile = new File(rootPath + "wgtraffic_phishing_attack_7d_2020_09_10.json");
            File msexchangeFile = new File(rootPath + "msexchange_phishing_attack_7d_2020_09_10.json");
            File sysmonFile = new File(rootPath + "sysmon_phishing_attack_1d_2020_09_10.json");
            File sepcFIle = new File(rootPath + "symantecendpoint_phishing_attack_7d_2020_09_10.json");

            JSONParser parser = new JSONParser();
            JSONArray windowsJSON = (JSONArray) parser.parse(new FileReader(windowsFile));
            JSONArray wgtrafficJSON = (JSONArray) parser.parse(new FileReader(wgtrafficFile));
            JSONArray msexchangeJSON = (JSONArray) parser.parse(new FileReader(msexchangeFile));
            JSONArray sysmonJSON = (JSONArray) parser.parse(new FileReader(sysmonFile));
            JSONArray sepcJSON = (JSONArray) parser.parse(new FileReader(sepcFIle));

            Iterator<JSONObject> windowsIter = windowsJSON.iterator();
            Iterator<JSONObject> wgtrafficIter = wgtrafficJSON.iterator();
            Iterator<JSONObject> msexchangeIter = msexchangeJSON.iterator();
            Iterator<JSONObject> sysmonIter = sysmonJSON.iterator();
            Iterator<JSONObject> sepcIter = sepcJSON.iterator();

            ArrayList<HashMap<String, Object>> windowsRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> wgtrafficRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> msexchangeRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sysmonRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sepcRecords = new ArrayList<>();

            while (windowsIter.hasNext()) {
                JSONObject record = windowsIter.next();
                HashMap<String, Object> row = new HashMap<>();
                record.forEach((key, value) -> row.put((String) key, value));
                windowsRecords.add(row);
            }

            while (wgtrafficIter.hasNext()) {
                JSONObject record = wgtrafficIter.next();
                HashMap<String, Object> row = new HashMap<>();
                record.forEach((key, value) -> row.put((String) key, value));
                wgtrafficRecords.add(row);
            }

            while (msexchangeIter.hasNext()) {
                JSONObject record = msexchangeIter.next();
                HashMap<String, Object> row = new HashMap<>();
                record.forEach((key, value) -> row.put((String) key, value));
                msexchangeRecords.add(row);
            }

            while (sysmonIter.hasNext()) {
                JSONObject record = sysmonIter.next();
                HashMap<String, Object> row = new HashMap<>();
                record.forEach((key, value) -> row.put((String) key, value));
                sysmonRecords.add(row);
            }

            while (sepcIter.hasNext()) {
                JSONObject record = sepcIter.next();
                HashMap<String, Object> row = new HashMap<>();
                record.forEach((key, value) -> row.put((String) key, value));
                sepcRecords.add(row);
            }

            this.convertToProtoRecords(windowsRecords, wgtrafficRecords, msexchangeRecords, sysmonRecords, sepcRecords);
            this.status = true;
        } catch (Exception e) {
            String rootPath = "/app/src/main/resources/data/";
            System.out.println("The files in directory " + rootPath + " are");
            try {
                Files.list(new File(rootPath).toPath())
                        .limit(10)
                        .forEach(System.out::println);
            } catch (IOException ex) {
                ex.printStackTrace();
                System.out.println("Can't read input directory STRANGE");
            }

            e.printStackTrace();
            this.status = false;
        }
    }

    private void loadFromQueryInThreads() {
        System.out.println("Loading data / Extracting data in threads");

        Set<String> tables = timeFilter.keySet();

        HashMap<String, ArrayList<Map<String, Object>>> datasets = new HashMap<>();
        try {
            QueryDataExtractor extractor = new QueryDataExtractor(query);
            extractor.setCaseId(caseId);
            extractor.setCoreGrpcClient(coreGrpcClient);
            extractor.addTablesToQuery(dataToQuery);
            extractor.setNumberOfThreads(10);
            extractor.setTables(tables);

            datasets = extractor.get();
            extractor.close();
            status = true;
        } catch (Exception e){
            status = false;
        }

        if (this.status) {
            final StringBuilder statusBuilder = new StringBuilder("Aggregating records ");

            System.out.println("=============================================");
            System.out.println("generated the datasets by executing the respective queries and are as follows");
            datasets.forEach( (tbl, data) -> {
                System.out.println("For table " + tbl + " the data as follows");
                System.out.println("Number of rows across levels is " + data.size());
                statusBuilder.append(String.format("DS: %s, Rows: %d ", tbl, data.size()));
                System.out.println("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
            });
            String status = statusBuilder.toString().trim();
            coreGrpcClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

            ArrayList<HashMap<String, Object>> windowsRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> wgtrafficRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> msexchangeRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sysmonRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sepcRecords = new ArrayList<>();

            ArrayList<String> windowsCols = new ArrayList<>();
            ArrayList<String> wgtrafficCols = new ArrayList<>();
            ArrayList<String> msexchangeCols = new ArrayList<>();
            ArrayList<String> sysmonCols = new ArrayList<>();
            ArrayList<String> sepcCols = new ArrayList<>();

            datasets.forEach( (tbl, data) -> {
                System.out.printf("Looping over ds %s dataset%n", tbl);

                String ds = this.getDataSourceFromTableName(tbl);
                if ("windows".equals(ds)) {
                    ArrayList<HashMap<String, Object>> winData = this.mapDatasetToHashMap(data);
                    windowsCols.addAll(this.getColumnsForTable(winData));
                    windowsRecords.addAll(winData);
                }
                else if ("msexchange".equals(ds)) {
                    ArrayList<HashMap<String, Object>> msExData = this.mapDatasetToHashMap(data);
                    msexchangeCols.addAll(this.getColumnsForTable(msExData));
                    msexchangeRecords.addAll(msExData);
                }
                else if ("sysmon".equals(ds)) {
                    ArrayList<HashMap<String, Object>> sysMonData = this.mapDatasetToHashMap(data);
                    sysmonCols.addAll(this.getColumnsForTable(sysMonData));
                    sysmonRecords.addAll(sysMonData);
                }
                else if ("watchguard".equals(ds)) {
                    ArrayList<HashMap<String, Object>> wgData = this.mapDatasetToHashMap(data);
                    wgtrafficCols.addAll(this.getColumnsForTable(wgData));
                    wgtrafficRecords.addAll(wgData);
                }
                else {
                    ArrayList<HashMap<String, Object>> sepc = this.mapDatasetToHashMap(data);
                    sepcCols.addAll(this.getColumnsForTable(sepc));
                    sepcRecords.addAll(sepc);
                }
            });

            System.out.println("Going to convert now the records from Java structure to Proto records, but before that, let's see the columns");
            System.out.println("Windows columns are " + new HashSet<>(windowsCols));
            System.out.println("MsExchange columns are " + new HashSet<>(msexchangeCols));
            System.out.println("Sysmon columns are " + new HashSet<>(sysmonCols));
            System.out.println("SEPC columns are " + new HashSet<>(sepcCols));
            System.out.println("WgTraffic columns are " + new HashSet<>(wgtrafficCols));

            allTableData.put("windows", windowsRecords);
            allTableData.put("msexchange", msexchangeRecords);
            allTableData.put("sysmon", sysmonRecords);
            allTableData.put("sepc", sepcRecords);
            allTableData.put("watchguard", wgtrafficRecords);

            this.convertToProtoRecords(windowsRecords, wgtrafficRecords, msexchangeRecords, sysmonRecords, sepcRecords);
//            windowsRecords.clear();
//            msexchangeRecords.clear();
//            wgtrafficRecords.clear();
//            sysmonRecords.clear();
//            sepcRecords.clear();

            coreGrpcClient.updateCaseLoadingStatus("Record aggregation and conversion over", CaseSubmissionPayload.getDefaultInstance(), caseId);
        }
    }

    private void loadFromQuery() {
//        System.out.println("Loading from query to be generated");
        // For every query, we search in required tables
        HashMap<String, ArrayList<Map<String, Object>>> datasets = new HashMap<>();

        try {
            Preconditions.checkArgument(this.query != null, "Please set the query by calling setInformationQuery before calling load()");

            Map<String, EntityTypeQuery> query = this.query.getQueryMap();
            Set<String> keys = query.keySet();

            Set<String> tables = this.dataToQuery.keySet();
            for (String table : tables) {
                System.out.println("Querying table " + table);
                coreGrpcClient.updateCaseLoadingStatus(String.format("Querying table %s", table), CaseSubmissionPayload.getDefaultInstance(), caseId);

                List<String> tableCols = this.dataToQuery.get(table);

                HashMap<String, ArrayList<String>> columnFilters = new HashMap<>();
                for (String nodeLabel : keys) {
//                    System.out.println("Querying above table for label " + nodeLabel);

                    EntityTypeQuery q = query.get(nodeLabel);

                    List<EntityQuery> queries = q.getEntityQueryList();
                    ArrayList<String> filterValues = new ArrayList<>();
                    for (EntityQuery entityQuery : queries) {
//                        System.out.println("For value as " + entityQuery.getValue());
                        filterValues.add(entityQuery.getValue());
                    }

                    List<String> colsForCombo = this.labelTableMapping.get(nodeLabel).get(table);
                    for (String col : colsForCombo) {
                        System.out.println("Column filter being used as " + col + " and value " + filterValues);
                        columnFilters.put(col, filterValues);
                    }
//                switch (key) {
//                    case "IP":
//                        columnFilters.put("src_id", filterValues);
//                        columnFilters.put("dst_ip", filterValues);
//                        break;
//                    case "user":
//                        columnFilters.put("src_user_name", filterValues);
//                        columnFilters.put("dst_user_name", new ArrayList<>());
//                        break;
//                    case "host":
//                        columnFilters.put("src_host", filterValues);
//                        columnFilters.put("dst_host", filterValues);
//                        break;
//                    default:
//                        throw new NotActiveException("Not implemented any label filter except IP/user/host but found " + key);
//                }
                }
//                System.out.println("Before calling DataGenerator, the columnFilters");
//                System.out.println(columnFilters);
                DataGenerator generator = new DataGenerator(table, new ArrayList<>(tableCols), snowflakeQueryService,
                        columnFilters, this.TIME_FILTER, this.LEVEL, this.timeFilter.get(table));
                generator.setCoreClient(coreGrpcClient);
                generator.setSetCaseId(caseId);
                generator.generate();
                datasets.put(table, generator.getDataset());

                coreGrpcClient.updateCaseLoadingStatus(String.format("Extracted table %s (Size: %s)", table, generator.getDataset().size()), CaseSubmissionPayload.getDefaultInstance(), caseId);
            }
            this.status = true;
        } catch (Exception e) {
            e.printStackTrace();
            this.status = false;
        }

        if (this.status) {
            final StringBuilder statusBuilder = new StringBuilder("Aggregating records ");

            System.out.println("=============================================");
            System.out.println("generated the datasets by executing the respective queries and are as follows");
            datasets.forEach( (tbl, data) -> {
                System.out.println("For table " + tbl + " the data as follows");
                System.out.println("Number of rows across levels is " + data.size());
                statusBuilder.append(String.format("DS: %s, Rows: %d ", tbl, data.size()));
                System.out.println("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
            });
            String status = statusBuilder.toString().trim();
            coreGrpcClient.updateCaseLoadingStatus(status, CaseSubmissionPayload.getDefaultInstance(), caseId);

            ArrayList<HashMap<String, Object>> windowsRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> wgtrafficRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> msexchangeRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sysmonRecords = new ArrayList<>();
            ArrayList<HashMap<String, Object>> sepcRecords = new ArrayList<>();

            ArrayList<String> windowsCols = new ArrayList<>();
            ArrayList<String> wgtrafficCols = new ArrayList<>();
            ArrayList<String> msexchangeCols = new ArrayList<>();
            ArrayList<String> sysmonCols = new ArrayList<>();
            ArrayList<String> sepcCols = new ArrayList<>();

            datasets.forEach( (tbl, data) -> {
                System.out.println(String.format("Looping over ds %s dataset", tbl));

                String ds = this.getDataSourceFromTableName(tbl);
                if ("windows".equals(ds)) {
                    ArrayList<HashMap<String, Object>> winData = this.mapDatasetToHashMap(data);
                    windowsCols.addAll(this.getColumnsForTable(winData));
                    windowsRecords.addAll(winData);
                }
                else if ("msexchange".equals(ds)) {
                    ArrayList<HashMap<String, Object>> msExData = this.mapDatasetToHashMap(data);
                    msexchangeCols.addAll(this.getColumnsForTable(msExData));
                    msexchangeRecords.addAll(msExData);
                }
                else if ("sysmon".equals(ds)) {
                    ArrayList<HashMap<String, Object>> sysMonData = this.mapDatasetToHashMap(data);
                    sysmonCols.addAll(this.getColumnsForTable(sysMonData));
                    sysmonRecords.addAll(sysMonData);
                }
                else if ("wgtraffic".equals(ds)) {
                    ArrayList<HashMap<String, Object>> wgData = this.mapDatasetToHashMap(data);
                    wgtrafficCols.addAll(this.getColumnsForTable(wgData));
                    wgtrafficRecords.addAll(wgData);
                }
                else {
                    ArrayList<HashMap<String, Object>> sepc = this.mapDatasetToHashMap(data);
                    sepcCols.addAll(this.getColumnsForTable(sepc));
                    sepcRecords.addAll(sepc);
                }
            });

            System.out.println("Going to convert now the records from Java structure to Proto records, but before that, let's see the columns");
            System.out.println("Windows columns are " + new HashSet<>(windowsCols));
            System.out.println("MsExchange columns are " + new HashSet<>(msexchangeCols));
            System.out.println("Sysmon columns are " + new HashSet<>(sysmonCols));
            System.out.println("SEPC columns are " + new HashSet<>(sepcCols));
            System.out.println("WgTraffic columns are " + new HashSet<>(wgtrafficCols));

            this.convertToProtoRecords(windowsRecords, wgtrafficRecords, msexchangeRecords, sysmonRecords, sepcRecords);

            coreGrpcClient.updateCaseLoadingStatus("Record aggregation and conversion over", CaseSubmissionPayload.getDefaultInstance(), caseId);
        }
    }

    public void load() {
        if (this.dataToQuery == null)
            this.loadFromFileSystem();
        else {
            if (useMultiThreaded)
                this.loadFromQueryInThreads();
            else
                this.loadFromQuery();
        }
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

    public HashMap<String, ArrayList<HashMap<String, Object>>> getAllDatasets() {
        return allTableData;
    }

    public List<WindowsRecord> getWindowsRecords() {
        return windowsRecords;
    }

    public List<WatchGuardRecord> getWatchGuardRecords() {
        return watchGuardRecords;
    }

    public List<MsExchangeRecord> getExchangeRecords() {
        return exchangeRecords;
    }

    public List<SysmonRecord> getSysmonRecords() {
        return sysmonRecords;
    }

    public List<SEPCRecord> getSepcRecords() {
        return sepcRecords;
    }

    public boolean getStatus() {
        return this.status;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }
}
