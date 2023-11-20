#!/usr/bin/python

from utils import *
import uuid
import random

iplist = {}

def generate_awstrail(user):
	global trail_events
	global iplist

	iplist = {}

	if (user in trail_events):
		events = trail_events[user]
	else:
		events = trail_events["default"]

	for event in events:
		event_name, frequency = event
		frq = int(frequency)
		offset = int(frq * 10 / 100)

		for i in range(random.randint(frq - offset, frq + offset)):
			generate_aws_user(user, event_name, None)

	for ip in get_notused_ip_list(user, iplist):
		for event in events:
			event_name, frequency = event

			generate_aws_user(user, event_name, ip)

def generate_aws_user(user, event_name, src_ip):
	global iplist

	sample = get_user_val(event_name, "aws_samples")

	arn = get_user_val(user, "aws_arn")

	if src_ip == None:
		src_ip = get_user_val(user, "aws_iplist")

	repl = {
		"%TS%": get_aws_time(),
		"%PRINCIPAL_ID%": get_user_val(user, "aws_principal_id"),
		"%ARN%": arn,
		"%SESSION_ARN%": arn,
		"%ROLE_ARN%": arn,
		"%ASSU_ARN%": arn,
		"%RES_ARN%": arn,
		"%ACCOUNTID%": get_user_val(user, "aws_accountid"),
		"%USERNAME%": get_user_val(user, "aws_username"),
		"%AWS_REGION%": get_user_val(user, "aws_region"),
		"%SRC_IP%": src_ip,
		"%REQUEST_ID%": str(uuid.uuid4()),
		"%EVENT_ID%": str(uuid.uuid4())
	}

	if "%SRC_IP%" in sample:
		iplist[src_ip] = 1

	for k in repl.keys():
		sample = sample.replace(k, repl[k])

	print sample

def main():
	global trail_events

	trail_events = load_config_file_list("aws_events")

	with open(HOME_PATH + "/config/users.csv", "r") as f:
		for row in f:
			user = row.strip()

			if user == "system":
				continue

			generate_awstrail(user)

days = get_cmd_days_offset()

for i in (range(days)):
	offset = days - i
	set_days_offset(offset)
	main()
