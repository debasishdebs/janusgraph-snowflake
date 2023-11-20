from client.traversal import EStep
# from .VStep import VStep
# from EStep import EStep
# from VStep import VStep
from client.traversal import EdgeVertexStep
from multipledispatch import dispatch
from client.traversal.Predicates import P, Predicates


class DirectedEStep(EStep.EStep):
    direction = None
    label = None

    def __init__(self, direction, byte_arr=None):
        super().__init__()
        self.direction = direction

        if byte_arr is None:
            self.byte_rep = []
        else:
            self.byte_rep = byte_arr

    @dispatch(str, P)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    @dispatch(str, Predicates)
    def with_(self, prop_name, prop_val):
        byte_arr = [prop_name]
        vals = prop_val.get()
        prop_value = ""
        for val in vals:
            if prop_value == "":
                prop_value += val
            else:
                prop_value += f",{val}"
        byte_arr.append(prop_value)
        self.byte_rep[-1].append(byte_arr)
        return self

    @dispatch(str, str)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    @dispatch(str, int)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    @dispatch(str, float)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    def set_label(self, label):
        self.label = label
        return self

    def otherV(self):
        raise AttributeError("otherV can only be invoked from bothE(). Use inV() or outV() instead based on need")

    def inV(self, label=None):
        if label is not None:
            self.byte_rep.append([["inV"], ["T.label", label]])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep).withLabel(label)
        else:
            self.byte_rep.append([["inV"], [], []])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep)

    def outV(self, label=None):
        if label is not None:
            self.byte_rep.append([["outV"], ["T.label", label]])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep).withLabel(label)
        else:
            self.byte_rep.append([["outV"], [], []])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep)

    def __bytes__(self):
        return self.byte_rep
