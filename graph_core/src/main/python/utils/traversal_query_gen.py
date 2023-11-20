def code_gen(level, filters, overall_filter):
    if level >= 1:
        if len(overall_filter.strip()) > 0:
            overall_filter = "where " + overall_filter
        sql_script_top = "with main as \n( select id, out_id from tmp_outgoing_nodes " + overall_filter.strip() + " ),"
        sql_script_middle = ""
        sql_script_bottom = ""
        for itr in range(level):
            if itr == 0 :
                clause = ""
                if len(filters[itr].strip()) > 0 :
                    clause = "where " + filters[itr]
                sql_script_middle += "\nlevel"+ str(itr+1) + " as \n( select main.id, main.out_id, '" + str(itr+1) + "' as lvl from main " + clause.strip() + " )"
                sql_script_bottom += "\nselect * from level" + str(itr+1)
                if itr < level -1:
                    sql_script_middle += ','
                    sql_script_bottom += "\nunion all"
            else:
                clause = ""
                if len(filters[itr].strip()) > 0 :
                    clause = "and " + filters[itr]
                else:
                    clause = ""
                sql_script_middle += "\nlevel"+ str(itr+1) + " as \n( select main.id, main.out_id, '" + str(itr+1) + "' as lvl from main" \
                                                                                                                     " join level" + str(itr) + " on main.id = level" + str(itr) + ".out_id " + clause.strip() + ")"
                sql_script_bottom += "\nselect * from level" + str(itr+1)
                if itr < level -1:
                    sql_script_middle += ','
                    sql_script_bottom += "\nunion all"
    else:
        return None
    return sql_script_top + sql_script_middle + sql_script_bottom


if __name__ == '__main__':

    traversal = {
        "anchor": {
            "T.id": 101,
            "op": "eq"
        },
        "traversal": {
            1: {
                "ip": ['192.168.0.102', '192.168.0.105', '192.168.0.113', '192.168.0.114', '192.168.0.119'],
                "op": "within"
            },
            2: {
                "ip": ['192.168.0.103', '192.168.0.131', '192.168.0.107', '192.168.0.120', '192.168.0.121'],
                "op": "within"
            },
            3: {
                "T.id": ['104', '106', '118', '126'],
                "op": "within"
            },
            4: {
                "T.id": ['122', '128', '130'],
                "op": "gte"
            },
            5: {
                "T.id": ['192.168.0.124', '192.168.0.129', '192.168.0.133'],
                "op": "within"
            },
            6: {
                "T.id": ['192.168.0.129', '192.168.0.133'],
                "op": "between"
            },
            7: {
                "T.label": ['IP'],
                "op": "eq"
            }
        }
    }

    traversal = {
        "anchor": {
            "PROPERTIES": {"ip": "192.168.0.101"}
        }
    }

    sql_code = code_gen(3, ["2=2", "3=3", "4=4"], "1=1")
    print(sql_code)
