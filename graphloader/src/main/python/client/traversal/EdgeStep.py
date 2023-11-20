# from EdgeVertexStep import EdgeVertexStep
# import EdgeVertexStep
from client.traversal import EdgeVertexStep
from client.traversal import Traversal
from multipledispatch import dispatch
from client.traversal.Predicates import Predicates


class EdgeStep(Traversal.Traversal):
    direction = None
    label = None

    def __init__(self, direction, byte_arr=None, anonymous=False):
        super().__init__()
        self.direction = direction
        self.anonymous = anonymous

        if byte_arr is None:
            self.byte_rep = []
        else:
            self.byte_rep = byte_arr

    @dispatch(str, Predicates)
    def with_(self, prop_name, prop_val):
        # print(self.byte_rep)
        # print(prop_name)
        # print(prop_val)
        # print(prop_val.get())
        # byte_rep = self.byte_rep[-1]
        # byte_rep.append(prop_name)
        # if self.anonymous:
        #     byte_rep.append(",".join(prop_val.get()))
        # else:
        #     byte_rep.append(prop_val.get())
        # self.byte_rep[-1] = byte_rep
        # print(self.byte_rep)
        # print("with_ EdgeStep")

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
        print(self.byte_rep)
        return self

    @dispatch(str, str)
    def with_(self, prop_name, prop_val):
        # byte_rep = self.byte_rep[-1]
        # byte_rep[1] = prop_name
        # byte_rep[2] = f"eq,{prop_val}"
        # self.byte_rep[-1] = byte_rep
        # self.byte_rep[-1].append([prop_name, prop_val])
        byte_arr = [prop_name, f"eq,{prop_val}"]
        self.byte_rep[-1].append(byte_arr)
        print(self.byte_rep)
        return self

    @dispatch(str, int)
    def with_(self, prop_name, prop_val):
        print("bytecode till now ", self.byte_rep)
        # byte_rep = self.byte_rep[-1]
        # print(byte_rep)
        byte_arr = [prop_name, f"eq,{prop_val}"]
        # byte_rep[1] = prop_name
        # byte_rep[2] = f"eq,{prop_val}"
        self.byte_rep[-1].append(byte_arr)
        print(self.byte_rep)
        # self.byte_rep[-1].append([prop_name, str(prop_val)])
        return self

    @dispatch(str, float)
    def with_(self, prop_name, prop_val):
        byte_arr = [prop_name, f"eq,{prop_val}"]
        self.byte_rep[-1].append(byte_arr)
        print(self.byte_rep)
        return self

    def set_label(self, label):
        self.label = label
        return self

    def as_(self, key):
        self.byte_rep[-1].append(["as", key])
        return self

    def otherV(self, label=None):
        if self.direction is not "both":
            raise AttributeError("otherV can only be invoked from bothE(). Use inV() or outV() instead based on need")
        label = label if label is not None else self.label if self.label is not None else None

        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["otherV", "T.label", label])
            else:
                self.byte_rep.append([["otherV"], ["T.label", label]])

            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)

        else:
            if self.anonymous:
                print("Calling otherV")
                print(self.byte_rep)
                self.byte_rep.append(["otherV", "", ""])
                print(self.byte_rep)
            else:
                self.byte_rep.append([["otherV"], [], []])
            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)

    def inV(self, label=None):
        if self.direction is "both":
            raise AttributeError("inV can only be invoked from outE()/inE() step not bothE(). Use otherV()")
        label = label if label is not None else self.label if self.label is not None else None

        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["inV", "T.label", label])
            else:
                self.byte_rep.append([["inV"], ["T.label", label]])

            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)
        else:
            if self.anonymous:
                self.byte_rep.append(["inV", "", ""])
            else:
                self.byte_rep.append([["inV"], [], []])

            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)

    def outV(self, label=None):
        if self.direction is "both":
            raise AttributeError("outV can only be invoked from inE()/outE() step not bothE(). Use otherV()")
        label = label if label is not None else self.label if self.label is not None else None

        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["outV", "T.label", label])
            else:
                self.byte_rep.append([["outV"], ["T.label", label]])

            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)
        else:
            if self.anonymous:
                self.byte_rep.append(["outV", "", ""])
            else:
                self.byte_rep.append([["outV"], [], []])

            return EdgeVertexStep.EdgeVertexStep(self.byte_rep, self.anonymous)

    def __bytes__(self):
        return self.byte_rep
