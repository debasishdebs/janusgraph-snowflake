#!/usr/bin/python

from utils import *
import uuid
import random

iplist = {}

def generate_dome9(user):
	global dome9_events
	global iplist

	iplist = {}

	if user in dome9_events:
		events = dome9_events[user]
	else:
		events = dome9_events["default"]

	for event in events:
		event_name, frequency = event

		frq = int(frequency)
		offset2 = offset = int(frq * 10 / 100)

		if offset2 == 0:
			offset2 = 1

		for i in range(random.randint(frq - offset, frq + offset2)):
			generate_dome9_user(user, event_name, None)

	for ip in get_notused_ip_list(user, iplist):
		for event in events:
			event_name, frequency = event

			generate_dome9_user(user, event_name, ip)

def generate_dome9_user(user, event_name, src_ip):
	global iplist

	sample = get_user_val(event_name, "dome9_sample")

	if src_ip == None:
		src_ip = get_user_val(user, "aws_iplist")

	repl = {
		"%MESSAGEID%": str(uuid.uuid4()),
		"%ARN%": get_user_val(user, "aws_arn"),
		"%TS%": get_aws_time(),
		"%USERID%": get_user_val(user, "dome9_userid"),
		"%USERNAME%": user,
		"%SRC_IP%": src_ip,
		"%AWSACCOUNTID%": get_user_val(user, "dome9_aws_accountid"),
		"%CLOUD_ACCOUNT_NAME%": get_user_val(user, "dome9_cloudaccpuntname"),
		"%AWS_ACCOUNT_NUMBER%": get_user_val(user, "dome9_aws_account_number"),
		"%AWS_ACCOUNT_NAME%": get_user_val(user, "dome9_aws_account_name"),
		"%AZ_CLOUD_ACCOUNTID%": get_user_val(user, "dome9_azure_cloud_account_id"),
		"%AZ_CLOUD_ACCOUNTID_NAME%": get_user_val(user, "dome9_azure_account_name"),
		"%SUBSCRIPTIONID%": get_user_val(user, "dome9_subscription_id"),
		"%TENANTID%": get_user_val(user, "dome9_tenant_id"),
		"%RESOURCE_GROUP%": get_user_val(user, "dome9_resource_group"),
		"%REGION%": get_user_val(user, "aws_region"),
		"%GROUP_NAME%": get_user_val(user, "dome9_group_name"),
		"%GROUP_TAGS%": get_user_val(user, "dome9_group_tags"),
		"%TARGET_USERID%": get_user_val(user, "dome9_target_user_id"),
		"%TARGET_USERNAME%": get_user_val(user, "dome9_target_user_name")
	}

	if "%SRC_IP%" in sample:
		iplist[src_ip] = 1

	for k in repl.keys():
		val = repl[k]

		if val == "NULL":
			val = ""

		sample = sample.replace(k, val)

	print sample

def main():
	global dome9_events

	dome9_events = load_config_file_list("dome9_events")

	with open(HOME_PATH + "/config/users.csv", "r") as f:
		for row in f:
			user = row.strip()

			generate_dome9(user)

days = get_cmd_days_offset()

for i in (range(days)):
	offset = days - i
	set_days_offset(offset)
	main()
