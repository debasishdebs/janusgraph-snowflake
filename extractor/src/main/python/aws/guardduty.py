#!/usr/bin/python

from utils import *
import uuid
import random

iplist = {}

def generate_guardduty(user):
	global guardduty_events
	global iplist

	iplist = {}

	if user in guardduty_events:
		events = guardduty_events[user]
	else:
		events = guardduty_events["default"]

	for event in events:
		event_name, frequency = event

		frq = int(frequency)
		offset2 = offset = int(frq * 10 / 100)

		if offset2 == 0:
			offset2 = 1

		for i in range(random.randint(frq - offset2, frq + offset2)):
			generate_guardduty_user(user, event_name, None)

	for ip in get_notused_ip_list(user, iplist):
		for event in events:
			event_name, frequency = event

			generate_guardduty_user(user, event_name, ip)

def generate_guardduty_user(user, event_name, src_ip):
	global iplist

	sample = get_user_val(event_name, "guardduty_sample")

	if src_ip == None:
		src_ip = get_user_val(user, "aws_iplist")

	repl = {
		"%USERNAME%": user,
		"%ACCOUNTID%": get_user_val(user, "aws_accountid"),
		"%REGION%": get_user_val(user, "aws_region"),
		"%ID%": str(uuid.uuid4().hex),
		"%TS%": get_aws_time(),
		"%ARN%": get_user_val(user, "aws_arn"),
		"%SRC_IP%": src_ip,
		"%DETECT_ID%": str(uuid.uuid4().hex)
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
	global guardduty_events

	guardduty_events = load_config_file_list("guardduty_events")

	with open(get_home_path() + "/config/users.csv", "r") as f:
		for row in f:
			user = row.strip()

			generate_guardduty(user)

days = get_cmd_days_offset()

for i in (range(days)):
	offset = days - i
	set_days_offset(offset)
	main()
