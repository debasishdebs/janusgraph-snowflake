def rcte_query_gen(anchor, traversal, project, times):
    rcte_query = f"{anchor} \n union all \n \
                select base.root_id, base.oth_id, recursive.lvl + 1 as lvl from edges base \
                join recursive on base.root_id = recursive.oth_id and lvl < {times}"

    query = f"{traversal}, \n recursive as (\n{rcte_query}\n) \n {project}"
    return query


def complete_custom_rcte_query_gen(anchor, traversal, times, rcte_view):
    rcte_query = f"{anchor} \n union all \n \
                select base.root_id, base.oth_id, recursive.lvl + 1 as lvl from edges base \
                join recursive on base.root_id = recursive.oth_id and lvl < {times}"

    query = f"{traversal}, \n {rcte_view} as (\n{rcte_query}\n)"
    return query


def repeat_query_gen(anchor, rcte_view, times):
    rcte_query = f"{anchor} \n union all \n \
                select base.root_id, base.oth_id, recursive.lvl + 1 as lvl from edges base \
                join recursive on base.root_id = recursive.oth_id and lvl < {times}"

    query = f"{rcte_view} as (\n{rcte_query}\n) \n"
    return query
