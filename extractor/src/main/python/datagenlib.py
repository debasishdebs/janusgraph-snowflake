import os
import sys
import numpy
import pycron
import random
import datetime
import json
from common.resources import Resources as R

class Template:
    def __init__(self, template_id, template):
        self.template_id = template_id
        self.template = template

class Schedule:
    def __init__(self, config):
        self.cronline = config[0]
        self.timeframe = config[1]
        self.frequency = config[2]
        self.current_tick = 0
        self.fill_frequency_map()

    def fill_frequency_map(self):
        self.current_tick = 0
        count = random.randint(self.frequency[0], self.frequency[1])
        self.frequency_map = numpy.random.randint(0, self.timeframe, count)

    def update_rel_time(self):
        self.current_tick += 1
        if self.timeframe != 0 and self.current_tick > self.timeframe:
            self.fill_frequency_map()

    def is_now(self, dt):
        if pycron.is_now(self.cronline, dt):
            if self.timeframe == 0:
                return True
            elif self.current_tick in self.frequency_map:
                return True
        else:
            # self.update_rel_time()
            return False


class Scenario:
    def __init__(self, template, properties, user):
        self.template = template
        if 'timeformat' in properties:
            self.timeformat = properties['timeformat']
        else:
            self.timeformat = '%Y-%m-%d %H:%M:%S'
        self.replaces = properties['replaces']
        self.abs_path = properties['abs_path']
        self.user = user
        for placeholder in self.replaces.keys():
            replacer = self.replaces[placeholder]
            if replacer[0] == 'file':
                self.replaces[placeholder][0] = 'set'
                self.replaces[placeholder][1] = self.load_samples_from_file(replacer[1])

    def load_samples_from_file(self, fname):
        if not os.path.isabs(fname):
            fname = os.path.join(self.abs_path, fname)
        with open(fname, 'r') as f:
            return f.read().splitlines()

    def produce(self, dt):
        replacement_map = {}
        replacement_map['dt'] = dt
        postpone = []
        result = self.template.template
        for placeholder in self.replaces.keys():
            replace = self.replaces[placeholder]
            if replace[0] == 'set':
                idx = random.randint(0, len(replace[1])-1)
                to_replace = replace[1][idx]
            elif replace[0] == 'user':
                to_replace = self.user.get_user_prop(replace[1])
            elif replace[0] == 'py':
                if len(replace) >= 4 and int(replace[3]) > 0:
                    item = replace.copy()
                    item.insert(0, placeholder)
                    postpone.append(item)
                    continue

                to_replace = replace[1](*replace[2])
            else:
                to_replace = '<<REPLACE_ME:'+placeholder+'>>'

            if ',' in placeholder:
                placeholder_list = placeholder.split(',')
                for i in range(0, len(to_replace)):
                    replacement_map[placeholder_list[i]] = to_replace[i]
            else:
                replacement_map[placeholder] = to_replace

        for itm in sorted(postpone, key=lambda x: x[4]):
            args = list(itm[3])
            args = list(map(lambda itm: replacement_map if str(itm) == '%VALS%' else itm, args))
            to_replace = itm[2](*args)
            replacement_map[itm[0]] = to_replace

        for p in replacement_map.keys():
            result = result.replace(p, str(replacement_map[p]))
        return result


class Activity:
    def __init__(self, scenario, schedule):
        self.scenario = scenario
        self.schedule = schedule

    def go(self, dt):
        if self.schedule.is_now(dt):
            for s in self.scenario:
                ts = dt.strftime(s.timeformat)
                # print(s.produce(dt).replace('%TS%', ts))
                R.put_data(convert_record_string_to_json(s.produce(dt).replace('%TS%', ts)))
        self.schedule.update_rel_time()


def convert_record_string_to_json(data):
    from common.resources import Resources as R

    if "msexchange" in R.get_ds() or "wgtraffic" in R.get_ds():
        if "msexchange" in R.get_ds():
            from common.CleanMsExchangeRecords import MsExchangeCleaner
            cleaner = MsExchangeCleaner(False)
            cleaner.fit([data])
            row = cleaner.clean_()
            return row[0]

        if "wgtraffic" in R.get_ds():
            from common.CleanWatchGuardRecords import WatchGuardCleaner
            cleaner = WatchGuardCleaner(False)
            cleaner.fit([data])
            row = cleaner.clean_()
            return row[0]

    else:
        data = data.split("]: {")[1]
        data = "{" + data
        data = data.replace("#015", "")
        if "\"LogonGuid\"" not in data:
            data = data.replace("LogonGuid\"", "\"LogonGuid\"")

        return json.loads(data)


class User:
    def __init__(self, user_info):
        self.user_info = user_info
        self.activities = {}

    def get_user_prop(self, key):
        if key in self.user_info:
            return self.user_info[key]
        else:
            return ''

    def add_activity(self, aid, activity):
        if aid in self.activities:
            return False
        self.activities[aid] = activity
        return True

    def del_activity(self, aid):
        del self.activities[aid]

    def time_changed(self, dt):
        for activity in self.activities.keys():
            self.activities[activity].go(dt)

    def set_state_prop(self, key, state):
        self.state_props[key] = state

    def get_state_prop(self, key):
        if key in self.state_props:
            return self.state_props[key]

class Clock:
    def __init__(self, beg_period, end_period):
        self.dt = beg_period
        self.end_period = end_period
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def tick(self):
        self.dt = self.dt + datetime.timedelta(seconds=1)
        if self.dt > self.end_period:
            return False
        for o in self.observers:
            o.time_changed(self.dt)
        return True

def load_model_from_file(fd):
    conf_abs_path = os.path.dirname(os.path.abspath(fd.name))
    sys.path.append(conf_abs_path)
    import yaml
    config = yaml.load(fd.read())

    USERS = config['USERS']
    ACTIVITY = config['ACTIVITY']
    TEMPLATES = config['TEMPLATES']
    SCENARIOS = config['SCENARIOS']

    users = []
    for userid in USERS.keys():
        user = User(USERS[userid])
        if userid in ACTIVITY:
            i = 0
            for a in ACTIVITY[userid]:
                scenarios = []
                for evt in SCENARIOS[a[0]]:
                    templateid = evt['templateid']
                    template = Template(templateid, TEMPLATES[templateid])
                    evt['abs_path'] = conf_abs_path
                    s = Scenario(template, evt, user)
                    scenarios.append(s)
                schedule = Schedule(a[1])
                activity = Activity(scenarios, schedule)
                user.add_activity(i, activity)
                i += 1
        users.append(user)
    return users
