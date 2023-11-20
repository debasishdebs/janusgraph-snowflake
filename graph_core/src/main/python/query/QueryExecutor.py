from query.QueryParser import QueryParser
from query.steps.VertexCentricStep import VertexCentricStep
from typing import Optional, Union
from query.steps.ProjectStep import ProjectStep
from query.steps.PropertiesStep import PropertiesStep
from query.steps.TraversalIdStep import TraversalIdStep
from query.steps.IteratationStepWrapper import IterationStepWrapper


class QueryExecutor(object):
    def __init__(self):
        self.FINAL_QUERY = None

        self.CENTRIC_STEP: VertexCentricStep = None
        self.ITERATION_STEP: IterationStepWrapper = None
        self.SELECTION_STEP: Optional[Union[ProjectStep, PropertiesStep, TraversalIdStep]] = None
        self.ERROR = ""
        self.READ_QUERY = True
        self.ELEMENT_ADD_STEP = None

    def for_query(self, query):
        # print(f"4: Executing for query \n{query}")
        self.QUERY = query
        return self

    def for_parser(self, parser: QueryParser):
        query_type = parser.get_query_type()
        self.READ_QUERY = (query_type.lower() == "read")

        if self.READ_QUERY:
            # print(f"5: Setting parser as \n{parser}")
            self.CENTRIC_STEP = parser.get_centric_query()
            # print(f"5a: Centric query is {self.CENTRIC_STEP}")
            self.ITERATION_STEP = self.CENTRIC_STEP.get_iteration_step()
            # print(f"5b: Iteration step query is {self.ITERATION_STEP}")
            self.SELECTION_STEP = self.ITERATION_STEP.get_selection_step()
            # print(f"5c: Selection step query is {self.SELECTION_STEP}")
        else:
            self.ELEMENT_ADD_STEP = parser.get_element_addition_query()

        return self

    def execute(self):
        print("Going to execute the query now")

        if self.READ_QUERY:
            self.CENTRIC_STEP.execute()
            self.SELECTION_STEP.execute()
            self.ITERATION_STEP.execute()

            self.ERROR = {
                "CENTRIC": self.CENTRIC_STEP.ERROR,
                "SELECTION": self.SELECTION_STEP.ERROR,
                "ITERATION": self.ITERATION_STEP.ERROR
            }

            print(f" Error is {self.ERROR} before pop")

            error = {k: v for k, v in self.ERROR.items() if v != "NA"}
            self.ERROR = error

            print(f" Error is {self.ERROR} after pop")

            traversal_query = self.ITERATION_STEP.get_query()
            display_query = self.SELECTION_STEP.get_query()

            if str(self.SELECTION_STEP) == "properties":
                print("I'm here")
                query = display_query.format(traversal=traversal_query)
            else:
                print("project here")
                query = display_query.format(traversal=traversal_query)

            print(query)
            self.FINAL_QUERY = [query]
            print(100*"-")

        else:
            # print(self.ELEMENT_ADD_STEP)
            self.ELEMENT_ADD_STEP.execute()

            self.ERROR = {
                "ElementAdd": self.ELEMENT_ADD_STEP.ERROR
            }

            print(f" Error is {self.ERROR} before pop")

            error = {k: v for k, v in self.ERROR.items() if v != "NA"}
            self.ERROR = error

            self.FINAL_QUERY = [self.ELEMENT_ADD_STEP.SQL_QUERY, self.ELEMENT_ADD_STEP.READ_QUERY]

            # print("Final query to add element is ")
            # print(self.FINAL_QUERY[0])
            # print(self.FINAL_QUERY[1])

        return self
