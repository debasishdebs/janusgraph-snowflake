package com.sstech.graphdb.extractor.server;

import com.elysum.springboot.service.SnowflakeQueryService;
import com.google.protobuf.Empty;
import com.sstech.graphdb.extractor.LoadAndConvertDataFromSQL;
import com.sstech.graphdb.extractor.bean.SnowFlakeConnection;
import com.sstech.graphdb.extractor.bean.SnowFlakeConnectionPool;
import com.sstech.graphdb.extractor.client.CoreGrpcClient;
import com.sstech.graphdb.extractor.client.LoaderGrpcClient;
import com.sstech.graphdb.extractor.client.TransformerGrpcClient;
import com.sstech.graphdb.extractor.utils.ConstantsAndUtils;
import com.sstech.graphdb.extractor.utils.OSUtils;
import com.sstech.graphdb.grpc.*;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import net.snowflake.client.jdbc.internal.apache.commons.io.FileUtils;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.*;
import java.util.concurrent.*;

import static java.util.stream.Collectors.toList;


@GrpcService
public class ServicesToGraphExtractorController extends ServicesToGraphExtractorGrpc.ServicesToGraphExtractorImplBase {
    private static final Object NULL = null;
	// This class receives signal from GraphExtractor using ServicesToGraphTransformer service
    @Autowired
    private LoaderGrpcClient loaderGrpcClient;
    @Autowired
    private CoreGrpcClient coreGrpcClient;
    @Autowired
    private TransformerGrpcClient transformerGrpcClient;
    @Autowired
	private SnowflakeQueryService snowflakeQueryService;

    private final boolean bathTransformation = false;
    private final boolean sparkTransformation = true;
    private final boolean streamDataToTransformer = false;

    private String rootDirectoryName;
    private final String windowsRootDirectoryName = "D:\\temp\\";
    private final String unixRootDirectoryName = "/app/temp/";

    private int FILE_WRITE_EXECUTORS = 5;
    private int FILE_PUT_EXECUTORS = 5;

//    private final HashMap<String, ArrayList<String>> dataSourceToTableMaps = new HashMap<String, ArrayList<String>>() {{
//    	put("windows", new ArrayList<String>() {{ add("MS_WIN_SECURITYAUDITING"); add("MS_WIN_SECURITYAUDITING_NETTRAFFIC");}});
//    	put("sysmon", new ArrayList<String>(){{add("MS_WIN_SYSMON");}});
//    	put("msexchange", new ArrayList<String>(){{ /*add("MS_EXCH_AGENT"); */ add("MS_EXCH_CONNECTIVITY"); add("MS_EXCH_MESSAGETRACKING");}});
//    	put("watchguard", new ArrayList<String>(){{add("WG_FW_EVENTSALARMS"); add("WG_FW_NETFLOW"); add("WG_FW_NETWORKTRAFFIC");}});
//    	put("sepc", new ArrayList<String>(){{add("SYM_ES_ENDPOINTPROTECTIONCLIENT"); add("SYM_ES_NETWORKPROTECTION");}});
//	}};

	private final HashMap<String, ArrayList<String>> dataSourceToTableMaps = new HashMap<String, ArrayList<String>>() {{
		put("windows", new ArrayList<String>() {{ add("MS_WIN_SECURITYAUDITING_DEMO");}});
		put("sysmon", new ArrayList<String>(){{add("MS_WIN_SYSMON_DEMO");}});
		put("msexchange", new ArrayList<String>(){{ add("MS_EXCH_MESSAGETRACKING_DEMO");}});
		put("watchguard", new ArrayList<String>(){{ add("WG_FW_NETWORKTRAFFIC_DEMO");}});
		put("sepc", new ArrayList<String>(){{add("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO");}});
	}};

//    private final HashMap<String, List<String>> colsPerTable = new HashMap<String, List<String>>() {{
//    	put("MS_WIN_SECURITYAUDITING", Arrays.asList("hostname", "event_time", "subjectdomainname",
//				"subjectusername", "targetdomainname", "targetusername", "ipaddress", "processname","data_file_name", "event_id", "event_time"));
//		put("MS_WIN_SECURITYAUDITING_NETTRAFFIC", Arrays.asList("hostname", "event_time", "sourceaddress",
//				"destaddress", "protocol", "direction", "application", "eventprovider","remotemachineid", "remoteuserid",
//				"data_file_name", "sourceport", "destport","event_id", "processid"));
//		put("MS_WIN_SYSMON", Arrays.asList("event_time", "eventprovider", "commandline",
//				"destinationhostname", "destinationip", "hostname", "parentimage", "image","processid", "protocol",
//				"sourcehostname", "sourceip", "targetfilename", "user_name","destinationport", "sourceport", "event_id"));//
////		put("MS_EXCH_AGENT", Arrays.asList("event_time", "dst_ip", "agent", "action", "dst_port", "localendpoint",
////				"src_ip", "src_port", "enteredorgfromip", "hostname", "p1fromaddresss", "p2fromaddress",
////				"reason", "recipient", "remoteendpoint", "numrecipient"));
//		put("MS_EXCH_CONNECTIVITY", Arrays.asList("event_time", "destination",
//				"hostname", "source"));
//		put("MS_EXCH_MESSAGETRACKING", Arrays.asList("event_id", "event_time", "client_hostname", "client_ip",
//				"directionality", "hostname", "message_subject", "original_client_ip", "original_server_ip",
//				"recipient_address", "sender_address", "server_ip", "server_hostname", "total_bytes"));//
//		put("WG_FW_EVENTSALARMS", Arrays.asList("syslog_event_datetime","syslog_host", "user_name", "path",
//				"ip_src_addr", "ip_dst_addr", "data_file_name", "ip_dst_port", "ip_src_port"));//
//		put("WG_FW_NETWORKTRAFFIC", Arrays.asList("syslog_event_datetime", "app_name", "arg", "syslog_host",
//				"src_user", "ip_src_addr","ip_dst_addr", "dstname", "dst_user", "filename", "path", "msg_host",
//				"duration", "method", "data_file_name", "ip_src_port", "in_bytes", "out_bytes", "ip_dst_port"));//
//		put("WG_FW_NETFLOW", Arrays.asList("event_time", "host", "ipv4_src_addr",
//				"ipv4_dst_addr", "direction", "in_bytes", "data_file_name"));//
//		put("SYM_ES_ENDPOINTPROTECTIONCLIENT", Arrays.asList("eventprovider", "event_desc", "event_time", "action_action", "action_desc",
//				"file_path", "hostname", "source", "data_file_name", "event_id",
//				"size", "num_scanned", "num_skipped", "num_risks", "num_omitted"));//
//		put("SYM_ES_NETWORKPROTECTION", Arrays.asList("eventprovider","event_desc", "event_time", "hostname",
//				"data_file_name", "event_id"));//
//	}};

	private final HashMap<String, List<String>> colsPerTable = new HashMap<String, List<String>>() {{
		put("MS_WIN_SECURITYAUDITING_DEMO", Arrays.asList("hostname", "eventtime", "subjectdomainname",
				"subjectusername", "targetdomainname", "targetusername", "ipaddress", "processname","data_file_name", "event_id"));
		put("MS_WIN_SYSMON_DEMO", Arrays.asList("eventtime", /*"eventprovider", "commandline",*/
				"destinationhostname", "destinationip", "hostname", "parentimage", "image","processid", "protocol",
				"sourcehostname", "sourceip", "targetfilename", "user","destinationport", "sourceport", "event_id"));
		put("MS_EXCH_MESSAGETRACKING_DEMO", Arrays.asList("event_id", "datetime", "client_hostname", "client_ip",
				"directionality", /*"hostname", */"message_subject", "original_client_ip", "original_server_ip",
				"recipient_address", "sender_address", "server_ip", "server_hostname", "total_bytes"));
		put("WG_FW_NETWORKTRAFFIC_DEMO", Arrays.asList("timestamp", /*"app_name", */"arg", /*"syslog_host",*/
				"src_user", "ip_src_addr","ip_dst_addr", "dstname", "dst_user",
				"elapsed_time", "data_file_name", "ip_src_port", "rcvd_bytes", "sent_bytes", "ip_dst_port"));
		put("SYM_ES_ENDPOINTPROTECTIONCLIENT_DEMO", Arrays.asList(/*"eventprovider", "event_desc", */"eventtime",
				"hostname", "data_file_name", "event_id"));
	}};

	public ServicesToGraphExtractorController() {
	}

	private void connectAndValidateConnectionToService(CoreGrpcClient service) {
		Object serviceCore = service.connect();
		if (serviceCore == null) {
			try {
				throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
						"HOST/PORT isn't defined in application.properties in extractor");
			} catch (IllegalAccessException e) {
				e.printStackTrace();
			}
		}
	}

	private void connectAndValidateConnectionToService(TransformerGrpcClient service) {
		Object serviceCore = service.connect();
		if (serviceCore == null) {
			try {
				throw new IllegalAccessException("Trying to access Transformer GRpc client but grpc.transformer -> " +
						"HOST/PORT isn't defined in application.properties in extractor");
			} catch (IllegalAccessException e) {
				e.printStackTrace();
			}
		}
	}

    @Override
    public void startGraphExtraction(CaseSubmissionPayload request, StreamObserver<Empty> responseObserver) {
        System.out.println("Got input payload to start extraction");

        if (OSUtils.isWindows())
        	rootDirectoryName = windowsRootDirectoryName;
        else
        	rootDirectoryName = unixRootDirectoryName;

        String caseId = request.getCaseId();

        List<String> dataSources = request.getDataSourcesList();
        HashMap<String, List<String>> dataToQuery = new HashMap<>();
        if (dataSources == null) {
        	System.out.println("Initialized the dataToQuery as EVERYTHING as its not passed");
        	dataToQuery = this.colsPerTable;
		} else {
        	if (dataSources.size() == 1 && dataSources.get(0).toLowerCase().equals("all")) {
				dataToQuery = this.colsPerTable;
				System.out.println("Initialized the dataToQuery as EVERYTHING as its passed as ALL");
			}
        	else {
        		System.out.printf("Number of datasources passed %d %n", dataSources.size());
				for (String ds : dataSources) {
					System.out.println("For dataSource " + ds);
					List<String> tables = this.dataSourceToTableMaps.get(ds);
					for (String table : tables) {
						dataToQuery.put(table, this.colsPerTable.get(table));
						System.out.printf("Initialized the dataToQuery for table %s and ds %s %n", table, ds);
					}
				}
			}
		}

		connectAndValidateConnectionToService(transformerGrpcClient);
        connectAndValidateConnectionToService(coreGrpcClient);

		Credentials credentials = coreGrpcClient.getSnowFlakeCredentials("tenant5", "enriched");
        ConstantsAndUtils.putSnowFlakeCredentials(credentials);
        System.out.println("Queried for snowflake credentials and saved it for reuse");

		CaseLoadingProperties queryInfo = ConstantsAndUtils.convertIncomingQueryToProtoProperties(request, caseId);
		coreGrpcClient.updateCaseLoadingProperties(queryInfo);

        coreGrpcClient.updateCaseLoadingStatus("Extraction Started", request, caseId);
//	    System.out.println("Query converted from QueryObject to HashMap");

        LoadAndConvertDataFromSQL extractor = new LoadAndConvertDataFromSQL(coreGrpcClient, transformerGrpcClient, snowflakeQueryService);
		extractor.addTablesToExtract(dataToQuery);
		extractor.setQueryTime(request.getStartDate(), request.getEndDate());
		extractor.setInformationToQuery(request);
		extractor.setCaseId(caseId);
//		extractor.execute();
        extractor.load();

        boolean status = extractor.getStatus();

        if (status) {
			if (this.bathTransformation)
			{
				transformerGrpcClient.startTransformationOfGraph(generateDataForTransformer(extractor, request, caseId));
			}
			else {
				if (sparkTransformation) {
					if (streamDataToTransformer) {
						IncomingDataFormat transformerFormat = generateDataForTransformer(extractor, request, caseId);
						transformerGrpcClient.streamDataForTransformationUsingSpark(transformerFormat.getWindowsRecordsList(),
								transformerFormat.getNetworkRecordsList(), transformerFormat.getExchangeRecordsList(),
								transformerFormat.getSysmonRecordsList(), transformerFormat.getSepcRecordsList(), caseId,
								coreGrpcClient, request);

						try {
							Thread.sleep(5000);
							coreGrpcClient.updateCaseLoadingStatus("Data Extraction & Stream to Transformer completed", request, caseId);
						} catch (InterruptedException e) {
							e.printStackTrace();
						}

					} else {
						List<HashMap<String, Object>> res = loadDataToStageAndTransformIt(extractor, caseId, request);
						coreGrpcClient.updateCaseLoadingStatus("Data Extraction complete", request, caseId);
						transformerGrpcClient.startGraphTransformationFromIntermediateTable(caseId, request);
						System.out.println("Data extraction complete");
					}
				} else {
					IncomingDataFormat transformerFormat = generateDataForTransformer(extractor, request, caseId);
					transformerGrpcClient.streamDataForTransformation(transformerFormat.getWindowsRecordsList(),
							transformerFormat.getNetworkRecordsList(), transformerFormat.getExchangeRecordsList(),
							transformerFormat.getSysmonRecordsList(), transformerFormat.getSepcRecordsList(), caseId,
							coreGrpcClient, transformerGrpcClient, request);
				}
			}
        }
        else {
            coreGrpcClient.updateCaseLoadingStatus("Extraction Failed", request, caseId);
        }

//
//		try {
//			String sqlQuery = "select a.* ,'break' as break, b.*  from  tenant1.enriched.MS_WIN_SECURITYAUDITING_ODM b, ( select * from tenant1.enriched.WG_FW_NETWORKTRAFFIC_ODM " +
//				"where src_user_name = 'amitkumar' limit 50000) a where b.src_ip = a.dst_ip and  a.EVENT_TIME::DATE between  '2020-07-02'  and '2020-07-03' limit 10000;" ;
//
//			System.out.println("Executing sql");
//			List<Object> executeQryList =    snowflakeQueryService.executeQuery(sqlQuery);
//			System.out.println("Executed sql");
//
//			System.out.println("Size "+executeQryList.size());
//			List<WindowsRecord> wList = new ArrayList<>();
//			List<WatchGuardRecord> wgList = new ArrayList<>();
//
//			int objCount = 0;
//			for (Object o : executeQryList) {
//				objCount++;
//				Map<String,Object> res =  (Map<String, Object>) o;
//				Set<String> keys = res.keySet();
//
//				WindowsRecord.Builder winbuilder = WindowsRecord.newBuilder();
//				WatchGuardRecord.Builder wgbuilder = WatchGuardRecord.newBuilder();
//				boolean splitfound = false;
//
//				for (String key : keys) {
//					Object object = res.get(key);
//					if(object != NULL) {
//						String strobj = object.toString();
//
//						if (strobj.contentEquals("break")){
//							splitfound = true;
//						}
//
//						if (!splitfound) {
//							winbuilder = ConstantsAndUtils.addToWindowsRecord(winbuilder, key, strobj);
//						}
//						else {
//							wgbuilder = ConstantsAndUtils.addToWGRecord(wgbuilder, key, strobj);
//						}
//					}
//				}
//
//				WindowsRecord wr = winbuilder.build();
//				wList.add(wr);
//
//				WatchGuardRecord wg = wgbuilder.build();
//				wgList.add(wg);
//
//				MsExchangeRecord msr = MsExchangeRecord.newBuilder().getDefaultInstanceForType();
//			}
//
//			System.out.println(String.format("Windows Record count: %d Network Record Count %d Total objects %d",
//					wList.size(), wgList.size(), objCount));
//
//			IncomingDataFormat transformerFormat = IncomingDataFormat.newBuilder().
//					setCaseId(caseId).addAllWindowsRecord(wList).addAllNetworkRecords(wgList).
//					build();
//
//			System.out.println("Queried snowflake and converted to proto instances");
//
//			coreGrpcClient.updateCaseLoadingStatus("Extraction Completed", request, caseId);
//			System.out.println("Extracted and transformed records, going to call Transformer now");
//			transformerGrpcClient.startTransformationOfGraph(transformerFormat);
//
//		} catch (Exception e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//			coreGrpcClient.updateCaseLoadingStatus("Extraction Failed", request, caseId);
//		}
        System.out.println("Extraction complete, returning back to GraphApp");
        responseObserver.onNext(Empty.getDefaultInstance());
        responseObserver.onCompleted();
    }

    private List<HashMap<String, Object>> loadDataToStageAndTransformIt(LoadAndConvertDataFromSQL extractor, String caseId, CaseSubmissionPayload request) {
		Credentials credentials = ConstantsAndUtils.getSnowflakeCredentials();
		String extractorToTransformerStoredProcedure = credentials.getAdditionalParametersOrThrow("stage_to_extractor_procedure");
		String stageName = credentials.getAdditionalParametersOrThrow("stage");
		String extractedOutputTable = credentials.getAdditionalParametersOrThrow("extraction_output_tbl");
		List<String> orderOfParameters = Arrays.asList(credentials.getAdditionalParametersOrThrow("stage_to_extractor_procedure_order").split(","));

		String stageStartStatus = "Going to put files to Stage";
		coreGrpcClient.updateCaseLoadingStatus(stageStartStatus, request, caseId);

		long startTime = System.currentTimeMillis();
		ArrayList<String> fileNames = loadExtractedDataUsingStage(extractor.getAllDatasets(), caseId);

		Double duration = (System.currentTimeMillis() - startTime)/ (double) 1000;
		String stageStatus = String.format("Put files to stage. Duration (sec): %s. FileNames: [%s]", duration, String.join(",", fileNames));
		coreGrpcClient.updateCaseLoadingStatus(stageStatus, request, caseId);

		ArrayList<String> enclosedFileNames = new ArrayList<>();
		for (String fileName : fileNames) {
			enclosedFileNames.add(String.format("'%s'", fileName));
		}

		String extractorDataTransformerQuery = String.format("call %s(array_construct(%s), '%s', '%s')",
				extractorToTransformerStoredProcedure, String.join(",", enclosedFileNames), stageName, extractedOutputTable);
		System.out.printf("Going to execute query for procedure: %s", extractorDataTransformerQuery);

		List<HashMap<String, Object>> res = new ArrayList<>();
		try {
			SnowFlakeConnection connection = SnowFlakeConnectionPool.getConnection();
			res = connection.executeQuery(extractorDataTransformerQuery).getResults();
			System.out.println("Result after updating table ");
			System.out.println(res);
		} catch (SQLException throwables) {
			throwables.printStackTrace();
		}
		return res;
	}

    private IncomingDataFormat generateDataForTransformer(LoadAndConvertDataFromSQL extractor, CaseSubmissionPayload request, String caseId) {
		List<WindowsRecord> windowsRecords = extractor.getWindowsRecords();
		List<WatchGuardRecord> watchGuardRecords = extractor.getWatchGuardRecords();
		List<MsExchangeRecord> exchangeRecords = extractor.getExchangeRecords();
		List<SysmonRecord> sysmonRecords = extractor.getSysmonRecords();
		List<SEPCRecord> sepcRecords = extractor.getSepcRecords();

		System.out.println("Queried snowflake and converted to proto instances");

		String statusMsg = String.format("Extraction complete. Windows: %d, Watchguard: %d, MsExchange: %d, SysMon: %d, SEPC: %d, Total: %d",
				windowsRecords.size(), watchGuardRecords.size(), exchangeRecords.size(), sysmonRecords.size(), sepcRecords.size(),
				(windowsRecords.size()+watchGuardRecords.size()+exchangeRecords.size()+sysmonRecords.size()+sepcRecords.size()));
		coreGrpcClient.updateCaseLoadingStatus(statusMsg, request, caseId);
		System.out.println("Extracted and transformed records, going to stream data to Transformer now");

		return IncomingDataFormat.newBuilder().
				setCaseId(caseId).
				addAllWindowsRecords(windowsRecords).
				addAllNetworkRecords(watchGuardRecords).
				addAllExchangeRecords(exchangeRecords).
				addAllSepcRecords(sepcRecords).
				addAllSysmonRecords(sysmonRecords).
				build();
	}

    private String writeToCSVFile(String fileName, List<HashMap<String, Object>> data, String ds, int idx) {
		String csvData = toCSV(data);

		try (PrintWriter writer = new PrintWriter(new File(fileName))) {
			writer.write(csvData);
			System.out.printf("\nWrote file for DS: %s, Batch: %s of size: %s to %s\n", ds, idx,
					data.size(), fileName);
		} catch (FileNotFoundException e) {
			System.out.println(e.getMessage());
		}
		return fileName;
	}

	private String writeToJSONFile(String fileName, List<HashMap<String, Object>> data, String ds, int idx, String caseId) {
		String csvData = toJSONString(data, ds, caseId);

		try (PrintWriter writer = new PrintWriter(new File(fileName))) {
			writer.write(csvData);
			System.out.printf("\nWrote file for DS: %s, Batch: %s of size: %s to %s\n", ds, idx,
					data.size(), fileName);
		} catch (FileNotFoundException e) {
			System.out.println(e.getMessage());
		}
		return fileName;
	}

    private ArrayList<String> loadExtractedDataUsingStage(HashMap<String, ArrayList<HashMap<String, Object>>> datasets, String caseId) {
    	int SPLIT_SIZE = 500000;
    	int iter = 1;
    	Set<String> dataSources = datasets.keySet();
    	ArrayList<String> fileNames = new ArrayList<>();
		ArrayList<String> fullFileNames = new ArrayList<>();

    	ThreadPoolExecutor es = (ThreadPoolExecutor) Executors.newFixedThreadPool(FILE_WRITE_EXECUTORS);

    	System.out.println("Going to convert data to csvs");

		int folderIdx = 0;
		String dirName = String.format("%s_%s", caseId, iter);
		String fullFileName = rootDirectoryName + dirName;
		File fullFilePath;
		while (true) {
			fullFilePath = new File(fullFileName + String.format("_%s", folderIdx));
			if (fullFilePath.exists() && fullFilePath.isDirectory()) {
				folderIdx += 1;
				System.out.printf("Path %s already exists so going to increase counter to %s", fullFilePath.getAbsolutePath(), folderIdx);
				continue;
			} else {
				fullFilePath.mkdirs();
				break;
			}
		}
		String baseDirectory = fullFilePath.getAbsolutePath();
		System.out.println("Created directory " + baseDirectory);

		datasets.forEach( (ds, data) -> {
			System.out.printf("For DS: %s, Total data size: %s\n", ds, data.size());
		});
		System.out.println("\n");

		Collection<Future<String >> futures = new LinkedList<>();
		for (String dataSource : dataSources) {
			ArrayList<HashMap<String, Object>> data = datasets.get(dataSource);
			List<List<HashMap<String, Object>>> partitions = new LinkedList<>();

			System.out.printf("For DS: %s, the size of data is: %s\n", dataSource, datasets.size());

			for (int i = 0; i < data.size(); i += SPLIT_SIZE) {
				List<HashMap<String, Object>> subList = data.subList(i, Math.min(i + SPLIT_SIZE, data.size()));
				partitions.add(subList);
				System.out.printf("Start idx: %s, Data size: %s, DS: %s, Split size: %s, sublist size: %s, Partition size: %s", i, data.size(), dataSource, SPLIT_SIZE, subList.size(), partitions.size());
			}
			System.out.printf("Partition size %s for ds: %s\n", partitions.size(), dataSource);

			for (int i = 0; i < partitions.size(); i++) {
				List<HashMap<String, Object>> partition = partitions.get(i);

				String fileName;
				if (OSUtils.isWindows())
					fileName = String.format("\\%s_%s_%s_%s.json", dataSource, caseId, folderIdx, i);
				else
					fileName = String.format("/%s_%s_%s_%s.json", dataSource, caseId, folderIdx, i);

				int finalI = i;
				System.out.printf("Writing batch %s for ds %s to file %s\n", finalI, dataSource, baseDirectory+fileName);
				futures.add(es.submit(() -> writeToJSONFile(baseDirectory+fileName, partition, dataSource, finalI, caseId)));

				if (OSUtils.isWindows())
					fileNames.add(fileName.replace("\\", ""));
				else
					fileNames.add(fileName.replace("/", ""));

				fullFileNames.add(baseDirectory + fileName);
			}
			iter += 1;
		}
		for (Future<String> future : futures) {
			try {
				String fileName = future.get();
				System.out.println("Finished thread with filename " + fileName);
			} catch (InterruptedException | ExecutionException e) {
				e.printStackTrace();
			}
		}
		es.shutdownNow();
		futures.clear();
		futures = new LinkedList<>();

		System.out.println("Finished loading data into csv files");
		System.out.println("Wrote files to csv. Total csv files " + fileNames.size());
		System.out.printf("%s, %s, %s\n", es.isTerminated(), es.isShutdown(), es.isTerminating());
		try {
			es.awaitTermination(30, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			System.out.println("Couldn't terminate thread");
			e.printStackTrace();
		}
		if (es.isTerminated() && es.isShutdown())
		{
			System.out.println("Started new executor");
			es = (ThreadPoolExecutor) Executors.newFixedThreadPool(FILE_PUT_EXECUTORS);
		}

		Credentials credentials = ConstantsAndUtils.getSnowflakeCredentials();
		String stageName = credentials.getAdditionalParametersOrThrow("stage");

		System.out.println("Going to load files into stage");
		ArrayList<SnowFlakeConnection> connections = new ArrayList<>();
		for (String fileName : fullFileNames) {
			String putQuery = String.format("put file://%s @%s", fileName, stageName);
			System.out.printf("Executing query %s\n", putQuery);
			try {
				SnowFlakeConnection connection = SnowFlakeConnectionPool.getConnection();
				futures.add(es.submit(() -> {
					connection.executeQuery(putQuery);
					return putQuery;
				}));
				System.out.printf("Submitted query inside callable %s\n", putQuery);
				connections.add(connection);
			} catch (SQLException throwables) {
				System.out.println("exception executing query " + putQuery);
				throwables.printStackTrace();
			}
		}

		boolean failed = false;
		for (Future<String> future : futures) {
			try {
				String query = future.get();
				System.out.println("Finished executing query " + query);
			} catch (InterruptedException | ExecutionException e) {
				failed = true;
				e.printStackTrace();
			}
		}

		System.out.println("Transferred all files to stage, going to close out connections");
		connections.forEach( conn -> conn.close());
		System.out.println("Closed all connections");

		if (failed)
			System.out.println("Failed to transfer few files. Check logs");

		futures.clear();
		es.shutdownNow();

		try {
			es.awaitTermination(30, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			System.out.println("Couldn't terminate thread");
			e.printStackTrace();
		}

		System.out.println("Deleting directory to clean space");
		try {
			FileUtils.deleteDirectory(new File(dirName));
		} catch (IOException e) {
			e.printStackTrace();
		}

		return fileNames;
	}

	private static String toJSONString(List<HashMap<String, Object>> records, String ds, String caseId) {
    	List<String> jsonData = new ArrayList<>();
		for (HashMap<String, Object> record : records) {
			record.put("dataSourceName", ds);
			record.put("caseId", caseId);

			StringBuilder recordString = new StringBuilder();
			int totalColumns = record.size();

			Set<String> columns = record.keySet();
			for (String colName : columns) {
				Object colValue = record.get(colName);
				String modifiedColName = ConstantsAndUtils.mapTableColumnNameToProtoColumnName(colName, ds);

				if (colValue != null) {
					if (((String) colValue).contains("\""))
						colValue = ((String) colValue).replace("\"", "'");
					if (((String) colValue).contains("\\"))
						colValue = ((String) colValue).replace("\\", "\\\\");
				}
				recordString.append(String.format("\"%s\":\"%s\"", modifiedColName, colValue));
				if (totalColumns > 1)
					recordString.append(",");
				totalColumns -= 1;
			}
			jsonData.add(String.format("{%s}", recordString.toString()));
		}
    	return "[" + String.join(",\n", jsonData) + "]";
	}

	private static String toCSV(List<HashMap<String, Object>> list) {
		List<String> headers = list.stream().flatMap(map -> map.keySet().stream()).distinct().collect(toList());
		final StringBuffer sb = new StringBuffer();
		for (int i = 0; i < headers.size(); i++) {
			sb.append(headers.get(i));
			sb.append(i == headers.size()-1 ? "\n" : "|");
		}
		for (Map<String, Object> map : list) {
			for (int i = 0; i < headers.size(); i++) {
				sb.append(map.get(headers.get(i)));
				sb.append(i == headers.size()-1 ? "\n" : "|");
			}
		}
		return sb.toString();
	}
    
    @Override
    public void testAPI(DummyMessage request, StreamObserver<DummyMessageStatus> responseObserver) {
		if (OSUtils.isWindows())
			rootDirectoryName = windowsRootDirectoryName;
		else
			rootDirectoryName = unixRootDirectoryName;

        connectAndValidateConnectionToService(transformerGrpcClient);

        DummyMessageStatus resp =
                transformerGrpcClient.pingGraphTransformerWithDummySignalMono(request.getMessage() + " sent from TransformerServer");

        System.out.println("Printing response from graphLoader");
        System.out.println(resp);
        System.out.println("===============");

        DummyMessageStatus response = DummyMessageStatus.newBuilder().
                setMessage(resp.getMessage() + " inside TransformerGrpcServer").
                setStatus("Computed inside TransformerServer").
                setSource(this.getClass().toGenericString()).
                addAllCurrent(resp.getCurrentList()).addCurrent("Extractor").build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}
