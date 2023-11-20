with v as
(
with main as
(
select nm.node_id,ne.map_id, 0 as lvl
from nodes_with_edges_all ne
inner join nodes_master nm on nm.node_id = ne.node_id
where nm.properties:ip = '192.168.0.101'
),
level1 as
(
select main.node_id, main.map_id, 1 as lvl
from main
inner join nodes_with_edges_all ne on ne.map_id = main.node_id
inner join nodes_master nm on nm.node_id = main.node_id
inner join nodes_master no on no.node_id = main.map_id
),
level2 as
(
select ne.node_id, ne.map_id,  2 as lvl
from nodes_master nm
inner join nodes_with_edges_all ne on ne.node_id = nm.node_id
inner join level1 l on ne.map_id = l.node_id or ne.node_id = l.map_id
where ne.map_id in (140, 136, 137)
),
repeat3 as
(
select root_id, edge_direction, edge_id, edge_label, edge_properties, oth_id
from nodes_master nm,
(
select node_id as oth_id, value_id as edge_id, 'incoming' as edge_direction, value_label as edge_label, value_properties as edge_properties, map_id as root_id
from nodes_with_edges_all
) ne
where nm.node_id = ne.oth_id
),
repeat3_rcte as
(
select root_id,oth_id, 3 as lvl
from repeat3 base
inner join level2 l on l.map_id = base.root_id
union all
select base.root_id, base.oth_id, r.lvl + 1 as lvl
from repeat3 base
join repeat3_rcte r on base.root_id = r.oth_id and lvl < 5
),
level5 as
(
select ne.node_id, ne.map_id,  5 as lvl
from nodes_master nm
inner join nodes_with_edges_all ne on ne.node_id = nm.node_id
inner join repeat3_rcte l on nm.node_id = l.oth_id
),
level6 as
(
select ne.node_id, ne.map_id,  6 as lvl
from nodes_master nm
inner join nodes_with_edges_all ne on ne.node_id = nm.node_id
inner join level5 l on ne.map_id = l.node_id or ne.node_id = l.map_id
inner join nodes_master no on no.node_id = ne.map_id
where ne.value_properties:counter = '1'
)
select * from level1
union all
select * from level2
union all
select * from repeat3_rcte
union all
select * from level5
union all
select * from level6

)
select distinct v.*, ns.label as src_label, ns.properties as src_properties, no.label as dst_label, no.properties as dst_properties, ne.value_id, ne.value_label, ne.value_properties
from v
inner join nodes_master ns on ns.node_id = v.node_id
inner join nodes_master no on no.node_id = v.map_id
inner join nodes_with_edges_all ne on (ne.node_id = v.node_id and ne.map_id = v.map_id) or (ne.map_id = v.node_id and ne.node_id = v.map_id);