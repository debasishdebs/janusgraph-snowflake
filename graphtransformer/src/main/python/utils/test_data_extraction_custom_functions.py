from os import path


def generate_user_name_for_windowsnxlog(params, record, repeat):
    if params[0] in record:
        username = record[params[0]]
        username = username.replace("$", "")
        username = username.replace("ACME\\", "")
        username = username.lower()
        return username
    else:
        return ""


def generate_user_name_for_sysmon(params, record, repeat):
    if params[0] in record:
        username = record[params[0]]
        username = username.replace("$", "")
        username = username.replace("ACME\\", "")
        username = username.lower()
        return username
    else:
        return ""


def generate_process_name_for_sysmon(params, record, repeat):
    from os import path
    # if params[0] in record:
    #     value = record[params[0]]
    #     processes = value.split(",")
    #     new_processes = []
    #     for process in processes:
    #         new_processes.append(path.basename(process))
    #     if repeat == -1:
    #         return new_processes
    #     return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    # else:
    #     return [""]

    if params[0] in record:
        value = record[params[0]]
        return path.basename(value).lower()
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process))
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return ""


def generate_process_path_for_sysmon(params, record, repeat):
    from os import path
    if params[0] in record:
        value = record[params[0]]
        value = value.replace("%", "")
        return path.dirname(value).lower()
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.dirname(process))
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return [""]


def generate_process_name_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        return path.basename(value).lower()
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.basename(process))
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return ""


def generate_process_path_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        return path.dirname(value).lower()
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.dirname(process))
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return ""


def generate_elapsed_time_for_watchguard(params, record, repeat):
    if params[0] in record:
        value = record[params[0]]
        values = value.split(" ")
        time_num = values[0]
        time_unit = values[1]
        return time_num
        return path.dirname(value).lower()
        processes = value.split(",")
        new_processes = []
        for process in processes:
            new_processes.append(path.dirname(process))
        if repeat == -1:
            return new_processes
        return new_processes if len(new_processes) >= repeat else new_processes[:repeat]
    else:
        return "NA"


if __name__ == '__main__':
    import json
    fname = "D:\\Projects\\Freelancing\\Elysium Analytics\\data\\data\\wgtraffic_phishing_attack_5d_2020_08_31.json"

    data = json.load(open(fname))

    print("Watchguard process names")
    process = []
    for record in data:
        process.append(generate_process_name_for_watchguard(["arg"], record, 1))
    print(set(process))

    print("Watchguard process paths")
    process = []
    for record in data:
        process.append(generate_process_path_for_watchguard(["arg"], record, 1))
    print(set(process))

    print("Watchguard elapsed times")
    times = []
    for record in data:
        times.append(generate_elapsed_time_for_watchguard(["elapsed_time"], record, 1))
    print(set(times))
