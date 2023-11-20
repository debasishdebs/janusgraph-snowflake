if __name__ == '__main__':
    import json
    import pprint

    root_path = "D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\graphdb-in-snowflake\\snowflake-graphdb\\extractor\\src\\main\\resources\\data\\v3\\"

    windows = json.load(open(root_path + "windowsnxlog_phishing_attack_5d_2020_08_31.json"))
    wgtraffic = json.load(open(root_path + "wgtraffic_phishing_attack_5d_2020_08_31.json"))
    sysmon = json.load(open(root_path + "sysmon_phishing_attack_1d_2020_08_31.json"))
    sepc = json.load(open(root_path + "symantecendpoint_phishing_attack_5d_2020_08_31.json"))
    exchange = json.load(open(root_path + "msexchange_phishing_attack_5d_2020_08_31.json"))

    unique_props = []
    unique_props_list = []
    property_string = ""
    i = 2
    replacement_dict = {}
    for record in windows:
        keys = record.keys()
        for k in keys:
            if k not in unique_props_list:
                unique_props.append([k, type(record[k])])
                unique_props_list.append(k)

                if "-" in k:
                    replacement_dict[k] = k.replace("-", "_")
                    new_k = k.replace("-", "_")
                else:
                    new_k = k

                if isinstance(record[k], int):
                    v = f"int64 {new_k} = {i};\n"
                if isinstance(record[k], str):
                    v = f"string {new_k} = {i};\n"

                i += 1
                property_string += v

    print("Unique properties in windows are")
    # pprint.pprint(unique_props)
    print(property_string)
    print(50*"=")

    unique_props = []
    unique_props_list = []
    property_string = ""
    i = 2
    for record in wgtraffic:
        keys = record.keys()
        for k in keys:
            if k not in unique_props_list:
                unique_props.append([k, type(record[k])])
                unique_props_list.append(k)

                if "-" in k:
                    replacement_dict[k] = k.replace("-", "_")
                    new_k = k.replace("-", "_")
                else:
                    new_k = k

                if isinstance(record[k], int):
                    v = f"int64 {new_k} = {i};\n"
                if isinstance(record[k], str):
                    v = f"string {new_k} = {i};\n"

                i += 1
                property_string += v
    print("Unique properties in wgtraffic are")
    # pprint.pprint(unique_props)
    print(property_string)
    print(50*"=")

    unique_props = []
    unique_props_list = []
    property_string = ""
    i = 2
    for record in sysmon:
        keys = record.keys()
        for k in keys:
            if k not in unique_props_list:
                unique_props.append([k, type(record[k])])
                unique_props_list.append(k)

                if "-" in k:
                    replacement_dict[k] = k.replace("-", "_")
                    new_k = k.replace("-", "_")
                else:
                    new_k = k

                if isinstance(record[k], int):
                    v = f"int64 {new_k} = {i};\n"
                if isinstance(record[k], str):
                    v = f"string {new_k} = {i};\n"

                i += 1
                property_string += v
    print("Unique properties in sysmon are")
    # pprint.pprint(unique_props)
    print(property_string)
    print(50*"=")

    unique_props = []
    unique_props_list = []
    property_string = ""
    i = 2
    for record in sepc:
        keys = record.keys()
        for k in keys:
            if k not in unique_props_list:
                unique_props.append([k, type(record[k])])
                unique_props_list.append(k)

                if "-" in k:
                    replacement_dict[k] = k.replace("-", "_")
                    new_k = k.replace("-", "_")
                else:
                    new_k = k

                if isinstance(record[k], int):
                    v = f"int64 {new_k} = {i};\n"
                if isinstance(record[k], str):
                    v = f"string {new_k} = {i};\n"

                i += 1
                property_string += v
    print("Unique properties in SEPC are")
    # pprint.pprint(unique_props)
    print(property_string)
    print(50*"=")

    unique_props = []
    unique_props_list = []
    property_string = ""
    i = 2
    for record in exchange:
        keys = record.keys()
        for k in keys:
            if k not in unique_props_list:
                unique_props.append([k, type(record[k])])
                unique_props_list.append(k)

                if "-" in k:
                    replacement_dict[k] = k.replace("-", "_")
                    new_k = k.replace("-", "_")
                else:
                    new_k = k

                if isinstance(record[k], int):
                    v = f"int64 {new_k} = {i};\n"
                if isinstance(record[k], str):
                    v = f"string {new_k} = {i};\n"

                i += 1
                property_string += v
    print("Unique properties in MsExchange are")
    # pprint.pprint(unique_props)
    print(property_string)
    print(50*"=")

    print(replacement_dict)
