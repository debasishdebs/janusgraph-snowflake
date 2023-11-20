import random

users = [
  "AWSServiceRoleForApplicationAutoScaling_DynamoDBTable", 
  "AstraSandBoxCrossAccount",
  "astra-aws-dome9-EventParserRole-GEV2FWPS3VXE",
  "astra-aws-dome9-accounts-AccountManagerRole-T4YBZ5METEUW",
  "astra-aws-dome9-compliance-AlertsFilterRole-184MFWS9LE5W5",
  "astra-aws-dome9-compliance-CloudSupervisorRole-TYQSWD6WM243",
  "astra-aws-dome9-compliance-InventoryCollectorRole-TBRHLFCWAR80",
  "astra-aws-dome9-compliance-RemediatorRole-IHHVMOVMZ3M4",
  "astra-aws-dome9-es-indexer-AstraD9ESIndexerRole-YTRMHW62F3I2",
  "astra-aws-dome9-ses-notif-AstraAccountNotifierRole-4QKGWH8C11SH",
  "astra-aws-lumberjack-S3deliveryRole-X4BH3EWFPAV9",
  "astra-aws-lumberjack-firehoseLambdaRole-3Z6JLFKBSOB7",
  "astra-aws-lumberjack-stormLambdaRole-E6SWOD4Q545X",
  "astra-aws-report-schedule-AstraAWSReportSchedulerR-11BYJX256H7XQ",
  "astra-aws-report-schedule-AstraAWSReportSchedulerR-18QL5S508GTI4",
  "astra-aws-workload-svm-report-AstraLambdaSvmWorker-152245NACSJ9U",
  "astra-aws-workload-svm-report-AstraLambdaSvmWorker-1T0B4EQTFKATZ",
  "astra-es-remodeller-AstraESRemodellerRole-XL763E96FIJ6",
  "astra-prod@list.att.com",
  "bm2371@att.com",
  "db521d@att.com",
  "dd457p@att.com",
  "fred.h.meyer@att.com",
  "jo757d@att.com",
  "pa0780@att.com"
]

ln = 10
for user in users:
	if len(user) > ln:
		ln = len(user)

cnt = 0
for user in users:
	cnt += 1

	for i in range(1, random.randint(20, 51)):
		format = "| %-" + str(ln) + "s  | %-12s  |"
		print format % (user, "54.85." + str(cnt) + "." + str(i))
