package com.sstech.graphdb.extractor.utils;

import com.sstech.graphdb.extractor.client.CoreGrpcClient;
import com.sstech.graphdb.grpc.*;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class ConstantsAndUtils {

    static CoreGrpcClient coreGrpcClient;
    static Credentials snowflakeCredentials;

    public static ArrayList<String> valueToSkip = new ArrayList<String>() {{
        add("-"); add(null); add("SYSTEM"); add("system"); add(""); add(" ");
        add("BDLOGWatch2.sstech.internal"); add("NAM12-MW2-obe.outbound.protection.outlook.com");
        add("EXCHSRVRTPA03"); add("EXCHSRVRTPA03"); add("d135953.o.ess.barracudanetworks.com");
        add("fe80::65e6:bfc1:28bb:6757, ff02::fb"); add("fe80::819f:69f6:ffae:90ca%10");
        add("fe80::4295:bdff:fe05:712c"); add("fe80::65e6:bfc1:28bb:6757");
        add("ff02:0:0:0:0:0:1:2"); add("fe80:0:0:0:65e6:bfc1:28bb:6757");
        add("SSTECH_TPA_XTM_525"); add("::1"); add("localhost"); add("127.0.0.1");
        add("destination"); add("hostname"); add("SSTECH_Dallas_XTM5"); add("SSDLWTSIEM.sstech.internal");
        add("noreply@yupptvemails.com"); add("NAM11-BN8-obe.outbound.protection.outlook.com");
        add("confluence@mail-us.atlassian.net"); add("destination"); add("hostname"); add("::"); add("SSTECH_Dallas_M470");
    }};

//    public static HashMap<String, HashMap<String, List<String>>> columnPairsPerLabelDict = new HashMap<String, HashMap<String, List<String>>>() {{
//        put("MS_WIN_SECURITYAUDITING", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("subjectusername", "targetusername"));
//            put("host", Arrays.asList("hostname")); put("ip", Arrays.asList("ipaddress"));
//        }});
//        put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", new HashMap<String, List<String>>() {{
//            put("user_name", Collections.emptyList());
//            put("host", Arrays.asList("hostname")); put("ip", Arrays.asList("sourceaddress", "destaddress"));
//        }});
//        put("MS_WIN_SYSMON", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("user_name"));
//            put("host", Arrays.asList("destinationhostname", "hostname", "sourcehostname"));
//            put("ip", Arrays.asList("destinationip", "sourceip"));
//        }});
//        /* put("MS_EXCH_AGENT", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("recipient"));
//            put("host", Arrays.asList("hostname"));
//            put("ip", Arrays.asList("dst_ip", "src_ip"));
//        }}); */
//        put("MS_EXCH_CONNECTIVITY", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("destination"));
//            put("host", Arrays.asList("hostname"));
//            put("ip", Collections.emptyList());
//        }});
//        put("MS_EXCH_MESSAGETRACKING", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("sender_address", "recipient_address"));
//            put("host", Arrays.asList("client_hostname", "hostname", "server_hostname"));
//            put("ip", Arrays.asList("original_server_ip", "original_client_ip", "client_ip", "server_ip"));
//        }});
//        put("WG_FW_EVENTSALARMS", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("user_name"));
//            put("host", Arrays.asList("syslog_host"));
//            put("ip", Arrays.asList("ip_dst_addr", "ip_src_addr"));
//        }});
//        put("WG_FW_NETWORKTRAFFIC", new HashMap<String, List<String>>() {{
//            put("user_name", Arrays.asList("src_user", "dst_user"));
//            put("host", Arrays.asList("syslog_host"));
//            put("ip", Arrays.asList("ip_dst_addr", "ip_src_addr"));
//        }});
//        put("WG_FW_NETFLOW", new HashMap<String, List<String>>() {{
//            put("user_name", Collections.emptyList());
//            put("host", Collections.emptyList());
//            put("ip", Arrays.asList("ipv4_src_addr", "ipv4_dst_addr", "host"));
//        }});
//        put("SYM_ES_ENDPOINTPROTECTIONCLIENT", new HashMap<String, List<String>>() {{
//            put("user_name",Collections.emptyList());
//            put("host", Arrays.asList("hostname"));
//            put("ip", Collections.emptyList());
//        }});
//        put("SYM_ES_NETWORKPROTECTION", new HashMap<String, List<String>>() {{
//            put("user_name", Collections.emptyList());
//            put("host", Arrays.asList("hostname"));
//            put("ip", Collections.emptyList());
//        }});
//    }};
//
//    public static HashMap<String, HashMap<String, List<String>>> nodeTypeToTableMappings = new HashMap<String, HashMap<String, List<String>>>() {{
//        put("host", new HashMap<String, List<String>>() {{
//            put("MS_WIN_SECURITYAUDITING", Arrays.asList("hostname"));
//            put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", Arrays.asList("hostname"));
//            put("MS_WIN_SYSMON", Arrays.asList("destinationhostname", "sourcehostname", "hostname"));
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
//    public static HashMap<String, String> timeFilterColPerTable = new HashMap<String, String>() {{
//        put("MS_WIN_SECURITYAUDITING", "event_time");
//        put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", "event_time");
//        put("MS_WIN_SYSMON", "event_time");
//        put("MS_EXCH_CONNECTIVITY", "event_time");
//        put("MS_EXCH_MESSAGETRACKING", "event_time");
//        put("WG_FW_EVENTSALARMS", "syslog_event_datetime");
//        put("WG_FW_NETWORKTRAFFIC", "syslog_event_datetime");
//        put("WG_FW_NETFLOW", "event_time");
//        put("SYM_ES_ENDPOINTPROTECTIONCLIENT", "event_time");
//        put("SYM_ES_NETWORKPROTECTION", "event_time");
//    }};

    public static HashMap<String, HashMap<String, List<String>>> columnPairsPerLabelDict = new HashMap<String, HashMap<String, List<String>>>() {{
        put("MS_WIN_SECURITYAUDITING_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("subjectusername", "targetusername"));
            put("host", Arrays.asList("hostname")); put("ip", Arrays.asList("ipaddress"));
        }});
        put("MS_WIN_SYSMON_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("user"));
            put("host", Arrays.asList("destinationhostname", "hostname", "sourcehostname"));
            put("ip", Arrays.asList("destinationip", "sourceip"));
        }});
        put("MS_EXCH_MESSAGETRACKING_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("sender_address", "recipient_address"));
            put("host", Arrays.asList("client_hostname", /*"hostname", */"server_hostname"));
            put("ip", Arrays.asList("original_server_ip", "original_client_ip", "client_ip", "server_ip"));
        }});
        put("WG_FW_NETWORKTRAFFIC_DEMO", new HashMap<String, List<String>>() {{
            put("user_name", Arrays.asList("src_user", "dst_user"));
            put("host", Arrays.asList("syslog_host"));
            put("ip", Arrays.asList("ip_dst_addr", "ip_src_addr"));
        }});
        put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", new HashMap<String, List<String>>() {{
            put("user_name",Collections.emptyList());
            put("host", Arrays.asList("hostname"));
            put("ip", Collections.emptyList());
        }});
    }};

    public static HashMap<String, HashMap<String, List<String>>> nodeTypeToTableMappings = new HashMap<String, HashMap<String, List<String>>>() {{
        put("host", new HashMap<String, List<String>>() {{
            put("MS_WIN_SECURITYAUDITING_DEMO", Arrays.asList("hostname"));
            put("MS_WIN_SYSMON_DEMO", Arrays.asList("destinationhostname", "sourcehostname", "hostname"));
            put("MS_EXCH_MESSAGETRACKING_DEMO", Arrays.asList("client_hostname", "server_hostname"/*, "hostname"*/));
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

//    public static HashMap<String, String> timeFilterColPerTable = new HashMap<String, String>() {{
//        put("MS_WIN_SECURITYAUDITING_DEMO", "event_time");
//        put("MS_WIN_SYSMON_DEMO", "event_time");
//        put("MS_EXCH_MESSAGETRACKING_DEMO", "event_time");
//        put("WG_FW_NETWORKTRAFFIC_DEMO", "syslog_event_datetime");
//        put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", "event_time");
//    }};

    public static HashMap<String, String> timeFilterColPerTable = new HashMap<String, String>() {{
        put("MS_WIN_SECURITYAUDITING_DEMO", "eventtime");
        put("MS_WIN_SYSMON_DEMO", "eventtime");
        put("MS_EXCH_MESSAGETRACKING_DEMO", "datetime");
        put("WG_FW_NETWORKTRAFFIC_DEMO", "timestamp");
        put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", "eventtime");
    }};

    private static ArrayList<SimpleDateFormat> EVENT_DATE_FORMATS  = new ArrayList<SimpleDateFormat>(){
        {
            add(new SimpleDateFormat("yyyy-MM-dd' 'HH:mm:ss"));
            add(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss"));
            add(new SimpleDateFormat("yyyy-MM-dd' 'HH:mm:ssXXX"));
            add(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX"));
            add(new SimpleDateFormat("yyyy-MM-dd' 'HH:mm:ss'Z'"));
            add(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'"));
            add(new SimpleDateFormat("yyyy-MM-dd't'HH:mm:ss"));
            add(new SimpleDateFormat("EEE MMM dd HH:mm:ss zzz yyyy"));
            add(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX"));
        }};

    public static Date parseDate(String dateString) {
        Optional<Date> returnDate = Optional.empty();

        for (int i = 0; i < EVENT_DATE_FORMATS.size(); i++) {
            SimpleDateFormat format = EVENT_DATE_FORMATS.get(i);
            try {
                returnDate = Optional.of(format.parse(dateString));
                i = EVENT_DATE_FORMATS.size();
//                System.out.println(String.format("Parsed date: %s $dateString with %s.", dateString, format.toPattern()));
            } catch (ParseException e) {
//                System.out.println(String.format("Error parsing date: %s $dateString with %s.", dateString, format.toPattern()));
                continue;
            }
        }

        return returnDate.orElseGet(Date::new);
    }

    public static void putCoreGrpcClient(CoreGrpcClient client) {
        coreGrpcClient = client;
    }

    public static CoreGrpcClient getCoreGrpcClient() {
        return coreGrpcClient;
    }

    public static void putSnowFlakeCredentials (Credentials credentials) {
        snowflakeCredentials = credentials;
    }

    public static Credentials getSnowflakeCredentials() {
        return snowflakeCredentials;
    }

    public static Date timestampToDate(String timestamp) {
        if (timestamp.charAt(timestamp.length() - 1) == 'Z') {
            DateTimeFormatter inputFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.ENGLISH);
            DateTimeFormatter outputFormatter = DateTimeFormatter.ofPattern("dd-MM-yyy HH:mm:ss", Locale.ENGLISH);
            LocalDateTime date = LocalDateTime.parse(timestamp, inputFormatter);
            String formattedDate = date.format(outputFormatter);
            SimpleDateFormat format = new SimpleDateFormat("dd-MM-yyy HH:mm:ss");

            try {
                long ts = format.parse(formattedDate).getTime();
                return new Date(ts);
            } catch (ParseException e) {
                return new Date();
            }
        } else {
            try{
                long ts = Long.parseLong(timestamp);
                return new Date(ts);
            } catch (Exception e) {
                return new Date();
            }
        }
    }

    public static Time convertJavaTimeToProtoTime(LocalDateTime time) {
        Time.Builder tBuilder = Time.newBuilder();
        tBuilder.setYear(time.getYear());
        tBuilder.setMonth(time.getMonth().getValue());
        tBuilder.setDay(time.getDayOfMonth());
        tBuilder.setHour(time.getHour());
        tBuilder.setMinutes(time.getMinute());
        tBuilder.setSeconds(time.getSecond());
        return tBuilder.build();
    }

    public static CaseInformation convertCaseSubmissionPayloadToCaseInformation(CaseSubmissionPayload caseInfo) {
        ArrayList<ConditionalHosts> hosts = new ArrayList<>();
        ArrayList<ConditionalURLs> urls = new ArrayList<>();
        ArrayList<ConditionalUsers> users = new ArrayList<>();
        ArrayList<ConditionalIPs> ips = new ArrayList<>();

        Time startTime = caseInfo.getStartDate();
        Time endTime = caseInfo.getEndDate();

        caseInfo.getQueryMap().forEach( (label, queryForLabel) -> {
            System.out.println(String.format("Iterating for label %s", label));

            List<EntityQuery> entityTypeQuery = queryForLabel.getEntityQueryList();

            entityTypeQuery.forEach( entityQuery -> {

                switch (label) {
                    case "IP": {
                        System.out.println(String.format("For label %s the value being added is %s ", label, entityQuery.getValue()));
                        ConditionalIPs obj = ConditionalIPs.newBuilder().setIP(entityQuery.getValue()).setStartTime(startTime).setEndTime(endTime).build();
                        ips.add(obj);
                        break;
                    }
                    case "user": {
                        System.out.println(String.format("For label %s the value being added is %s ", label, entityQuery.getValue()));
                        ConditionalUsers obj = ConditionalUsers.newBuilder().setUSER(entityQuery.getValue()).setStartTime(startTime).setEndTime(endTime).build();
                        users.add(obj);
                        break;
                    }
                    case "host": {
                        System.out.println(String.format("For label %s the value being added is %s ", label, entityQuery.getValue()));
                        ConditionalHosts obj = ConditionalHosts.newBuilder().setHOST(entityQuery.getValue()).setStartTime(startTime).setEndTime(endTime).build();
                        hosts.add(obj);
                        break;
                    }
                    case "URL": {
                        System.out.println(String.format("For label %s the value being added is %s ", label, entityQuery.getValue()));
                        ConditionalURLs obj = ConditionalURLs.newBuilder().setURL(entityQuery.getValue()).setStartTime(startTime).setEndTime(endTime).build();
                        urls.add(obj);
                        break;
                    }
                    default:
                        throw new IllegalArgumentException("Expecting label for either URL/host/user/IP for " + label);
                }
            });
        });

        CaseInformation info = CaseInformation.newBuilder().
                addAllIPs(ips).
                addAllHosts(hosts).
                addAllUrls(urls).
                addAllUsers(users).
                build();

        return info;
    }

    public static CaseLoadingProperties convertIncomingQueryToProtoProperties(CaseSubmissionPayload query, String caseId) {
        Map<String, EntityTypeQuery> queryMap = query.getQueryMap();

        Time startTime = query.getStartDate();
        Time endTime = query.getEndDate();
        List<String> dataSources = query.getDataSourcesList();

        Set<String> nodeLabels = queryMap.keySet();
        ArrayList<HashMap<String, String>> queryToInsert = new ArrayList<>();
        for (String nodeLabel : nodeLabels) {
            String label;
            switch (nodeLabel) {
                case "IP": label = "ip"; break;
                case "user": label = "userName"; break;
                default: label = "hostname"; break;
            }
            List<EntityQuery> entityQueries = queryMap.get(nodeLabel).getEntityQueryList();
            for (EntityQuery eq : entityQueries) {
                queryToInsert.add(new HashMap<String, String>(){{
                    put("property_key", label);
                    put("property_value", eq.getValue());
                }});
            }
        }

        ListValue.Builder lb = ListValue.newBuilder();
        for (HashMap<String, String> qi : queryToInsert) {
            String propertyKey = qi.get("property_key");
            String propertyValue = qi.get("property_value");

            HashMap<String, StructureValue> map = new HashMap<String, StructureValue>() {{
                put("propertyKey", StructureValue.newBuilder().setStringValue(propertyKey).build());
                put("propertyValue", StructureValue.newBuilder().setStringValue(propertyValue).build());
            }};

            GenericStructure g = GenericStructure.newBuilder().putAllFields(map).build();
            lb.addValues(StructureValue.newBuilder().setStructValue(g).build());
        }

        StructureValue queryStruct = StructureValue.newBuilder().setListValue(lb.build()).build();

        CaseLoadingProperties ret = CaseLoadingProperties.newBuilder().setCaseId(caseId).putProperty("query", queryStruct).build();

        return ret;
    }

    public static String mapTableColumnNameToProtoColumnName(String tableColumnName, String ds) {
        String protoColumnName;
        switch (ds) {
            case "windows":
                switch (tableColumnName) {
                    case "EVENT_TIME":
                    case "EVENTTIME":
                        protoColumnName = "EventTime";
                        break;
                    case "HOSTNAME":
                        protoColumnName = "Hostname";
                        break;
                    case "EVENT_ID":
                        protoColumnName = "EventID";
                        break;
                    case "PROCESSID":
                        protoColumnName = "ProcessID";
                        break;
                    case "SUBJECTUSERNAME":
                        protoColumnName = "SubjectUserName";
                        break;
                    case "SUBJECTDOMAINNAME":
                        protoColumnName = "SubjectDomainName";
                        break;
                    case "TARGETUSERNAME":
                        protoColumnName = "TargetUserName";
                        break;
                    case "TARGETDOMAINNAME":
                        protoColumnName = "TargetDomainName";
                        break;
                    case "WorkstationName":
                        protoColumnName = "WorkstationName";
                        break;
                    case "PROCESSNAME":
                        protoColumnName = "ProcessName";
                        break;
                    case "IPADDRESS":
                        protoColumnName = "IpAddress";
                        break;
                    case "REMOTEUSERID":
                        protoColumnName = "RemoteUserId";
                        break;
                    case "APPLICATION":
                        protoColumnName = "APPLICATION";
                        break;
                    case "REMOTEMACHINEID":
                        protoColumnName = "RemoteMachineId";
                        break;
                    case "SOURCEADDRESS":
                        protoColumnName = "SourceAddress";
                        break;
                    case "DESTPORT":
                        protoColumnName = "DestPort";
                        break;
                    case "DIRECTION":
                        protoColumnName = "Direction";
                        break;
                    case "PROTOCOL":
                        protoColumnName = "Protocol";
                        break;
                    case "EVENTPROVIDER":
                        protoColumnName = "EventProvider";
                        break;
                    case "LEVEL":
                        protoColumnName = "Level";
                        break;
                    case "DESTADDRESS":
                        protoColumnName = "DestinationAddress";
                        break;
                    case "DATA_FILE_NAME":
                        protoColumnName = "DataFileName";
                        break;
                    case "SOURCEPORT":
                        protoColumnName = "SourcePort";
                        break;
                    default:
                        protoColumnName = tableColumnName;
                        break;
                }
                break;
            case "watchguard":
                switch (tableColumnName) {
                    case "LEVEL":
                        protoColumnName = "level";
                        break;
                    case "SYSLOG_EVENT_DATETIME":
                    case "TIMESTAMP":
                    case "EVENT_TIME":
                        protoColumnName = "timestamp";
                        break;
                    case "IP_SRC_ADDR":
                    case "IPV4_SRC_ADDR":
                        protoColumnName = "ip_src_addr";
                        break;
                    case "IP_SRC_PORT":
                        protoColumnName = "ip_src_port";
                        break;
                    case "IP_DST_ADDR":
                    case "IPV4_DST_ADDR":
                        protoColumnName = "ip_dst_addr";
                        break;
                    case "IP_DST_PORT":
                        protoColumnName = "ip_dst_port";
                        break;
                    case "IN_BYTES":
                    case "RCVD_BYTES":
                        protoColumnName = "rcvd_bytes";
                        break;
                    case "OUT_BYTES":
                    case "SENT_BYTES":
                        protoColumnName = "sent_bytes";
                        break;
                    case "DST_USER":
                        protoColumnName = "dst_user";
                        break;
                    case "DSTNAME":
                        protoColumnName = "dstname";
                        break;
                    case "ARG":
                        protoColumnName = "arg";
                        break;
                    case "FILENAME":
                        protoColumnName = "fileName";
                        break;
                    case "PATH":
                        protoColumnName = "filePath";
                        break;
                    case "SRC_USER":
                        protoColumnName = "src_user";
                        break;
                    case "DURATION":
                    case "ELAPSED_TIME":
                        protoColumnName = "duration";
                        break;
                    case "METHOD":
                        protoColumnName = "op";
                        break;
                    default:
                        protoColumnName = tableColumnName;
                        break;
                }
                break;
            case "msexchange":
                switch (tableColumnName) {
                    case "EVENT_TIME":
                    case "DATETIME":
                        protoColumnName = "datetime";
                        break;
                    case "CLIENT_IP":
                    case "DST_IP":
                        protoColumnName = "client_ip";
                        break;
                    case "CLIENT_HOSTNAME":
                        protoColumnName = "client_hostname";
                        break;
                    case "SERVER_IP":
                    case "SRC_IP":
                        protoColumnName = "server_ip";
                        break;
                    case "SERVER_HOSTNAME":
                        protoColumnName = "server_hostname";
                        break;
                    case "LEVEL":
                        protoColumnName = "level";
                        break;
                    case "EVENT_ID":
                        protoColumnName = "event_id";
                        break;
                    case "RECIPIENT_ADDRESS":
                    case "RECIPIENT":
                        protoColumnName = "recipient_address";
                        break;
                    case "TOTAL_BYTES":
                        protoColumnName = "total_bytes";
                        break;
                    case "MESSAGE_SUBJECT":
                        protoColumnName = "message_subject";
                        break;
                    case "SENDER_ADDRESS":
                        protoColumnName = "sender_address";
                        break;
                    case "DIRECTIONALITY":
                        protoColumnName = "directionality";
                        break;
                    case "ORIGINAL_CLIENT_IP":
                        protoColumnName = "original_client_ip";
                        break;
                    case "ORIGINAL_SERVER_IP":
                        protoColumnName = "original_server_ip";
                        break;
                    case "HOSTNAME":
                        protoColumnName = "hostname";
                        break;
                    default:
                        protoColumnName = tableColumnName;
                }
                break;
            case "sysmon":
                switch (tableColumnName) {
                    case "EVENT_TIME":
                    case "EVENTTIME":
                        protoColumnName = "EventTime";
                        break;
                    case "HOSTNAME":
                        protoColumnName = "Hostname";
                        break;
                    case "EVENT_ID":
                        protoColumnName = "EventID";
                        break;
                    case "PROCESSID":
                        protoColumnName = "ProcessID";
                        break;
                    case "IMAGE":
                        protoColumnName = "Image";
                        break;
                    case "USER_NAME":
                    case "USER":
                        protoColumnName = "User";
                        break;
                    case "PROTOCOL":
                        protoColumnName = "Protocol";
                        break;
                    case "SOURCEIP":
                        protoColumnName = "SourceIp";
                        break;
                    case "SOURCEHOSTNAME":
                        protoColumnName = "SourceHostname";
                        break;
                    case "SOURCEPORT":
                        protoColumnName = "SourcePort";
                        break;
                    case "DESTINATIONIP":
                        protoColumnName = "DestinationIp";
                        break;
                    case "DESTINATIONHOSTNAME":
                        protoColumnName = "DestinationHostname";
                        break;
                    case "DESTINATIONPORT":
                        protoColumnName = "DestinationPort";
                        break;
                    case "COMMANDLINE":
                        protoColumnName = "CommandLine";
                        break;
                    case "PARENTIMAGE":
                        protoColumnName = "ParentImage";
                        break;
                    case "TARGETFILENAME":
                        protoColumnName = "TargetFilename";
                        break;
                    default:
                        protoColumnName = tableColumnName;
                        break;
                }
                break;
            case "sepc":
                switch (tableColumnName) {
                    case "EVENT_TIME":
                        protoColumnName = "EventTime";
                        break;
                    case "HOSTNAME":
                        protoColumnName = "Hostname";
                        break;
                    case "EVENT_ID":
                        protoColumnName = "EventID";
                        break;
                    case "NUM_OMITTED":
                        protoColumnName = "NumOmitted";
                        break;
                    case "SIZE":
                        protoColumnName = "size";
                        break;
                    case "EVENTPROVIDER":
                        protoColumnName = "EventProvider";
                        break;
                    case "LEVEL":
                        protoColumnName = "Level";
                        break;
                    case "FILE_PATH":
                        protoColumnName = "FilePath";
                        break;
                    case "ACTION_DESC":
                        protoColumnName = "ActionDesc";
                        break;
                    case "NUM_RISKS":
                        protoColumnName = "NumRisks";
                        break;
                    case "NUM_SKIPPED":
                        protoColumnName = "NumSkipped";
                        break;
                    case "NUM_SCANNED":
                        protoColumnName = "NumScanned";
                        break;
                    case "DATA_FILE_NAME":
                        protoColumnName = "DataFileName";
                        break;
                    case "SOURCE":
                        protoColumnName = "Source";
                        break;
                    default:
                        protoColumnName = tableColumnName;
                        break;
                }
                break;
            default:
                protoColumnName = tableColumnName;
                break;
        }
        return protoColumnName;
    }

    public static WindowsRecord.Builder addToWindowsRecord(WindowsRecord.Builder builder , String key, Object value)  {
        if (value == null)
            return builder;
        //WindowsRecord wr = null;
        if(key.contentEquals("EVENT_TIME")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("HOSTNAME")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("EVENT_ID")) {
            try {
                builder.setEventID(Long.valueOf((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in windows", key, value.getClass(), value));
            }
        }
        else if(key.equals("PROCESSID")) {
            try {
                builder.setProcessID(Long.valueOf((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in windows", key, value.getClass(), value));
            }
        }
        else if(key.equals("SUBJECTUSERNAME")) {
            builder.setSubjectUserName((String) value);
        }
        else if(key.equals("SUBJECTDOMAINNAME")) {
            builder.setSubjectDomainName((String) value);
        }
        else if(key.equals("TARGETUSERNAME")) {
            builder.setTargetUserName((String) value);
        }
        else if(key.equals("TARGETDOMAINNAME")) {
            builder.setTargetDomainName((String) value);
        }
        else if(key.equals("WorkstationName")) {
            builder.setWorkstationName((String) value);
        }
        else if(key.equals("PROCESSNAME")) {
            builder.setProcessName((String) value);
        }
        else if(key.equals("IPADDRESS")) {
            builder.setIpAddress((String) value);
        }
        else if(key.equals("REMOTEUSERID")) {
            builder.setRemoteUserId((String) value);
        }
        else if(key.equals("APPLICATION")) {
            builder.setApplication((String) value);
        }
        else if(key.equals("REMOTEMACHINEID")) {
            builder.setRemoteMachineId((String) value);
        }
        else if(key.equals("SOURCEADDRESS")) {
            builder.setSourceAddress((String) value);
        }
        else if(key.equals("DESTPORT")) {
            try {
                builder.setDestPort(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in windows", key, value.getClass(), value));
            }
        }
        else if(key.equals("DIRECTION")) {
            builder.setDirection((String) value);
        }
        else if(key.equals("PROTOCOL")) {
            builder.setProtocol((String) value);
        }
        else if(key.equals("EVENTPROVIDER")) {
            builder.setEventProvider((String) value);
        }
        else if(key.equals("LEVEL")) {
            try {
                builder.setLevel(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in windows", key, value.getClass(), value));
            }
        }
        else if(key.equals("DESTADDRESS")) {
            builder.setDestinationAddress((String) value);
        }
        else if(key.equals("DATA_FILE_NAME")) {
            builder.setDataFileName((String) value);
        }
        else if(key.equals("SOURCEPORT")) {
            try {
                builder.setSourcePort(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in windows", key, value.getClass(), value));
            }
        }
        return builder;
    }

    public static WindowsRecord.Builder addToWindowsRecord_old(WindowsRecord.Builder builder , String key, Object value)  {
        //WindowsRecord wr = null;
        if(key.contentEquals("EventTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("Hostname")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("Keywords")) {
            try {
                builder.setKeywords((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Keywords in win");
            }
        }
        else if(key.equals("EventType")) {
            builder.setEventType((String) value);
        }
        else if(key.equals("SeverityValue")) {
            try {
                builder.setSeverityValue((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast SeverityValue in win");
            }
        }
        else if(key.equals("Severity")) {
            builder.setSeverity((String) value);
        }
        else if(key.equals("EventID")) {
            try {
                builder.setEventID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast eventid in win");
            }
        }
        else if(key.equals("SourceName")) {
            builder.setSourceName((String) value);
        }
        else if(key.equals("ProviderGuid")) {
            builder.setProviderGuid((String) value);
        }
        else if(key.equals("Version")) {
            try {
                builder.setVersion((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Version in win");
            }
        }
        else if(key.equals("Task")) {
            try {
                builder.setTask((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Task in win");
            }
        }
        else if(key.equals("OpcodeValue")) {
            try {
                builder.setOpcodeValue((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast OpcodeValue in win");
            }
        }
        else if(key.equals("RecordNumber")) {
            try {
                builder.setRecordNumber((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast RecordNumber in win");
            }
        }
        else if(key.equals("ProcessID")) {
            try {
                builder.setProcessID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ProcessID in win");
            }
        }
        else if(key.equals("ThreadID")) {
            try {
                builder.setThreadID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ThreadID in win");
            }
        }
        else if(key.equals("Channel")) {
            builder.setChannel((String) value);
        }
        else if(key.equals("Message")) {
            builder.setMessage((String) value);
        }
        else if(key.equals("Category")) {
            builder.setCategory((String) value);
        }
        else if(key.equals("Opcode")) {
            builder.setOpcode((String) value);
        }
        else if(key.equals("SubjectUserSid")) {
            builder.setSubjectUserSid((String) value);
        }
        else if(key.equals("SubjectUserName")) {
            builder.setSubjectUserName((String) value);
        }
        else if(key.equals("SubjectDomainName")) {
            builder.setSubjectDomainName((String) value);
        }
        else if(key.equals("SubjectLogonId")) {
            builder.setSubjectLogonId((String) value);
        }
        else if(key.equals("TargetUserSid")) {
            builder.setTargetSid((String) value);
        }
        else if(key.equals("TargetUserName")) {
            builder.setTargetUserName((String) value);
        }
        else if(key.equals("TargetDomainName")) {
            builder.setTargetDomainName((String) value);
        }
        else if(key.equals("TargetLogonId")) {
            builder.setTargetLogonId((String) value);
        }
        else if(key.equals("LogonType")) {
            builder.setLogonType((String) value);
        }
        else if(key.equals("LogonProcessName")) {
            builder.setLogonProcessName((String) value);
        }
        else if(key.equals("AuthenticationPackageName")) {
            builder.setAuthenticationPackageName((String) value);
        }
        else if(key.equals("WorkstationName")) {
            builder.setWorkstationName((String) value);
        }
        else if(key.equals("LogonGuid")) {
            builder.setLogonGuid((String) value);
        }
        else if(key.equals("TransmittedServices")) {
            builder.setTransmittedServices((String) value);
        }
        else if(key.equals("LmPackageName")) {
            builder.setLmPackageName((String) value);
        }
        else if(key.equals("KeyLength")) {
            builder.setKeyLength((String) value);
        }
        else if(key.equals("ProcessName")) {
            builder.setProcessName((String) value);
        }
        else if(key.equals("IpAddress")) {
            builder.setIpAddress((String) value);
        }
        else if(key.equals("IpPort")) {
            builder.setIpPort((String) value);
        }
        else if(key.equals("EventReceivedTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventReceivedTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.equals("SourceModuleName")) {
            builder.setSourceModuleName((String) value);
        }
        else if(key.equals("SourceModuleType")) {
            builder.setSourceModuleType((String) value);
        }
        else if(key.equals("ObjectServer")) {
            builder.setObjectServer((String) value);
        }
        else if(key.equals("ObjectType")) {
            builder.setObjectType((String) value);
        }
        else if(key.equals("ObjectName")) {
            builder.setObjectName((String) value);
        }
        else if(key.equals("HandleId")) {
            builder.setHandleId((String) value);
        }
        else if(key.equals("AccessMask")) {
            builder.setAccessMask((String) value);
        }
        else if(key.equals("PrivilegeList")) {
            builder.setPrivilegeList((String) value);
        }
        else if(key.equals("ActivityID")) {
            builder.setActivityID((String) value);
        }
        else if(key.equals("ImpersonationLevel")) {
            builder.setImpersonationLevel((String) value);
        }
        else if(key.equals("RestrictedAdminMode")) {
            builder.setRestrictedAdminMode((String) value);
        }
        else if(key.equals("TargetOutboundUserName")) {
            builder.setTargetOutboundUserName((String) value);
        }
        else if(key.equals("TargetOutboundDomainName")) {
            builder.setTargetOutboundDomainName((String) value);
        }
        else if(key.equals("VirtualAccount")) {
            builder.setVirtualAccount((String) value);
        }
        else if(key.equals("TargetLinkedLogonId")) {
            builder.setTargetLinkedLogonId((String) value);
        }
        else if(key.equals("ElevatedToken")) {
            builder.setElevatedToken((String) value);
        }
        else if(key.equals("TargetSid")) {
            builder.setTargetSid((String) value);
        }
        else if(key.equals("MemberName")) {
            builder.setMemberName((String) value);
        }
        else if(key.equals("MemberSid")) {
            builder.setMemberSid((String) value);
        }
        else if(key.equals("SamAccountName")) {
            builder.setSamAccountName((String) value);
        }
        else if(key.equals("DisplayName")) {
            builder.setDisplayName((String) value);
        }
        else if(key.equals("UserPrincipalName")) {
            builder.setUserPrincipalName((String) value);
        }
        else if(key.equals("HomeDirectory")) {
            builder.setHomeDirectory((String) value);
        }
        else if(key.equals("HomePath")) {
            builder.setHomePath((String) value);
        }
        else if(key.equals("ScriptPath")) {
            builder.setScriptPath((String) value);
        }
        else if(key.equals("ProfilePath")) {
            builder.setProfilePath((String) value);
        }
        else if(key.equals("UserWorkstations")) {
            builder.setUserWorkstations((String) value);
        }
        else if(key.equals("PasswordLastSet")) {
            builder.setPasswordLastSet((String) value);
        }
        else if(key.equals("AccountExpires")) {
            builder.setAccountExpires((String) value);
        }
        else if(key.equals("PrimaryGroupId")) {
            builder.setPrimaryGroupId((String) value);
        }
        else if(key.equals("AllowedToDelegateTo")) {
            builder.setAllowedToDelegateTo((String) value);
        }
        else if(key.equals("OldUacValue")) {
            builder.setOldUacValue((String) value);
        }
        else if(key.equals("NewUacValue")) {
            builder.setNewUacValue((String) value);
        }
        else if(key.equals("UserAccountControl")) {
            builder.setUserAccountControl((String) value);
        }
        else if(key.equals("UserParameters")) {
            builder.setUserParameters((String) value);
        }
        else if(key.equals("SidHistory")) {
            builder.setSidHistory((String) value);
        }
        else if(key.equals("LogonHours")) {
            builder.setLogonHours((String) value);
        }
        return builder;
    }

    public static WatchGuardRecord.Builder addToWGRecord(WatchGuardRecord.Builder builder , String key, Object value) {
        if (value == null)
            return builder;

        if(key.contentEquals("sid"))
            builder.setSid((String) value);
        else if(key.contentEquals("cluster")) {
            builder.setCluster((String) value);
        }
        else if(key.equals("sn")) {
            builder.setSn((String) value);
        }
        else if(key.equals("messageID")) {
            builder.setMessageID((String) value);
        }
        else if(key.equals("tag_id")) {
            builder.setTagId((String) value);
        }
        else if(key.equals("raw_id")) {
            builder.setRawId((String) value);
        }
        else if(key.equals("disp")) {
            builder.setDisp((String) value);
        }
        else if(key.equals("direction")) {
            builder.setDirection((String) value);
        }
        else if(key.equals("pri")) {
            builder.setPri((String) value);
        }
//        else if(key.equals("DATA_FILE_NAME")) {
//            builder.setDataFileName((String) value);
//        }
//        else if(key.equals("PATH")) {
//            builder.setPath((String) value);
//        }
//        else if(key.equals("SYSLOG_HOST")) {
//            builder.setHostname((String) value);
//        }
//        else if(key.equals("FILENAME")) {
//            builder.setFileName((String) value);
//        }
        else if(key.equals("SYSLOG_EVENT_DATETIME")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setTimestamp(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.equals("policy")) {
            builder.setPolicy((String) value);
        }
        else if(key.equals("protocol")) {
            builder.setProtocol((String) value);
        }
        else if(key.equals("IP_SRC_ADDR")) {
            builder.setIpSrcAddr((String) value);
        }
        else if(key.equals("IP_SRC_PORT")) {
            builder.setIpSrcPort((String) value);
        }
        else if(key.equals("IP_DST_ADDR")) {
            builder.setIpDstAddr((String) value);
        }
        else if(key.equals("IP_DST_PORT")) {
            builder.setIpDstPort((String) value);
        }
        else if(key.equals("src_ip_nat")) {
            builder.setSrcIpNat((String) value);
        }
        else if(key.equals("src_port_nat")) {
            builder.setSrcPortNat((String) value);
        }
        else if(key.equals("dst_ip_nat")) {
            builder.setDstIpNat((String) value);
        }
        else if(key.equals("dst_port_nat")) {
            builder.setDstPortNat((String) value);
        }
        else if(key.equals("src_intf")) {
            builder.setSrcIntf((String) value);
        }
        else if(key.equals("dst_intf")) {
            builder.setDstIntf((String) value);
        }
        else if(key.equals("rc")) {
            builder.setRc((String) value);
        }
        else if(key.equals("pckt_len")) {
            builder.setPcktLen((String) value);
        }
        else if(key.equals("ttl")) {
            builder.setTtl((String) value);
        }
        else if(key.equals("pr_info")) {
            builder.setPrInfo((String) value);
        }
        else if(key.equals("proxy_act")) {
            builder.setProxyAct((String) value);
        }
        else if(key.equals("alarm_name")) {
            builder.setAlarmName((String) value);
        }
        else if(key.equals("alarm_type")) {
            builder.setAlarmType((String) value);
        }
        else if(key.equals("alarm_id")) {
            builder.setAlarmId((String) value);
        }
        else if(key.equals("IN_BYTES")) {
            builder.setRcvdBytes((String) value);
        }
        else if(key.equals("OUT_BYTES")) {
            builder.setSentBytes((String) value);
        }
        else if(key.equals("DST_USER")) {
            builder.setDstUser((String) value);
        }
        else if(key.equals("DSTNAME")) {
            builder.setDstname((String) value);
        }
        else if(key.equals("ARG")) {
            builder.setArg((String) value);
        }
        else if(key.equals("property35")) {
            builder.setProperty35((String) value);
        }
        else if(key.equals("property36")) {
            builder.setProperty36((String) value);
        }
        else if(key.equals("property37")) {
            builder.setProperty37((String) value);
        }
        else if(key.equals("property38")) {
            builder.setProperty38((String) value);
        }
        else if(key.equals("property39")) {
            builder.setProperty39((String) value);
        }
        else if(key.equals("property40")) {
            builder.setProperty40((String) value);
        }
        else if(key.equals("log_type")) {
            builder.setLogType((String) value);
        }
        else if(key.equals("msg")) {
            builder.setMsg((String) value);
        }
        else if(key.equals("geo_src")) {
            builder.setGeoSrc((String) value);
        }
        else if(key.equals("SRC_USER")) {
            builder.setSrcUser((String) value);
        }
        else if(key.equals("op")) {
            builder.setOp((String) value);
        }
        else if(key.equals("geo_dst")) {
            builder.setGeoDst((String) value);
        }
        else if(key.equals("DURATION")) {
            builder.setDuration((String) value);
        }
        return builder;
    }

    public static MsExchangeRecord.Builder addToExchangeRecord(MsExchangeRecord.Builder builder , String key, Object value) {
        if (value == null)
            return builder;

        if(key.equals("EVENT_TIME")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setDatetime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("CLIENT_IP")) {
            builder.setClientIp((String) value);
        }
        else if(key.contentEquals("DST_IP")) {
            builder.setClientIp((String) value);
        }
        else if(key.equals("CLIENT_HOSTNAME")) {
            builder.setClientHostname((String) value);
        }
        else if(key.equals("SERVER_IP")) {
            builder.setServerIp((String) value);
        }
        else if(key.equals("SRC_IP")) {
            builder.setServerIp((String) value);
        }
        else if(key.equals("SERVER_HOSTNAME")) {
            builder.setServerHostname((String) value);
        }
        else if(key.equals("LEVEL")) {
            try {
                builder.setLevel(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in msexchange", key, value.getClass(), value));
            }
        }
        else if(key.equals("EVENT_ID")) {
            builder.setEventId((String) value);
        }
        else if(key.equals("RECIPIENT_ADDRESS")) {
            builder.setRecipientAddress((String) value);
        }
        else if(key.equals("RECIPIENT")) {
            builder.setRecipientAddress((String) value);
        }
        else if(key.equals("TOTAL_BYTES")) {
            builder.setTotalBytes((String) value);
        }
        else if(key.equals("MESSAGE_SUBJECT")) {
            builder.setMessageSubject((String) value);
        }
        else if(key.equals("SENDER_ADDRESS")) {
            builder.setSenderAddress((String) value);
        }
        else if(key.equals("DIRECTIONALITY")) {
            builder.setDirectionality((String) value);
        }
        else if(key.equals("ORIGINAL_CLIENT_IP")) {
            builder.setOriginalClientIp((String) value);
        }
        else if(key.equals("ORIGINAL_SERVER_IP")) {
            builder.setOriginalServerIp((String) value);
        }
        else if(key.equals("HOSTNAME")) {
            builder.setHostname((String) value);
        }
        return builder;
    }

    public static MsExchangeRecord.Builder addToExchangeRecord_old(MsExchangeRecord.Builder builder , String key, Object value) {
        if(key.equals("datetime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setDatetime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("client_ip")) {
            builder.setClientIp((String) value);
        }
        else if(key.equals("client_hostname")) {
            builder.setClientHostname((String) value);
        }
        else if(key.equals("server_ip")) {
            builder.setServerIp((String) value);
        }
        else if(key.equals("server_hostname")) {
            builder.setServerHostname((String) value);
        }
        else if(key.equals("source_context")) {
            builder.setSourceContext((String) value);
        }
        else if(key.equals("connector_id")) {
            builder.setConnectorId((String) value);
        }
        else if(key.equals("source")) {
            builder.setSource((String) value);
        }
        else if(key.equals("event_id")) {
            builder.setEventId((String) value);
        }
        else if(key.equals("internal_message_id")) {
            builder.setInternalMessageId((String) value);
        }
        else if(key.equals("message_id")) {
            builder.setMessageId((String) value);
        }
        else if(key.equals("recipient_address")) {
            builder.setRecipientAddress((String) value);
        }
        else if(key.equals("recipient_status")) {
            builder.setRecipientStatus((String) value);
        }
        else if(key.equals("total_bytes")) {
            builder.setTotalBytes((String) value);
        }
        else if(key.equals("recipient_count")) {
            builder.setRecipientCount((String) value);
        }
        else if(key.equals("related_recipient_address")) {
            builder.setRelatedRecipientAddress((String) value);
        }
        else if(key.equals("reference")) {
            builder.setReference((String) value);
        }
        else if(key.equals("message_subject")) {
            builder.setMessageSubject((String) value);
        }
        else if(key.equals("sender_address")) {
            builder.setSenderAddress((String) value);
        }
        else if(key.equals("return_path")) {
            builder.setReturnPath((String) value);
        }
        else if(key.equals("message_info")) {
            builder.setMessageInfo((String) value);
        }
        else if(key.equals("directionality")) {
            builder.setDirectionality((String) value);
        }
        else if(key.equals("tenant_id")) {
            builder.setTenantId((String) value);
        }
        else if(key.equals("original_client_ip")) {
            builder.setOriginalClientIp((String) value);
        }
        else if(key.equals("original_server_ip")) {
            builder.setOriginalServerIp((String) value);
        }
        else if(key.equals("custom_data")) {
            builder.setCustomData((String) value);
        }
        return builder;
    }

    public static SysmonRecord.Builder addToSysmonRecord(SysmonRecord.Builder builder , String key, Object value) {
        if (value == null)
            return builder;

        if(key.contentEquals("EVENT_TIME")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("HOSTNAME")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("EVENT_ID")) {
            try {
                builder.setEventID(Long.valueOf((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sysmon", key, value.getClass(), value));
            }
        }
        else if(key.equals("PROCESSID")) {
            try {
                builder.setProcessID(Long.valueOf((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sysmon", key, value.getClass(), value));
            }
        }
        else if(key.equals("IMAGE")) {
            builder.setImage((String) value);
        }
        else if(key.equals("USER_NAME")) {
            builder.setUser((String) value);
        }
        else if(key.equals("PROTOCOL")) {
            builder.setProtocol((String) value);
        }
        else if(key.equals("SOURCEIP")) {
            builder.setSourceIp((String) value);
        }
        else if(key.equals("SOURCEHOSTNAME")) {
            builder.setSourceHostname((String) value);
        }
        else if(key.equals("SOURCEPORT")) {
            builder.setSourcePort((String) value);
        }
        else if(key.equals("DESTINATIONIP")) {
            builder.setDestinationIp((String) value);
        }
        else if(key.equals("DESTINATIONHOSTNAME")) {
            builder.setDestinationHostname((String) value);
        }
        else if(key.equals("DESTINATIONPORT")) {
            builder.setDestinationPort((String) value);
        }
        else if(key.equals("COMMANDLINE")) {
            builder.setCommandLine((String) value);
        }
        else if(key.equals("PARENTIMAGE")) {
            builder.setParentImage((String) value);
        }
        else if(key.equals("TARGETFILENAME")) {
            builder.setTargetFilename((String) value);
        }
        return builder;
    }

    public static SysmonRecord.Builder addToSysmonRecord_old(SysmonRecord.Builder builder , String key, Object value) {
        if(key.contentEquals("EventTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("Hostname")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("Keywords")) {
            try {
                builder.setKeywords((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Keywords in sysmon");
            }
        }
        else if(key.equals("EventType")) {
            builder.setEventType((String) value);
        }
        else if(key.equals("SeverityValue")) {
            try {
                builder.setSeverityValue((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast SeverityValue in sysmon");
            }
        }
        else if(key.equals("Severity")) {
            builder.setSeverity((String) value);
        }
        else if(key.equals("EventID")) {
            try {
                builder.setEventID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast EventID in sysmon");
            }
        }
        else if(key.equals("SourceName")) {
            builder.setSourceName((String) value);
        }
        else if(key.equals("ProviderGuid")) {
            builder.setProviderGuid((String) value);
        }
        else if(key.equals("Version")) {
            try {
                builder.setVersion((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Version in sysmon with value " + value.toString());
            }
        }
        else if(key.equals("Task")) {
            try {
                builder.setTask((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Task in sysmon");
            }
        }
        else if(key.equals("OpcodeValue")) {
            try {
                builder.setOpcodeValue((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast OpcodeValue in sysmon");
            }
        }
        else if(key.equals("RecordNumber")) {
            try {
                builder.setRecordNumber((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast RecordNumber in sysmon");
            }
        }
        else if(key.equals("ProcessID")) {
            try {
                builder.setProcessID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ProcessID in sysmon");
            }
        }
        else if(key.equals("ThreadID")) {
            try {
                builder.setThreadID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ThreadID in Sysmon");
            }
        }
        else if(key.equals("Channel")) {
            builder.setChannel((String) value);
        }
        else if(key.equals("Domain")) {
            builder.setDomain((String) value);
        }
        else if(key.equals("AccountName")) {
            builder.setAccountName((String) value);
        }
        else if(key.equals("UserID")) {
            builder.setUserID((String) value);
        }
        else if(key.equals("AccountType")) {
            builder.setAccountType((String) value);
        }
        else if(key.equals("Message")) {
            builder.setMessage((String) value);
        }
        else if(key.equals("Category")) {
            builder.setCategory((String) value);
        }
        else if(key.equals("Opcode")) {
            builder.setOpcode((String) value);
        }
        else if(key.equals("UtcTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setUtcTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.equals("ProcessGuid")) {
            builder.setProcessGuid((String) value);
        }
        else if(key.equals("Image")) {
            builder.setImage((String) value);
        }
        else if(key.equals("User")) {
            builder.setUser((String) value);
        }
        else if(key.equals("Protocol")) {
            builder.setProtocol((String) value);
        }
        else if(key.equals("Initiated")) {
            builder.setInitiated((String) value);
        }
        else if(key.equals("SourceIsIpv6")) {
            builder.setSourceIsIpv6((String) value);
        }
        else if(key.equals("SourceIp")) {
            builder.setSourceIp((String) value);
        }
        else if(key.equals("LogonGuid")) {
            builder.setLogonGuid((String) value);
        }
        else if(key.equals("SourceHostname")) {
            builder.setSourceHostname((String) value);
        }
        else if(key.equals("SourcePort")) {
            builder.setSourcePort((String) value);
        }
        else if(key.equals("DestinationIsIpv6")) {
            builder.setDestinationIsIpv6((String) value);
        }
        else if(key.equals("DestinationIp")) {
            builder.setDestinationIp((String) value);
        }
        else if(key.equals("DestinationHostname")) {
            builder.setDestinationHostname((String) value);
        }
        else if(key.equals("DestinationPort")) {
            builder.setDestinationPort((String) value);
        }
        else if(key.equals("EventReceivedTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventReceivedTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.equals("SourceModuleName")) {
            builder.setSourceModuleName((String) value);
        }
        else if(key.equals("SourceModuleType")) {
            builder.setSourceModuleType((String) value);
        }
        else if(key.equals("FileVersion")) {
            builder.setFileVersion((String) value);
        }
        else if(key.equals("Description")) {
            builder.setDescription((String) value);
        }
        else if(key.equals("Product")) {
            builder.setProduct((String) value);
        }
        else if(key.equals("Company")) {
            builder.setCompany((String) value);
        }
        else if(key.equals("CommandLine")) {
            builder.setCommandLine((String) value);
        }
        else if(key.equals("CurrentDirectory")) {
            builder.setCurrentDirectory((String) value);
        }
        else if(key.equals("LogonId")) {
            builder.setLogonId((String) value);
        }
        else if(key.equals("TerminalSessionId")) {
            builder.setTerminalSessionId((String) value);
        }
        else if(key.equals("IntegrityLevel")) {
            builder.setIntegrityLevel((String) value);
        }
        else if(key.equals("Hashes")) {
            builder.setHashes((String) value);
        }
        else if(key.equals("ParentProcessGuid")) {
            builder.setParentProcessGuid((String) value);
        }
        else if(key.equals("ParentProcessId")) {
            builder.setParentProcessId((String) value);
        }
        else if(key.equals("ParentImage")) {
            builder.setParentImage((String) value);
        }
        else if(key.equals("ParentCommandLine")) {
            builder.setParentCommandLine((String) value);
        }
        else if(key.equals("TargetFilename")) {
            builder.setTargetFilename((String) value);
        }
        else if(key.equals("CreationUtcTime")) {
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setCreationUtcTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.equals("RuleName")) {
            builder.setRuleName((String) value);
        }
        else if(key.equals("Hash")) {
            builder.setHash((String) value);
        }
        else if(key.equals("DestinationPortName")) {
            builder.setDestinationPortName((String) value);
        }
        return builder;
    }

    public static SEPCRecord.Builder addToSEPCRecord(SEPCRecord.Builder builder , String key, Object value) {
        if (value == null)
            return builder;

        if(key.contentEquals("EVENT_TIME")){
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("HOSTNAME")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("EVENT_ID")) {
            try {
                builder.setEventID(Long.valueOf((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("NUM_OMITTED")) {
            try {
                builder.setNumOmitted(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("SIZE")) {
            try {
                builder.setSize(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("EVENTPROVIDER")) {
            builder.setEventProvider((String) value);
        }
        else if(key.equals("LEVEL")) {
            try {
                builder.setLevel(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("FILE_PATH")) {
            builder.setFilePath((String) value);
        }
        else if(key.equals("ACTION_DESC")) {
            builder.setActionDesc((String) value);
        }
        else if(key.equals("NUM_RISKS")) {
            try {
                builder.setNumRisks(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("NUM_SKIPPED")) {
            try {
                builder.setNumSkipped(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("NUM_SCANNED")) {
            try {
                builder.setNumScanned(Integer.parseInt((String) value));
            } catch (ClassCastException e) {
                System.out.println(String.format("Couldnt cast %s from datatype %s and value %s in sepc", key, value.getClass(), value));
            }
        }
        else if(key.equals("DATA_FILE_NAME")) {
            builder.setDataFileName((String) value);
        }
        else if(key.equals("SOURCE")) {
            builder.setSource((String) value);
        }
        return builder;
    }

    public static SEPCRecord.Builder addToSEPCRecord_old(SEPCRecord.Builder builder , String key, Object value) {
        if(key.contentEquals("EventTime")){
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        else if(key.contentEquals("Hostname")) {
            builder.setHostname((String) value);
        }
        else if(key.equals("Keywords")) {
            try {
                builder.setKeywords((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Keywords in SEPC");
            }
        }
        else if(key.equals("EventType")) {
            builder.setEventType((String) value);
        }
        else if(key.equals("SeverityValue")) {
            try {
                builder.setSeverityValue((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast SeverityValue in SEPC");
            }
        }
        else if(key.equals("Severity")) {
            builder.setSeverity((String) value);
        }
        else if(key.equals("EventID")) {
            try {
                builder.setEventID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast EventID in SEPC");
            }
        }
        else if(key.equals("SourceName")) {
            builder.setSourceName((String) value);
        }
        else if(key.equals("Task")) {
            try {
                builder.setTask((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast Task in SEPC");
            }
        }
        else if(key.equals("RecordNumber")) {
            try {
                builder.setRecordNumber((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast RecordNumber in SEPC");
            }
        }
        else if(key.equals("ProcessID")) {
            try {
                builder.setProcessID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ProcessID in SEPC");
            }
        }
        else if(key.equals("ThreadID")) {
            try {
                builder.setThreadID((Long) value);
            } catch (ClassCastException e) {
                System.out.println("Couldnt cast ThreadID in SEPC");
            }
        }
        else if(key.equals("Channel")) {
            builder.setChannel((String) value);
        }
        else if(key.equals("Message")) {
            builder.setMessage((String) value);
        }
        else if(key.equals("SourceModuleName")) {
            builder.setSourceModuleName((String) value);
        }
        else if(key.equals("SourceModuleType")) {
            builder.setSourceModuleType((String) value);
        }
        else if(key.contentEquals("EventReceivedTime")){
            Date dt = ConstantsAndUtils.parseDate((String) value);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(dt);
            builder.setEventReceivedTime(
                    Time.newBuilder().
                            setDay(calendar.get(Calendar.DAY_OF_MONTH)).
                            setHour(calendar.get(Calendar.HOUR_OF_DAY)).
                            setMinutes(calendar.get(Calendar.MINUTE)).
                            setMonth(calendar.get(Calendar.MONTH)).
                            setYear(calendar.get(Calendar.YEAR)).
                            setSeconds(calendar.get(Calendar.SECOND)).
                            build()
            );
        }
        return builder;
    }
}
