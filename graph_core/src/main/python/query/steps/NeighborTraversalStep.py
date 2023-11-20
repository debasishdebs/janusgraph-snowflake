from gen.graphdb_pb2 import MiddleMostByteCode


class NeighborTraversalStep(object):
    FILTERS = dict()

    def __init__(self, step):
        self.VCI_STEP = step
        assert type(self.VCI_STEP) == MiddleMostByteCode

    def execute(self):
        self._generate_filters_()
        query = self._generate_query_()
        print("WHERE CLAUSE FOR ANCHOR")
        print(query)
        return self

    def _generate_filters_(self):
        i = 0
        for step in self.VCI_STEP.middle_layer:
            if i == 0:
                i += 1
                continue

            if step.inner_values[0] == "with":
                assert len(step.inner_values) == 3
                key = step.inner_values[1]
                value = step.inner_values[2]
                self.FILTERS[key] = value

            else:
                assert len(step.inner_values) == 2
                key = step.inner_values[0]
                value = step.inner_values[1]
                self.FILTERS[key] = value

            i += 1
        return self

    def _generate_query_(self):
        SQL = ""
        for k, v in self.FILTERS.items():
            if k == "T.id" or k == "T.label":
                key = k.split("T.")[1]
            else:
                key = k

            if SQL == "":
                if key != "id" or key != "label":
                    string = f"where nodes.properties:'{key}' = '{v}'"
                else:
                    string = f"where '{key}' = '{v}'"
                SQL += string
            else:
                if key != "id" or key != "label":
                    string = f"and nodes.properties:'{key}' = '{v}'"
                else:
                    string = f"and '{key}' = '{v}'"
                SQL += string
        return SQL
