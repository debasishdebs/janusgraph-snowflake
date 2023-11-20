from flask import Flask, request, jsonify, g
from server.GraphAppController import GraphAppController
from utils.commons import Utilities as U, APPLICATION_PROPERTIES, API_UTILITIES as apiU
from time import sleep
import threading
from flask_cors import CORS, cross_origin
import datetime as dt
import requests


config = U.load_properties(APPLICATION_PROPERTIES)
app = Flask(__name__)

cors = CORS(app, resources={r"/startCaseExport/*": {"origins": "*"},
                            r"/getCaseStatus/*": {"origins": "*"},
                            r"/getGraphForId/*": {"origins": "*"},
                            r"/getGraphForCaseId/*": {"origins": "*"},
                            r"/isQueryExported/*": {"origins": "*"},
                            r"/getGraphForProperty/*": {"origins": "*"},
                            r"/collapseGraph/*": {"origins": "*"},
                            r"/getVertex/*": {"origins": "*"},
                            r"/getRecentData/*": {"origins": "*"},
                            r"/getDeltaForRawAndGraphData/*": {"origins": "*"},
                            r"/updateProcessedTime/*": {"origins": "*"},
                            r"/updateAddedTimeToTrackingTable/*": {"origins": "*"},
                            r"/getAllCaseIds/*": {"origins": "*"}}, support_credentials=True)


@app.before_request
def before_first_request():
    print("Initializing the connection to Snowflake db")
    g.controller = GraphAppController(config)
    print("DB connection created and stored")


@app.route("/getDeltaForRawAndGraphData",  methods=["POST"])
def get_delta_for_raw_and_graph_data():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)
    return jsonify(g.controller.get_delta_between_raw_and_graph_data())


@app.route("/updateProcessedTime", methods=["POST"])
def update_processed_time():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)
    params = request.get_json()

    processed_time = params["processedTime"]
    processed_proto_time = U.convert_time_string_to_proto_time(processed_time)
    return jsonify(g.controller.update_processed_time_to_tracking_table(processed_proto_time))


@app.route("/updateAddedTimeToTrackingTable", methods=["POST"])
def update_added_time_to_tracking_table():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)
    params = request.get_json()

    tables = params["tables"]
    added_time = params["addedTime"]
    added_proto_time = U.convert_time_string_to_proto_time(added_time)

    data_sources = []
    for tbl in tables:
        if tbl == "MS_WIN_SECURITYAUDITING" or "MS_WIN_SECURITYAUDITING_NETTRAFFIC":
            data_sources.append("windows")
        if tbl == "MS_WIN_SYSMON":
            data_sources.append("sysmon")
        if tbl == "MS_EXCH_CONNECTIVITY" or "MS_EXCH_MESSAGETRACKING":
            data_sources.append("msexchange")
        if tbl == "WG_FW_EVENTSALARMS" or tbl == "WG_FW_NETFLOW" or tbl == "WG_FW_NETWORKTRAFFIC":
            data_sources.append("watchguard")
        if tbl == "SYM_ES_ENDPOINTPROTECTIONCLIENT" or tbl == "SYM_ES_NETWORKPROTECTION":
            data_sources.append("sepc")
    print(f"Data sources: {data_sources}")
    data_sources = list(set(data_sources))
    print(f"After, {data_sources}, {len(data_sources)}")
    if len(data_sources) == 5:
        data_sources = ["all"]

    return jsonify(g.controller.update_added_time_to_tracking_table(tables, added_proto_time, data_sources))


@app.route("/startCaseExport", methods=["POST"])
def start_case_export():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    print("Starting case export")

    params = request.get_json()
    print("Params is ", params)

    stream = True if "stream" in params else False
    if stream:
        print("Since its streaming, I'm going to update the processed time to now")
        base_url = config["flask.server.host"]
        base_port = config["flask.server.port"]
        r = requests.post(f'http://{base_url}:{base_port}/updateProcessedTime', json={"processedTime": dt.datetime.now().strftime(apiU.API_DATE_FORMAT)})
        print(f"API Response code: {r.status_code}")
        print(f"Response of update of ProcessedTime: {r.json()}")
        print(100*"-")

    controller = g.controller

    case_id = U.generate_case_id()
    if "case_id" not in params:
        params.update({"case_id": case_id})

    startTime = apiU.__get_start_time__(params)
    endTime = apiU.__get_end_time__(params)

    params.update({"startTime": startTime})
    params.update({"endTime": endTime})

    print("Starting case export, sleeping now for 2sec")
    sleep(2)

    t = threading.Thread(target=controller.start_case_import, kwargs={"case_info": params})
    print("Created thread")
    t.start()
    print("Started thread")
    print("Didn't wait for import to be over, hopefully its running in background")
    print("Case export has started already")
    print("Sleeping for 5sec then I'll return")
    sleep(5)
    print(f"Is Thread alive? {t.is_alive()}")

    return jsonify({
        "caseId": case_id,
        "status": "success"
    })


@app.route("/isQueryExported", methods=["POST"])
def is_query_exported():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()
    print(params)

    result = g.controller.get_status_for_query_export(params)

    return jsonify({"status": result.status, "caseId": result.caseId})


@app.route("/getAllCaseIds", methods=["POST"])
def get_all_case_ids():
    if request.method != "POST":
        return jsonify("Expecting POST queruest only")

    result = g.controller.get_all_case_ids()
    case_ids = []
    for res in result:
        case_ids.append(res.caseId)
    print(case_ids)
    return jsonify({"case_ids": case_ids})


@app.route("/getCaseStatus", methods=["POST"])
def get_case_export_status():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    params = request.get_json()

    if params is None:
        return jsonify("BAD Request, got None as params, expecting something")

    controller = g.controller

    if isinstance(params["case_id"], str):
        return jsonify("BAD Request, expecting list of CaseId, not single string")

    case_status = controller.get_case_status(params)

    case_statuses = {}
    for case_id in case_status.status:
        case_obj = case_status.status[case_id]

        case_statuses[case_id] = {
            "case_id": str(case_obj.caseId),
            "status": str(case_obj.status),
            "query": U.convert_case_information_to_python_query_dict(case_obj.query),
            "others": U.convert_proto_map_to_python_dict(case_obj.others),
            "nodes": len(U.convert_nodes_in_record_proto_to_python_list(case_obj.nodes)),
            "exportTime": U.convert_proto_time_to_time_string(case_obj.queryExportTime),
            "processingTime": U.convert_proto_time_to_time_string(case_obj.processingTime),
            "startTime": U.convert_proto_time_to_time_string(case_obj.startTime),
            "endTime": U.convert_proto_time_to_time_string(case_obj.endTime),
            "dataSources": U.convert_proto_list_to_python_list(case_obj.dataSources)
        }

    print(case_statuses)
    return jsonify(case_statuses)


@app.route("/getRecentData", methods=["POST"])
def get_recent_data():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()

    search_id = int(params["id"]) if "id" in params else None
    search_for = params["search_for"] if "search_for" in params else None
    search_by = params["search_value"] if "search_value" in params else None
    case_id = params["caseId"] if "caseId" in params else None

    ID_SEARCH = False
    PROPERTY_SEARCH = False
    CASE_SEARCH = False
    if search_id is not None:
        # if search_by or search_for is None :
        #     return jsonify({"ERROR": "Pass either ID or search_for/search_value pair to identify root node"})
        ID_SEARCH = True
    else:
        if case_id is not None:
            CASE_SEARCH = True
        else:
            PROPERTY_SEARCH = True

    if not ID_SEARCH or not PROPERTY_SEARCH or not CASE_SEARCH:
        return jsonify({"ERROR": "Pass ID/Search/Case for recentDataFilter"})

    startTime, endTime = apiU.__get_start_end_time_for_recent_data_api__(params)
    hops = params["hops"] if "hops" in params else 1
    dedup = (params["dedup"] == "true") if "dedup" in params else True

    assert (ID_SEARCH is not False) or (PROPERTY_SEARCH is not False) or (CASE_SEARCH is not False)

    if ID_SEARCH:
        result = g.controller.generate_ego_network_for_vertex_id(search_id, None, hops, None, startTime, endTime, None, dedup)
    elif PROPERTY_SEARCH:
        result = g.controller.generate_ego_network_for_vertex_property(search_for, search_by, None, hops, None, startTime, endTime, None, dedup)
    else:
        result = g.controller.generate_ego_network_for_case_id(case_id, dedup, None, startTime, endTime)

    print(f"Executed in {(dt.datetime.now() - start).total_seconds()} with nodes: {len(result['nodes'])} edges: {len(result['edges'])}")
    return jsonify(result)


@app.route("/getGraphForId", methods=["POST"])
def get_graph_for_id():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    # selection is not implemented
    # need to refresh data

    params = request.get_json()
    search_id = int(params["id"])

    direction = params["direction"] if "direction" in params else "both"
    selection = apiU.__get_selection__(params)
    hops = params["hops"] if "hops" in params else 1
    data_sources = apiU.__get_data_sources__(params)
    start_time = apiU.__get_start_time__(params)
    end_time = apiU.__get_end_time__(params)
    dedup = (params["dedup"] == "true") if "dedup" in params else True

    print(params)
    print(search_id, selection, hops, data_sources, start_time, end_time)
    result = g.controller.generate_ego_network_for_vertex_id(search_id, selection, hops, data_sources, start_time, end_time, direction, dedup)

    print(result)
    print(f"Executed in {(dt.datetime.now() - start).total_seconds()} with nodes: {len(result['nodes'])} edges: {len(result['edges'])}")
    return jsonify(result)


@app.route("/getGraphForCaseId", methods=["POST"])
def get_graph_for_case_id():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()
    case_id = params["caseId"]

    # selection = __get_selection__(params)
    # hops = params["hops"] if "hops" in params else 1
    data_sources = apiU.__get_data_sources__(params)
    start_time = apiU.__get_start_time__(params)
    end_time = apiU.__get_end_time__(params)
    dedup = (params["dedup"] == "true") if "dedup" in params else True

    print(params)
    # print(case_id, selection, hops, data_sources, start_time, end_time)
    result = g.controller.generate_ego_network_for_case_id(case_id, dedup, data_sources, start_time, end_time)

    print(f"Executed in {(dt.datetime.now() - start).total_seconds()} with nodes: {len(result['nodes'])} edges: {len(result['edges'])}")
    return jsonify(result)


@app.route("/getGraphForProperty", methods=["POST"])
def get_graph_for_property():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()
    search_for = params["search_for"]
    search_by = params["search_value"]

    direction = params["direction"] if "direction" in params else "both"
    selection = apiU.__get_selection__(params)
    hops = params["hops"] if "hops" in params else 1
    data_sources = apiU.__get_data_sources__(params)
    start_time = apiU.__get_start_time__(params)
    end_time = apiU.__get_end_time__(params)
    dedup = (params["dedup"] == "true") if "dedup" in params else True

    print(params)
    print(search_for, search_by, selection, hops, data_sources, start_time, end_time)
    result = g.controller.generate_ego_network_for_vertex_property(search_for, search_by, selection, hops, data_sources, start_time, end_time, direction, dedup)

    print(f"Executed in {(dt.datetime.now() - start).total_seconds()} with nodes: {len(result['nodes'])} edges: {len(result['edges'])}")

    return jsonify(result)


@app.route("/collapseGraph", methods=["POST"])
def collapse_graph():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()

    if "collapse_by" in params:
        collapse_by = params["collapse_by"]

        id_num = params["id"]
        data_sources = params["data_source_name"] if "data_source_name" in params else None
        data_sources = data_sources.split(",") if data_sources is not None else None
        username = params["username"] if "username" in params else None
        timeWindow = params["timeWindow"] if "timeWindow" in params else None
        URLclicked = params["URL"] if "URL" in params else None
        process = params["process"] if "process" in params else None
        startTime = params["startTime"] if "startTime" in params else None
        startTime = None if startTime is None or startTime == "null" else startTime
        endTime = params["endTime"] if "endTime" in params else None
        endTime = None if endTime is None or endTime == "null" else endTime
        try:
            startTime = dt.datetime.strptime(startTime, apiU.API_DATE_FORMAT) if startTime is not None else None
            endTime = dt.datetime.strptime(endTime, apiU.API_DATE_FORMAT) if endTime is not None else None
        except ValueError:
            try:
                startTime = dt.datetime.strptime(startTime, apiU.API_DATE_FORMAT_2) if startTime is not None else None
                endTime = dt.datetime.strptime(endTime, apiU.API_DATE_FORMAT_2) if endTime is not None else None
            except ValueError:
                from dateutil.parser import parse
                startTime = parse(startTime) if startTime is not None else None
                endTime = parse(endTime) if endTime is not None else None

        if collapse_by == "user_process_user":
            # data = collapse_to_user_process_user_relation(id_num, janusgraph, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": -1,
                          "status": "Failure"},
                "data": "Not implemented user_process_user api"}

        elif collapse_by == "process_user":
            print("Got process user")
            data = g.controller.collapse_to_process_user_relation(id_num, startTime, endTime, data_sources)

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "user_process":
            data = g.controller.collapse_to_user_process_relation(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "user_email_user":
            data = g.controller.collapse_to_user_email_user_relation(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "user_URL_user":
            data = g.controller.collapse_user_URL_user_relation(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "ip_user":
            data = g.controller.collapse_ip_user_relation(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "process_ip":
            data = g.controller.collapse_process_ip_relation(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "collapse_process_communicated":
            # data = collapse_process_communicated(id_num, janusgraph, startTime, endTime, timeWindow)
            print("Computed gremlin response")

            response = {
                "error": {"code": -1,
                          "status": "Failure"},
                "data": "Not implemented collapse_process_communicated"}

            data = g.controller.collapse_to_process_ip_communicated(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "process_downloaded_on":
            data = g.controller.collapse_process_downloaded_on(id_num, startTime, endTime, data_sources)
            print("Computed gremlin response")

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "user_touched_host":
            data = g.controller.collapse_user_loggedin_host_relation(id_num, startTime, endTime, data_sources)

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "collapse_host_user":
            data = g.controller.collapse_user_loggedin_host_relation(id_num, startTime, endTime, data_sources)

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "collapse_user_clicked_url":
            data = g.controller.collapse_user_clicked_url(id_num, startTime, endTime, data_sources)

            response = {
                "error": {"code": 0,
                          "status": "Success"},
                "edges": data["edges"],
                "nodes": data["nodes"]}

        elif collapse_by == "collapse_user_url_process":
            if username is None and URLclicked is None:
                response = {
                    "error": {"code": 1,
                              "status": "Collapse User-URL-Process needs Username and URL parameter. Missing in API call"},
                    "data": {}}
            else:
                # data = collapse_user_click_url_download_process(username, URLclicked, janusgraph, startTime, endTime)
                response = {
                    "error": {"code": -1,
                              "status": "Failure"},
                    "data": "Not implemented collapse_user_url_process"}

        elif collapse_by == "background_process":
            if username is None and URLclicked is None and process is None:
                response = {
                    "error": {"code": 1,
                              "status": "Collapse Background-Process needs Username, URL and Process parameter. Missing in API call"},
                    "data": {}}
            else:
                # data = collapse_get_host_with_background_process(username, URLclicked, process, janusgraph, startTime,
                #                                                  endTime)
                response = {
                    "error": {"code": -1,
                              "status": "Failure"},
                    "data": "Not implemented background_process"}

        else:
            response = {
                "error": {"code": 1,
                          "status": "Invalid collapse_by parameter passed. Expecting "
                                    "user_process_user/user_process/user_process/user_email_user/user_URL_user"},
                "data": {}}

    else:
        response = {
            "error": {"code": 1,
                      "status": "Failed as collapse_by is compulsory requirement for collapse_data api"},
            "data": {}}

    end = dt.datetime.now()
    print("Successfully returned data in {}".format((end-start).total_seconds()))

    return jsonify(response)


@app.route("/getVertex", methods=["POST"])
def get_vertex():
    if request.method != 'POST':
        return jsonify("Expecting only POST request got " + request.method)

    start = dt.datetime.now()

    params = request.get_json()
    search_for = params["search_for"] if "search_for" in params else None
    search_by = params["search_value"] if "search_by" in params else None
    search_id = params["node_id"] if "node_id" in params else None

    if search_by is None and search_for is None and search_id is None:
        return jsonify("failure please pass one of search by/for or node_id")

    else:
        if search_id is not None:
            result = g.controller.get_vertex_by_id(search_id)
        else:
            result = g.controller.get_vertex_by_property(search_for, search_by)

    print(f"Executed in {(dt.datetime.now() - start).total_seconds()}")
    return jsonify(result)


if __name__ == '__main__':
    url = config["flask.server.host"]
    port = int(config["flask.server.port"])
    app.run(debug=False, use_reloader=False, host=url, port=port)
