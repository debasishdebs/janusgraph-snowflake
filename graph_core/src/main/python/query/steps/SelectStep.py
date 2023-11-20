from gen.graphdb_pb2 import MiddleMostByteCode, ByteCode
from typing import List


class SelectStep:
    def __init__(self, bytecode):
        self.QUERY: ByteCode = bytecode
        self.STEPS: List[MiddleMostByteCode] = bytecode.steps

    def _identify_projection_and_aggregate_steps_(self):
        break_index = 0
        for step in self.STEPS:
            if step.middle_layer[0].inner_values[0] == "break":
                break
            break_index += 1
        self.PROJECT_AGGREGATE_STEPS = self.STEPS[break_index:]
        return self

    def _identify_type_of_step_(self):
        # Either simple step like Project / Order / Group
        # Or mixed step like Project - Order / Group - Order / Project - Group
        mixed = False
        simple = False
        mixed_steps = []
        for step in self.PROJECT_AGGREGATE_STEPS:
            if step.middle_layer[0].inner_values[0] in ["project", "order", "group"]:
                mixed_steps.append(step)

        if len(mixed_steps) > 1:
            mixed = True
        else:
            simple = True

        self.QUERY_TYPE = "mixed" if mixed else "simple"
        self.QUERY_STEPS = mixed_steps

        return self

    @staticmethod
    def identify_display_step_type(step):
        if step.middle_layer[0].inner_values[0] == "project":
            from query.steps.ProjectStep import ProjectStep
            return ProjectStep
        if step.middle_layer[0].inner_values[0] == "order":
            from query.steps.OrderStep import OrderStep
            return OrderStep
        if step.middle_layer[0].inner_values[0] == "group":
            from query.steps.GroupStep import GroupStep
            return GroupStep

    def _convert_query_to_steps_(self):
        project_steps = []
        for step in self.QUERY_STEPS:
            STEP = self.identify_display_step_type(step)
            STEP_CLS = STEP(bytecode=self.STEPS, current=step)
            project_steps.append(STEP_CLS)
        return project_steps

    def execute(self):
        view_steps = self._convert_query_to_steps_()
        return
