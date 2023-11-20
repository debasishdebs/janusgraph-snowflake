if __name__ == '__main__':
    fname = "D:\\Projects\\Freelancing\\Elysium Analytics\\data\\data\\msexchange_phishing_attack_5d_2020_09_01.json"

    import json
    import dateutil.parser

    data = json.load(open(fname))

    modified_data = []
    for d in data:
        dd = {}
        for k, v in d.items():
            if k != "datetime":
                dd[k] = v
        dd["datetime"] = dateutil.parser.isoparse(d["datetime"]).strftime("%Y-%m-%d %H:%M:%S")
        modified_data.append(dd)

    json.dump(modified_data, open("D:\\Projects\\Freelancing\\Elysium Analytics\\data\\data\\msexchange_phishing_attack_modified.json", "w+"), indent=1)
    parsed = dateutil.parser.isoparse(data[0]["datetime"])
    print(parsed, type(parsed))
    print(parsed.strftime("%Y-%m-%d %H:%M:%S"))
    pass
