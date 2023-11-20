from query.steps.RepeatStep import RepeatStep
from query.steps.TraversalStep import TraversalStep
from query.steps.CoalesceStep import CoalesceStep
from query.steps.UnionStep import UnionStep
from query.steps.MixedTraversalStep import MixedTraversalStep
from typing import List, Optional
from query.steps.ProjectStep import ProjectStep


class IterationStepWrapper(object):
    ITERATE_QUERY = None
    TOTAL_STEPS = None
    CENTRIC_QUERY = None

    SELECTION_BY = None
    PROPERTIES_STEP = False
    ERROR = "NA"

    def __init__(self, mixed_step=None, repeat_step=None, traversal_step=None, coalesce_step=None, union_step=None):
        self.MIXED_STEP: MixedTraversalStep = mixed_step

        self.REPEAT_STEPS: List[RepeatStep] = list()
        if repeat_step is not None:
            self.REPEAT_STEPS.append(repeat_step)

        self.TRAVERSAL_STEPS: List[TraversalStep] = list()
        if traversal_step is not None:
            self.TRAVERSAL_STEPS.append(traversal_step)

        self.COALESCE_STEPS: List[CoalesceStep] = list()
        if coalesce_step is not None:
            self.COALESCE_STEPS.append(coalesce_step)

        self.UNION_STEPS: List[UnionStep] = list()
        if union_step is not None:
            self.UNION_STEPS.append(union_step)

    def add_centric_step(self, centric_step):
        self.CENTRIC_QUERY = centric_step.FILTER_QUERY
        return self

    def get_query(self):
        return self.ITERATE_QUERY

    def with_selection_step(self, step):
        # print("Here")
        self.SELECTION_BY = step
        # print(f"Select by {self.SELECTION_BY}")
        if str(step) in ["properties", "last_id"]:
            self.PROPERTIES_STEP = True
        return self

    def get_selection_step(self) -> Optional[ProjectStep]:
        return self.SELECTION_BY

    def add_repeat_step(self, repeat_step):
        self.REPEAT_STEPS.append(RepeatStep(repeat_step))
        return self

    def add_traversal_step(self, traversal_step: list):
        self.TRAVERSAL_STEPS.append(TraversalStep(traversal_step))
        return self

    def add_coalesce_step(self, traversal_step: list):
        self.COALESCE_STEPS.append(CoalesceStep(traversal_step))
        return self

    def add_union_step(self, traversal_step: list):
        self.UNION_STEPS.append(UnionStep(traversal_step))
        return self

    def execute(self):
        self._generate_number_of_iterations_()
        self._build_query_component_()
        return self

    def _generate_number_of_iterations_(self):
        l = self.MIXED_STEP.total_steps() if self.MIXED_STEP is not None else 0
        l += len(self.REPEAT_STEPS)
        l += len(self.TRAVERSAL_STEPS)
        l += len(self.COALESCE_STEPS)
        l += len(self.UNION_STEPS)
        self.TOTAL_STEPS = l
        return self

    def _build_query_component_(self):
        # print(self.MIXED_STEP, "mixes step")
        # print(self.REPEAT_STEPS, "repeat step")
        # print(self.TRAVERSAL_STEPS, "traversal step")
        # print(self.COALESCE_STEPS, "coalesce step")
        # print(self.UNION_STEPS, "union step")
        # print(self.CENTRIC_QUERY, "Centric query inside iteration step")

        if self.MIXED_STEP is not None:
            assert len(self.REPEAT_STEPS) == 0
            assert len(self.TRAVERSAL_STEPS) == 0
            assert self.TOTAL_STEPS == self.MIXED_STEP.total_steps()

            self.MIXED_STEP.CENTRIC_QUERY = self.CENTRIC_QUERY
            self.MIXED_STEP.execute()
            aggregated_query = self.MIXED_STEP.MIXED_QUERY
            views = self.MIXED_STEP.VIEWS

        else:
            assert self.MIXED_STEP is None
            if len(self.REPEAT_STEPS) != 0:

                assert len(self.TRAVERSAL_STEPS) == 0
                assert self.TOTAL_STEPS == len(self.REPEAT_STEPS)

                queries = []
                aggregated_query = ""
                views = []
                iter_num = 2
                for i in range(len(self.REPEAT_STEPS)):
                    # if iter_num == 0:
                    #     iter_num = i+1

                    repeat_step = self.REPEAT_STEPS[i]
                    repeat_view = "repeat{lvl}".format(lvl=iter_num)
                    repeat_rcte_view = "repeat{lvl}_rcte".format(lvl=iter_num)

                    repeat_step.RCTE_MAIN_VIEW = repeat_view
                    repeat_step.RCTE_REPEAT_VIEW = repeat_rcte_view
                    repeat_step.ITERATION_NUM = iter_num
                    repeat_step.CENTRIC_QUERY = self.CENTRIC_QUERY
                    repeat_step.execute()

                    repeat_rcte_query = repeat_step.REPEAT_QUERY
                    if repeat_rcte_view not in views:
                        views.append(repeat_rcte_view)
                    # repeat_times = repeat_step.REPEAT_TIMES
                    # anchor = self.CENTRIC_QUERY
                    #
                    # rcte_query = complete_custom_rcte_query_gen(anchor, repeat_query, repeat_times, repeat_rcte_view)
                    queries.append(repeat_rcte_query)

                    # print("====START RCTE QUERY====")
                    # print(repeat_rcte_query)
                    # print("====END RCTE QUERY====")

                    if aggregated_query == "":
                        aggregated_query += f"with main as ({self.CENTRIC_QUERY}), \n"
                    aggregated_query += repeat_rcte_query
                    aggregated_query += "\n"

                    # print(f"Adding comma i: {i}, tot repeat steps: {len(self.REPEAT_STEPS)}")
                    if i < len(self.REPEAT_STEPS)-1:
                        # print("Added comma to " + aggregated_query)
                        aggregated_query += ","

                    iter_num += repeat_step.REPEAT_TIMES

            elif len(self.TRAVERSAL_STEPS) != 0:
                # print("Homogenous traversal in iteratonstepwrapper")

                assert len(self.REPEAT_STEPS) == 0
                assert self.TOTAL_STEPS == len(self.TRAVERSAL_STEPS)
                # print(self.TOTAL_STEPS, "inside traversal step")
                # print(self.TRAVERSAL_STEPS)

                aggregated_query = ""
                queries = []
                views = []
                iter_num = 2
                for i in range(len(self.TRAVERSAL_STEPS)):
                    # iter_num += 1

                    traversal_step = self.TRAVERSAL_STEPS[i]
                    traversal_view = "level{lvl}".format(lvl=iter_num)

                    # print(f"reinitializing traversal with view: {traversal_view}, iter: {iter_num}")

                    traversal_step.TRAVERSAL_VIEW = traversal_view
                    traversal_step.ITERATION_NUM = iter_num
                    traversal_step.execute()

                    traversal_query = traversal_step.TRAVERSAL_QUERY

                    queries.append(traversal_query)
                    if traversal_view not in views:
                        views.append(traversal_view)

                    if aggregated_query == "":
                        aggregated_query += f"with main as ({self.CENTRIC_QUERY}), \n"
                    aggregated_query += traversal_query
                    aggregated_query += "\n"

                    # print(f"Adding comma i: {i}, tot traversal steps: {len(self.TRAVERSAL_STEPS)}")
                    if i < len(self.TRAVERSAL_STEPS)-1:
                        # print("Added comma to " + aggregated_query)
                        aggregated_query += ","

                    iter_num += 1

            elif len(self.COALESCE_STEPS) != 0:
                # print("Homogenous coalesce in iteratonstepwrapper")

                assert len(self.REPEAT_STEPS) == 0
                assert self.TOTAL_STEPS == len(self.COALESCE_STEPS)
                # print(self.TOTAL_STEPS, "inside coalesce step")
                # print(self.COALESCE_STEPS)

                aggregated_query = ""
                queries = []
                views = []
                iter_num = 2
                for i in range(len(self.COALESCE_STEPS)):
                    # iter_num += 1

                    coalesce_step = self.COALESCE_STEPS[i]
                    coalesce_view = "level{lvl}".format(lvl=iter_num)

                    # print(f"reinitializing coalesce with view: {coalesce_view}, iter: {iter_num}")

                    coalesce_step.COALESCE_VIEW = coalesce_view
                    coalesce_step.ITERATION_NUM = iter_num
                    coalesce_step.execute()

                    traversal_query = coalesce_step.COALESCE_QUERY

                    queries.append(traversal_query)
                    if coalesce_view not in views:
                        views.append(coalesce_view)

                    if aggregated_query == "":
                        aggregated_query += f"with main as ({self.CENTRIC_QUERY}), \n"
                    aggregated_query += traversal_query
                    aggregated_query += "\n"

                    # print(f"Adding comma i: {i}, tot traversal steps: {len(self.COALESCE_STEPS)}")
                    if i < len(self.COALESCE_STEPS)-1:
                        # print("Added comma to " + aggregated_query)
                        aggregated_query += ","

                    iter_num += 1

            else:
                # print("Homogenous union in iteratonstepwrapper")

                assert len(self.REPEAT_STEPS) == 0
                assert self.TOTAL_STEPS == len(self.UNION_STEPS)
                # print(self.TOTAL_STEPS, "inside union step")
                # print(self.UNION_STEPS)

                aggregated_query = ""
                queries = []
                views = []
                iter_num = 2
                for i in range(len(self.UNION_STEPS)):
                    # iter_num += 1

                    union_step = self.UNION_STEPS[i]
                    union_view = "level{lvl}".format(lvl=iter_num)

                    # print(f"reinitializing union with view: {union_view}, iter: {iter_num}")

                    union_step.UNION_VIEW = union_view
                    union_step.ITERATION_NUM = iter_num
                    union_step.execute()

                    union_query = union_step.UNION_QUERY

                    queries.append(union_query)
                    if union_view not in views:
                        views.append(union_view)

                    if aggregated_query == "":
                        aggregated_query += f"with main as ({self.CENTRIC_QUERY}), \n"
                    aggregated_query += union_query
                    aggregated_query += "\n"

                    # print(f"Adding comma i: {i}, tot traversal steps: {len(self.UNION_STEPS)}")
                    if i < len(self.UNION_STEPS)-1:
                        # print("Added comma to " + aggregated_query)
                        aggregated_query += ","

                    iter_num += 1

        if self.PROPERTIES_STEP:
            views = [views[-1]]
        else:
            views = ["main"] + views
        for i in range(len(views)):
            view = views[i]
            if i == 0:
                q = f"select * from {view}\n"
            else:
                q = f"union all\nselect * from {view}\n"
            aggregated_query += q

        self.ITERATE_QUERY = aggregated_query

        # print("Final iteration query is")
        # print(self.ITERATE_QUERY)

        # self.ITERATE_QUERY = f"with temp as \n(\n\t{aggregated_query}\n)"

        return self
