
create or replace sequence streaming_edge_id_sequence;
//VALUE_ID varchar(16777216) default edge_id_sequence.nextval,
create or replace TABLE EDGES_DEMO (
	NODE_ID NUMBER(38,0),
	LABEL VARCHAR(16777216),
	VALUE_ID varchar(16777216) default uuid_string(),
	DIRECTION VARCHAR(8),
	VALUE_LABEL VARCHAR(16777216),
	VALUE_PROPERTIES VARIANT,
	MAP_ID NUMBER(38,0),
	MAP_LABEL VARCHAR(16777216)
);

create or replace sequence streaming_node_id_sequence;
create or replace table NODES_DEMO (
  "NODE_ID" number default streaming_node_id_sequence.nextval,
  "LABEL" varchar default null,
  "PROPERTIES" variant default null
);

create or replace sequence streaming_tracker_id_sequence;
create or replace table stream_graph_import_tracker (
    row_id number default streaming_tracker_id_sequence.nextval,
    added_time datetime,
    processed_time datetime,
    table_name array,
    datasource array
);

create or replace TABLE CASE_DEMO (
	ID NUMBER(38,0),
	CASE_ID VARCHAR(16777216),
	NODES VARIANT,
	HOPS NUMBER(38,0),
	STATUS VARCHAR(16777216),
	QUERY VARIANT,
	START_TIME DATETIME,
	PROCESSING_TIME DATETIME,
	QUERY_START_TIME DATETIME,
	QUERY_END_TIME DATETIME,
	DATASOURCES ARRAY,
    QUERY_TRACKER array
);

create or replace TABLE CASE_DEMO_TMP (
	ID NUMBER(38,0),
	CASE_ID VARCHAR(16777216),
	NODES VARCHAR(16777216),
	HOPS NUMBER(38,0),
	STATUS VARCHAR(16777216),
	QUERY VARCHAR(16777216),
	START_TIME DATETIME,
	PROCESSING_TIME DATETIME,
	QUERY_START_TIME DATETIME,
	QUERY_END_TIME DATETIME,
	DATASOURCES VARCHAR(16777216),
    query_tracker VARCHAR(16777216)
);

create or replace table transformed_graph_data_demo_1  (
    element variant,
    element_type varchar,
    case_id varchar,
    ds varchar,
    processing_dttm varchar
);

create or replace table transformed_graph_data_demo_tmp  (
    element varchar,
    element_type varchar,
    case_id varchar,
    ds varchar,
    processing_dttm varchar
);


CREATE OR REPLACE PROCEDURE "SP_CONVERT_VARCHAR_TO_VARIANT_FOR_TRANSFORMED_DATA"(SOURCE_TABLE VARCHAR, TARGET_TABLE VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS
$$
var sql = `insert into ` + TARGET_TABLE + ` select parse_json(element), element_type, case_id, ds, processing_dttm from ` + SOURCE_TABLE + `;`

var result = "";
try {
    var stmt = snowflake.createStatement({sqlText: sql});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    result += "Rows inserted: " + str_result1 + " "
}
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result += "Data conversion failed: "
    result +=  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
}
return result
$$;


create or replace table transformed_graph_data_demo_2  (
    element variant,
    element_type varchar,
    case_id varchar,
    ds varchar,
    processing_dttm varchar
);

create or replace file format json_format
  type = json
  trim_space = true
  file_extension = 'json'
  null_if = ('NULL', 'null')
  STRIP_OUTER_ARRAY = true
  compression = gzip;

create or replace stage tenant5.enriched.snowgraph_streaming_stage_1 FILE_FORMAT = json_format;

create or replace table tenant5.enriched.extracted_snowgraph_data_demo (
    data variant,
    ds varchar,
    case_id varchar,
    processing_dttm datetime
);


CREATE OR REPLACE FUNCTION update_variant(OBJ_1 VARIANT, OBJ_2 VARIANT)
    RETURNS variant
    LANGUAGE JAVASCRIPT
    AS
    $$
    function extend(self, other) {
      if (self == undefined && other != undefined) {
        self = other;
        return self;
      }
      for (var key in other) {
          if (self.hasOwnProperty(key)){
            var data = self[key];
            if (Array.isArray(data)) {
                var updated = data.concat(other[key]);
                updated = [...new Set(updated)];
            }
            else
                var updated = other[key];
            self[key] = updated;
          }
          else {
            self[key] = other[key];
          }
      }
      return self;
    }
    return extend(OBJ_1, OBJ_2)
    $$;


CREATE OR REPLACE FUNCTION create_variant_from_separator(VARIANT_STRING VARIANT, SEP VARCHAR)
    RETURNS VARIANT
    LANGUAGE JAVASCRIPT
    AS
    $$
    function create_variant(obj, sep) {
    if (obj == null)
        return obj;
      var obj_clean = obj.replace("{", "").replace("}", "");
      var pairs = obj_clean.split(sep);

      var element = {}

      var i;
      for (i = 0; i < pairs.length; i++) {
          var p = pairs[i];
          var keyValue = p.split("=");
          element[keyValue[0].trim()] = keyValue[1].trim();
      }
      return element;
    }
    return create_variant(VARIANT_STRING, SEP)
    $$;


CREATE OR REPLACE PROCEDURE "SP_GENERATE_STREAM_NODE_AND_EDGE_IDS"(CASE_ID_VAL VARCHAR, SRC_TRANSFORMED_TBL VARCHAR, TARGET_TRANSFORMED_TBL VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS
$$
var node_id_query = `insert into ` + TARGET_TRANSFORMED_TBL + `  select update_variant(element, object_construct('node_id', streaming_node_id_sequence.nextval)) as element, element_type, case_id, ds, processing_dttm from ` + SRC_TRANSFORMED_TBL + `  where case_id = '` + CASE_ID_VAL + `' and element_type = 'node'`;
var edge_id_query = `insert into ` + TARGET_TRANSFORMED_TBL + `  select update_variant(element, object_construct('edge_id', streaming_edge_id_sequence.nextval)) as element, element_type, case_id, ds, processing_dttm from ` + SRC_TRANSFORMED_TBL + `  where case_id = '` + CASE_ID_VAL + `' and element_type = 'edge'`;

var result = "";
try {
    var stmt = snowflake.createStatement({sqlText: node_id_query});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    result += "Node IDs updated: " + str_result1 + " "
    try {
      var stmt = snowflake.createStatement({sqlText: edge_id_query});
      var res1 = stmt.execute();
      snowflake.execute({sqlText:"COMMIT"})
      res1.next();
      str_result2 = res1.getColumnValue(1);
      result += " Edge IDs updated: " + str_result2 + " "
    }
    catch (err) {
      snowflake.execute({sqlText: "ROLLBACK"});
      result += "Edge IDs Failed: "
      result +=  "Failed: Code: " + err.code + "\n  State: " + err.state;
      result += "\n  Message: " + err.message;
      result += "\nStack Trace:\n" + err.stackTraceTxt;
    }
}
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result += "Node IDs Failed: "
    result +=  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
}
return result
$$;

CREATE OR REPLACE FUNCTION SF_STREAM_GRAPH_EDGE_ENRICHMENT(CASE_ID_VAL VARCHAR)
RETURNS TABLE (VALUE_ID VARCHAR, VALUE_LABEL VARCHAR, VALUE_PROPERTIES VARIANT, MAP_LABEL  VARCHAR, MAP_ID NUMBER, LABEL VARCHAR, NODE_ID NUMBER, DIRECTION VARCHAR)
LANGUAGE SQL
AS
$$
with edges as
(
select
ELEMENT:edge_id :: varchar as value_id,
ELEMENT:edge_label :: varchar as value_label,
ELEMENT as value_properties,
//create_variant_from_separator(ELEMENT:left,',') as lft,
ELEMENT:left as lft,
ELEMENT:right as rght,
//create_variant_from_separator(ELEMENT:right, ',') as rght,
lft:label:: string as left_lbl,
lft:property_key:: string as left_pk,
lft:value::string as left_val,
rght:label:: string as right_lbl,
rght:property_key:: string as right_pk,
rght:value:: string as right_val
from transformed_graph_data_demo_2 where case_id = case_id_val and element_type = 'edge'
)
select distinct
    ed.value_id::varchar,ed.value_label::varchar,ed.value_properties::variant,
    rt.label::varchar as map_label, rt.node_id::number as map_id, lt.label::varchar as label, lt.node_id::number as node_id, 'out'::varchar as direction
 from edges ed
 join NODES_DEMO rt on ed.right_val = case when rt.properties:"hostname" != 'null' then rt.properties:"hostname"
                                                      when rt.properties:"ip" != 'null' then rt.properties:"ip"
                                                      when rt.properties:"emailSubject" != 'null' then rt.properties:"emailSubject"
                                                      when rt.properties:"userName" != 'null' then rt.properties:"userName"
                                                      when rt.properties:"URL" != 'null' then rt.properties:"URL"
                                                      when rt.properties:"fileName" != 'null' then rt.properties:"fileName"
                                  end
 join NODES_DEMO lt on ed.left_val = case when  lt.properties:"hostname" != 'null' then lt.properties:"hostname"
                                                     when lt.properties:"ip" != 'null' then lt.properties:"ip"
                                                     when lt.properties:"emailSubject" != 'null' then lt.properties:"emailSubject"
                                                     when lt.properties:"userName" != 'null' then lt.properties:"userName"
                                                     when lt.properties:"URL" != 'null' then lt.properties:"URL"
                                                      when lt.properties:"fileName" != 'null' then lt.properties:"fileName"
                                  end
  where right_val != 'null' and left_val != 'null'
$$;


CREATE OR REPLACE PROCEDURE "SP_STREAM_GRAPH_EDGE_LOAD"(CASE_ID_VAL VARCHAR,TARGET_EDGE_TBL VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS $$
var sql_edge_command = `merge into ` + TARGET_EDGE_TBL  + ` ef using table(SF_STREAM_GRAPH_EDGE_ENRICHMENT('` + CASE_ID_VAL + `')) et on et.value_id = ef.value_id
when matched then update set ef.value_properties = update_variant(et.value_properties, ef.value_properties), ef.VALUE_LABEL = et.VALUE_LABEL, ef.node_id = et.node_id, ef.map_id = et.map_id, ef.label = et.label, ef.map_label = et.map_label
WHEN NOT MATCHED THEN INSERT (node_id, label, value_id, direction, value_label, value_properties, map_id, map_label)
values (et.node_id, et.label, et.value_id, et.direction, et.value_label, et.value_properties, et.map_id, et.map_label)`;
var result = "";

try {
    var stmt = snowflake.createStatement({sqlText: sql_edge_command});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    str_result2 = res1.getColumnValue(2);
    result = 'Egdes Inserted: ' + str_result1 + ' and Edges Updated: ' + str_result2;
    }
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result =  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
    }
return result
$$;

CREATE OR REPLACE PROCEDURE "SP_STREAM_GRAPH_NODE_LOAD"(CASE_ID_VAL VARCHAR,TARGET_NODE_TBL VARCHAR, TRANSFORMED_TBL VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS $$
var sql_node_command = `merge into ` + TARGET_NODE_TBL  + ` ns using
(
  select distinct element:node_id::string as node_id, element:node_label::string as label, element as properties,
    case when element:"hostname" is not null then element:"hostname"::string
      when element:"ip" is not null then element:"ip"::string
      when element:"emailSubject" is not null then element:"emailSubject"::string
      when element:"userName" is not null then element:"userName"::string
      when element:"URL" is not null then element:"URL"::string
      when element:"fileName" is not null then element:"fileName"::string
    end as identifier
  from ` + TRANSFORMED_TBL + `
  where case_id = '` +  CASE_ID_VAL + `' and element_type = 'node'
) nt on nt.identifier = case when ns.properties:"hostname" is not null then ns.properties:"hostname"::string
                          when ns.properties:"ip" is not null then ns.properties:"ip"::string
                          when ns.properties:"emailSubject" is not null then ns.properties:"emailSubject"::string
                          when ns.properties:"userName" is not null then ns.properties:"userName"::string
                          when ns.properties:"URL" is not null then ns.properties:"URL"::string
                          when ns.properties:"fileName" is not null then ns.properties:"fileName"::string
                        end
when matched then update set ns.properties = update_variant(nt.properties, ns.properties)
WHEN NOT MATCHED THEN INSERT (node_id, label, properties) values (nt.node_id, nt.label, nt.properties)`;
var result = "";

try {
    var stmt = snowflake.createStatement({sqlText: sql_node_command});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    str_result2 = res1.getColumnValue(2);
    result = 'Nodes Inserted: ' + str_result1 + ' and Nodes Updated: ' + str_result2;
    }
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result =  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
    }
return result
$$;


CREATE OR REPLACE PROCEDURE "LOAD_STREAM_NODES_FOR_CASE"(CASE_ID_VAL VARCHAR, TRANSFORMED_TBL VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS $$
var sql_node_command = `update CASE_DEMO
set nodes = (
select array_agg(node) as nodes from (
select object_construct(
  'node_id',element:node_id::numeric,
  'property',
        case when element:node_label = 'IP' then 'ip'
        when element:node_label = 'user' then 'userName'
        when element:node_label = 'host' then 'hostname'
        when element:node_label = 'email' then 'emailSubject'
        when element:node_label = 'URLs' then 'URL'
        else 'fileName' end,
  'value',
        case when element:node_label = 'IP' then element:ip
        when element:node_label = 'user' then element:userName
        when element:node_label = 'host' then element:hostname
        when element:node_label = 'email' then element:emailSubject
        when element:node_label = 'URLs' then element:URL
        else element:fileName end
    ) as node
  from ` + TRANSFORMED_TBL + ` where case_id = '` +  CASE_ID_VAL + `' and element_type = 'node'
  )
  )
  where case_id = '` +  CASE_ID_VAL + `'`;
var result = "";

try {
    var stmt = snowflake.createStatement({sqlText: sql_node_command});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    result = 'Success';
    }
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result =  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
    }
return result
$$;


CREATE OR REPLACE PROCEDURE "STREAMING_EXTRACTOR_TO_TRANSFORMER_DATA"(FILE_NAMES array, STAGE_NAME VARCHAR, EXTRACTION_OUTPUT_TBL VARCHAR)
RETURNS STRING
LANGUAGE JAVASCRIPT
EXECUTE AS OWNER
AS $$
var size = FILE_NAMES.length;
var counter = 0;
var result = size;
var sql_query = "";

if (size == 0)
    return "Nothing inserted as file size is 0";

while (counter < size)
{
    var processing_time = new Date().toLocaleTimeString('en-GB');
    var processing_date = new Date().toLocaleDateString('en-US');
    var processing_datetime = processing_date + " " + processing_time;
    var query = `\nselect $1::variant as data, $1:dataSourceName::string as ds, $1:caseId::string as case_id, '` + processing_datetime + `'::datetime as processing_time from @` + STAGE_NAME + `/` + FILE_NAMES[counter] + `.gz`;
    if (counter < size-1) {
        query += `\nunion all`
    }
    sql_query += query;
    counter += 1;
}

var insert_query = `insert into ` + EXTRACTION_OUTPUT_TBL + ` ` + sql_query;

var result = "";
try {
    var stmt = snowflake.createStatement({sqlText: insert_query});
    var res1 = stmt.execute();
    snowflake.execute({sqlText:"COMMIT"})
    res1.next();
    str_result1 = res1.getColumnValue(1);
    result = `Rows Inserted: ` + str_result1;
    }
catch (err)  {
    snowflake.execute({sqlText: "ROLLBACK"});
    result =  "Failed: Code: " + err.code + "\n  State: " + err.state;
    result += "\n  Message: " + err.message;
    result += "\nStack Trace:\n" + err.stackTraceTxt;
    }
return result;
$$;


CREATE OR REPLACE FUNCTION get_overall_data_sources(DATASOURCES ARRAY)
RETURNS ARRAY
LANGUAGE JAVASCRIPT
AS
$$
function getOverallDataSources(data_sources) {
  if (data_sources.indexOf('all') > -1) {
    // If there is atleast one entry in data sources added for ALL then return ALL so that we don't miss it out in ETL
    return ['all'];
  }
  else {
    unique = [...new Set(data_sources)];
    return unique;
  }
}
return getOverallDataSources(DATASOURCES)
$$;

CREATE OR REPLACE FUNCTION GENERATE_ALL_ETL_QUERY(START_TIME VARCHAR, END_TIME VARCHAR, DATA_SOURCE ARRAY)
RETURNS VARIANT
LANGUAGE JAVASCRIPT
AS
$$

var query = {};
query["startTime"] = START_TIME.toString().substring(0, START_TIME.toString().lastIndexOf("."));
query["endTime"] = END_TIME.toString().substring(0, END_TIME.toString().lastIndexOf("."));
query["dataSource"] = DATA_SOURCE;
query["stream"] = "yes";
query["query"] = {};
query["query"]["user"] = {};
query["query"]["user"]["entityQueries"] = ["all"];
query["query"]["IP"] = {};
query["query"]["IP"]["entityQueries"] = ["all"];
query["query"]["host"] = {};
query["query"]["host"]["entityQueries"] = ["all"];
return query;
$$;

//eventprovider, commandline,parentimage,targetfilename,user_name (user) -> MS_WIN_SYSMON_DEMO
// hostname -> MS_EXCH_MESSAGETRACKING_DEMO
// syslog_event_datetime, syslog_host, src_user, path, filename, msg_host, duration, method. ip_src_port, in_bytes ->WG_FW_NETWORKTRAFFIC_DEMO
show columns like 'timestamp' in table tenant5.enriched.WG_FW_NETWORKTRAFFIC_DEMO;

// datamapper addition
drop table datamappers;
create or replace TABLE DATAMAPPERS (
	DATAMAPPER VARIANT,
	DATASOURCE VARCHAR(16777216),
	NODES VARIANT,
	EDGES VARIANT,
	ANALYZE VARIANT
);
insert into datamappers
select parse_json('{
  "nodes": {
    "host": {
      "maps": {
        "hostname": "Hostname",
        "eventId": "EventID",
        "node_label": "default=host",
        "dataSourceName": "default=sepc"
      },
      "constraints": {
        "unique": "hostname"
      }
    },
    "process": {
      "maps": {
        "fileName": "FileName",
        "filePath": "Path",
        "fullFileName": "FullFileName",
        "Action": "Action",
        "ActionStatus": "ActionStatus",
        "node_label": "default=process",
        "dataSourceName": "default=sepc"
      },
      "constraints": {
        "unique": "fullFileName"
      }
    }
  },
  "edges": {
    "runningProcess": {
      "maps": {
        "eventTime": "EventTime",
        "eventId": "EventID",
        "edge_label": "default=runningProcess",
        "counter": "default=1",
        "dataSourceName": "default=sepc"
      },
      "constraints": {
        "left": "host.hostname(Hostname)",
        "right": "process.fullFileName(FullFileName)"
      }
    }
  },
  "analyze": {
  }
}')::variant as datamapper,
'sepc'::varchar as datasource,
datamapper:nodes::variant as nodes,
datamapper:edges::variant as edges,
datamapper:analyze::variant as analyze;

select * from datamappers;