with tmp as
(
  with main as
  ( select * from nodes_with_edges_all where node_id = 101 ),
  level1 as
  (
    select main.*, 1 as lvl from main inner join nodes_master nm on nm.node_id = main.map_id
    where nm.properties:ip in ('192.168.0.102', '192.168.0.105', '192.168.0.113', '192.168.0.114', '192.168.0.119')
  ),
  level2 as
  (
    select ne.*, 2 as lvl from nodes_master nm inner join level1 on nm.node_id = level1.map_id inner join nodes_with_edges_all ne on ne.node_id = nm.node_id
    inner join nodes_master nm1 on nm1.node_id = ne.map_id
    where nm1.properties:ip in ('192.168.0.103', '192.168.0.131', '192.168.0.107', '192.168.0.120', '192.168.0.121')
    and ne.value_properties:counter = 1
  ),
  // Cols: node_id, label, value_id, direction, value_label, value_properties, map_id, lvl
  outgoing as
  (
    select ne.node_id, ne.label, ne.value_id, ne.direction, ne.value_label, ne.value_properties, ne.map_id  from nodes_master nm,
   (
     select * from nodes_with_edges_all ne where value_properties:counter=0
   ) ne
    where nm.node_id = ne.map_id
  ),
  outgoing_rcte as
  (
    -- Anchor Clause
    select base.node_id, base.label, base.value_id, base.direction, base.value_label, base.value_properties, base.map_id, 3 as lvl
      from outgoing base, level2 l2
      where base.node_id = l2.map_id
    union all
    -- Recursive Clause
    select base.node_id, base.label, base.value_id, base.direction, base.value_label, base.value_properties, base.map_id, outgoing_rcte.lvl + 1 as lvl
      from outgoing base
      join outgoing_rcte
      on base.node_id = outgoing_rcte.map_id and outgoing_rcte.lvl < 5
  )
  select *, 'level1' as tbl from level1
  union all
  select *, 'level2' as tbl from level2
  union all
  select *, 'level' || lvl as tbl from outgoing_rcte
)
select * from tmp
order by lvl;