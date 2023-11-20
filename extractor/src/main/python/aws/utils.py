import os
import sys
import datetime
import random

HOME_PATH = os.path.dirname(os.path.abspath(__file__))
cdata = {}
date = None

def set_days_offset(offset):
	global date

	date = str((datetime.datetime.now() - datetime.timedelta(days = offset)).date()) + "T01:02:03Z"

def get_home_path():
	return HOME_PATH

def get_aws_time():
	global date

	return date

def load_config_file_list(name):
	data = {}

	with open(HOME_PATH + "/config/" + name + ".csv", "r") as f:
		for row in f:
			cols = row.strip().strip("|").split("|")
			cols = map(lambda item: item.strip(), cols)

			user = cols.pop(0)

			if user not in data:
				data[user] = []

			data[user].append(cols)

		return data

def load_config_file(name):
	global cdata

	data = {}

	with open(HOME_PATH + "/config/" + name + ".csv", "r") as f:
		for row in f:
			row = row.strip().strip("|")

			if row == "":
				continue

			cols = row.split("|")
			cols = map(lambda item: item.strip(), cols)

			user = cols.pop(0)

			if user in data:
				if type(data[user]) != list:
					data[user] = [data[user]]

				data[user].append(cols[0])
			else:
				data[user] = cols[0]

		cdata[name] = data;

		return data

def get_user_val(user, filename):
	global cdata

	if filename not in cdata:
		load_config_file(filename)

	data = cdata[filename]

	if user in data:
		val = data[user]
	else:
		val = data["default"]

	if type(val) == list:
		return random.choice(val)

	return val

def get_notused_ip_list(user, iplist):
	global cdata

	data = cdata["aws_iplist"]

	if user in data:
		val = data[user]
	else:
		val = data["default"]

	if type(val) != list:
		val = [val]

	result = []

	for ip in val:
		if ip not in iplist:
			result.append(ip)

	return result
	

def get_cmd_days_offset():
	if len(sys.argv) <= 1:
		return 1

	return int(sys.argv[1])

