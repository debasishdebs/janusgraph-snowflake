from client.traversal import EStep
# from .VStep import VStep
# from EStep import EStep
# from VStep import VStep
from client.traversal import EdgeVertexStep
from multipledispatch import dispatch
from client.traversal.Predicates import Predicates


class BothEStep(EStep.EStep):
    label = None

    def __init__(self, byte_arr=None):
        super().__init__()

        if byte_arr is None:
            self.byte_rep = []
        else:
            self.byte_rep = byte_arr
        print("bytecode after initializing bothe " , self.byte_rep)

    @dispatch(str, Predicates)
    def with_(self, prop_name, prop_val):
        print("bytecode in bothe before predicate condition ", self.byte_rep)
        byte_rep = self.byte_rep[-1]
        byte_arr = [prop_name]
        vals = prop_val.get()
        prop_value = ""
        for val in vals:
            if prop_value == "":
                prop_value += val
            else:
                prop_value += f",{val}"
        # byte_rep = [prop_name, prop_value]
        byte_arr.append(prop_value)
        print(prop_value)
        print(prop_name)
        print(prop_val.get())
        print(byte_arr)
        self.byte_rep[-1].append(byte_arr)
        print("bytecode in bothe after predicate condition ", self.byte_rep)
        return self

    @dispatch(str, str)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    @dispatch(str, int)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, str(prop_val)])
        return self

    @dispatch(str, float)
    def with_(self, prop_name, prop_val):
        self.byte_rep[-1].append([prop_name, prop_val])
        return self

    def set_label(self, label):
        self.label = label
        return self

    def otherV(self, label=None):
        if label is not None:
            self.byte_rep.append([["otherV"], ["T.label", label]])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep).withLabel(label)
        else:
            self.byte_rep.append([["otherV"], [], []])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep)

    def inV(self):
        raise AttributeError("inV can only be invoked from outE() step not bothE(). Use otherV()")

    def outV(self):
        raise AttributeError("outV can only be invoked from inE() step not bothE(). Use otherV()")

    def __bytes__(self):
        return self.byte_rep
