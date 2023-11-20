import os
from datetime import date, datetime, timedelta
import random
import uuid

ind = 0
ind2 = 1
ind3 = 1

def get_ip_lateral():
	global ind

	ind += 1

	if (ind >= 4):
		ind = 1

	return '10.10.110.' + str(ind)

def get_ip_lateral2():
	global ind2

	ind2 += 1

	if (ind2 >= 5):
		ind2 = 2

	return '10.10.110.' + str(ind2)

def get_dst_domain_lateral2():
	global ind3

	ind3 += 1

	if (ind3 >= 5):
		ind3 = 2

	return 'domain-' + str(ind3) + '.local'

def get_distance_vpn_ip():
	import random

	return random.choice(["94.244.22.168", "104.236.213.230", "192.206.151.131", "219.75.27.16", "216.58.194.142", "17.178.96.59", "104.43.195.251", "77.88.55.77", "216.58.194.68"])

# def get_1gb_plus():
def get_sent_bytes():
	import random

	return 1073741 + random.randint(1, 1073741)
#	return 1073741824 + random.randint(1, 1073741824)

def get_500mb_plus():
	import random

	return 504857600 + random.randint(1, 504857600)

def get_random_ip(cidr):
    import ipaddress
    import random
    net = ipaddress.IPv4Network(cidr)
    return net[ random.randint(0, net.num_addresses-1) ]

def get_email():
    import random
    fn = ['noah','emma','mason','ethan','james','madison','daniel','ray','camille','clark','bruce','diana','flash']
    ln = ['smith','gold','hunt','knight','fisher','cook','clark','kent','wayne','prince','gordon']
    dom = ['example.com','outlook.com','skype.com','hotmail.com','yahoo.com','gmail.com','secure.com','cnn.com','nbc.com','news.com']
    email = fn[random.randrange(0, len(fn))] + '.' + ln[random.randrange(0, len(ln))] + '@' + dom[random.randrange(0, len(dom))]
    return email

def get_rcpt(min_=1, max_=3):
    import random
    cnt = random.randint(min_, max_)
    rcpt = [ get_email() for x in range(0, cnt) ]
    return [ ';'.join(rcpt), cnt ]


def get_random_host():
    import random
    return 'test' + str(random.randint(1, 20)) + random.choice(['.com', '.net', '.org', '.info', '.biz'])

def get_random_host_200():
    import random
    return 'test200case-' + str(random.randint(1, 30)) + random.choice(['.com', '.net', '.org', '.info', '.biz'])

def get_random_uripath():
    import random
    return '/' + random.choice(['index', 'test', 'page' + str(random.randint(1, 50)), 'info']) + \
        random.choice([ '.html', '.htm', '.js', '.css', '.xml', '.json', '.swf',
            '.gif', '.jpg', '.bmp', '.jpeg', '.png',
            '.pl', '.php', '.rb', '.py',
            '.txt', '.doc', 'csv', '.cgi'])

def get_random_mac():
    import random
    mac_arr = []
    for part in range(0, 6):
        mac_arr.append(str(hex(random.randint(16, 255)))[2:])
    return ':'.join(mac_arr)

import time;

uniq_id = int(round(time.time() * 1000))

def getYMD(vals):
    time = vals["dt"]
    return time.strftime("%Y-%m-%d %H:%M:%S")

def get_id_num():
    global uniq_id

    uniq_id += 1

    return uniq_id

def get_agtscan_duration(ts):
    from datetime import datetime
    import random
    import time

    duration = random.randint(1, 300)
    e_ts = int(ts) - random.randint(1, 120);
    s_ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e_ts - duration))
    e_ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e_ts))

    return 'Begin: ' + s_ts + ',End: ' + e_ts + ',Completed,Duration (seconds): ' + str(duration);

def get_barracuda_btotal_recip(vals):
    return int(vals['%POLICY%']) + int(vals['%SPAM%']) + int(vals['%VIRUS%']) + int(vals['%ATDFULL%']) + int(vals['%OTHER%'])

def get_barracuda_total_recip(vals):
    return get_barracuda_btotal_recip(vals) + int(vals['%DEFERRED%']) + int(vals['%QUARANTINED%']) + int(vals['%ALLOWED%'])

users_info = None

def load_users_info():
    global users_info

    users_info = {}
    with open(os.path.dirname(__file__) + '/users_data.txt', 'r') as f:
        for line in f.readlines():
            user, src_ip, host, min_sent, min_rcvd, user_id = line.rstrip().split(',')
            ip_list = src_ip.split('|')

            if len(ip_list) > 1:
                weekNumber = date.today().isocalendar()[1]
                ind = weekNumber % len(ip_list)
                src_ip = ip_list[ind]

            data = {
                'src_ip': src_ip,
                'host': host,
                'min_sent': int(min_sent),
                'min_rcvd': int(min_rcvd),
                'user_id': user_id
            }

            users_info[user] = data
            users_info[user.split('@')[0]] = data

def get_user_info(get_user):
    global users_info

    if users_info == None:
        users_info = {}
        load_users_info()

    if get_user not in users_info:
        return None

    return users_info[get_user]

def get_user_src_ip(vals):
    user = get_user_info(vals['%SRCUSER%'])

    if user == None:
        return ''

    return user['src_ip']

def get_target_account_ip(vals):
    user = get_user_info(vals['%TARGET_ACCOUNT%'])

    if user == None:
        return ''

    return user['src_ip']

def get_target_account_host(vals):
    user = get_user_info(vals['%TARGET_ACCOUNT%'])

    if user == None:
        return ''

    return user['host']

def get_user_sent_bytes(vals):
    user = get_user_info(vals['%SRCUSER%'])

    min = 0 if user == None else user['min_sent']

    return min + random.randint(100, 10000)

def get_user_rcvd_bytes(vals):
    user = get_user_info(vals['%SRCUSER%'])

    min = 0 if user == None else user['min_rcvd']

    return min + random.randint(1000, 100000)

def get_username(vals):
    global users_info

    if not '%USER%' in vals:
        if users_info == None:
            load_users_info()

        vals['%USER%'] = random.choice(list(users_info.keys()))

    return vals['%USER%']

def get_sysmon_hostname(vals):
    user = get_user_info(get_username(vals))

    if user == None:
        return ''

    return user['host']

def get_uuid():
    return str(uuid.uuid4())

def get_sysmon_userid(vals, name = None):
    if name == None:
        name = get_username(vals)
    else:
        vals['%USER%'] = name

    user = get_user_info(name)

    if user == None:
        return ''

    return user['user_id']

def get_sysmon_srcip(vals):
    user = get_user_info(get_username(vals))

    if user == None:
        return ''

    return user['src_ip']

def get_guid_time(str):
    return '{' + datetime.now().strftime("%Y%m%d") + str + '}'

def get_random_filename(prefix):
    return prefix + random.choice(['index', 'test', 'file' + str(random.randint(1, 50)), 'info']) + \
        random.choice([ '.html', '.htm', '.js', '.css', '.xml', '.json', '.swf',
            '.gif', '.jpg', '.bmp', '.jpeg', '.png',
            '.pl', '.php', '.rb', '.py',
            '.txt', '.doc', 'csv', '.cgi'])

def get_random_time(interval, vals):
    ts = vals['dt'] - timedelta(minutes=random.randint(0, interval));

    return ts.strftime('%Y-%m-%d %H:%M:%S')

def get_random_external_internal_ip():
    return random.choice([get_distance_vpn_ip(), get_random_ip('192.168.0.0/24')])
