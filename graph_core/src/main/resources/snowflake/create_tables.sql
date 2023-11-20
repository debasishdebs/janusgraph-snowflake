
create or replace TABLE EDGES_FINAL_DEMO (
	NODE_ID NUMBER(38,0),
	LABEL VARCHAR(16777216),
	VALUE_ID VARCHAR(16777216),
	DIRECTION VARCHAR(8),
	VALUE_LABEL VARCHAR(16777216),
	VALUE_PROPERTIES VARIANT,
	MAP_ID NUMBER(38,0),
	MAP_LABEL VARCHAR(16777216)
);

create or replace table nodes_final_demo (
  "NODE_ID" number default null,
  "LABEL" varchar default null,
  "PROPERTIES" variant default null
);

create or replace TABLE CASE_FINAL_DEMO (
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
	DATASOURCES ARRAY
);

----------------------------

create or replace table edges_final_demo as
select node_id, label, l.value:id :: string as VALUE_ID, 'outEdges' as Direction, l.value:label :: string AS VALUE_LABEL,
       l.value:properties :: variant AS VALUE_PROPERTIES, l.value:target:id :: numeric AS MAP_ID, l.value:target:label::varchar as map_label
from (select * from nodes) n,
      lateral flatten(input => n."outEdges")l
union all
select node_id, label, l.value:id :: string as VALUE_ID, 'inEdges' as Direction, l.value:label :: string AS VALUE_LABEL,
       l.value:properties :: variant AS VALUE_PROPERTIES, l.value:source:id :: numeric AS MAP_ID, l.value:target:label::varchar as map_label
from (select * from nodes) n,
      lateral flatten(input => n."inEdges")l;

create or replace table nodes_with_vertices_all as
select node_id, label, 'inVertices' as Direction, l.value:id :: numeric AS MAP_ID
from (select * from nodes) n,
      lateral flatten(input => n."inVertices")l
union all
select node_id, label, 'outVertices' as Direction, l.value:id :: numeric AS MAP_ID
from (select * from nodes) n,
      lateral flatten(input => n."outVertices")l;

------------------------------
create or replace table nodes_with_outedges as
select node_id, label, l.value:id :: string as VALUE_ID, l.value:label :: string AS VALUE_LABEL,
       l.value:properties :: variant AS VALUE_PROPERTIES, l.value:target:id :: numeric AS MAP_ID
from (select * from nodes) n,
      lateral flatten(input => n."outEdges")l;

create or replace table nodes_with_inedges as
select node_id, label, l.value:id :: string as VALUE_ID, l.value:label :: string AS VALUE_LABEL,
       l.value:properties :: variant AS VALUE_PROPERTIES, l.value:source:id :: numeric AS MAP_ID
from (select * from nodes) n,
      lateral flatten(input => n."inEdges")l;

create or replace table nodes_master as
select distinct node_id, label, properties from nodes;