from client.traversal import EdgeStep
from client.traversal import Traversal
from multipledispatch import dispatch
from client.traversal.Predicates import Predicates


class EdgeVertexStep(Traversal.Traversal):
    label = None

    def __init__(self, byte_arr=None, anonymous=False):
        super().__init__()
        self.byte_rep = byte_arr if byte_arr is not None else []
        self.anonymous = anonymous

    @dispatch(str, Predicates)
    def with_(self, prop_name, prop_val: Predicates):
        # byte_rep = self.byte_rep[-1]
        # byte_rep.append(prop_name)
        # byte_rep.append(",".join(prop_val.get()))
        # self.byte_rep[-1] = byte_rep

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

        # self.byte_rep[-1].append([prop_name, *prop_val.get()])
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
        # byte_rep = self.byte_rep[-1]
        # byte_rep[1] = prop_name
        # byte_rep[2] = f"eq,{prop_val}"
        # self.byte_rep[-1] = byte_rep
        # self.byte_rep[-1].append([prop_name, prop_val])
        byte_arr = [prop_name, f"eq,{prop_val}"]
        self.byte_rep[-1].append(byte_arr)
        print(self.byte_rep)
        return self

    @dispatch(str, float)
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

    @dispatch(int)
    def withId(self, id_val):
        self.byte_rep[-1][-1].extend(["T.id", str(id_val)])
        return self

    @dispatch(Predicates)
    def withId(self, id_val: Predicates):
        self.byte_rep[-1][-1].extend(["T.id", *id_val.get()])
        return self

    def withLabel(self, label):
        print(self.byte_rep[-1])
        print("withLabel")
        is_labelized = any([True if "T.label" == x[0] else False for x in self.byte_rep[-1]])
        print(is_labelized)
        print([True if "T.label" == x[0] else False for x in self.byte_rep[-1]])
        print([x[0] for x in self.byte_rep[-1]])
        if not is_labelized:
            self.byte_rep[-1][-1].extend(["T.label", label])
            self.label = label
        else:
            print("Label is already defined going to instantiate the class var label")
            el = [x[1] if "T.label" == x[0] else False for x in self.byte_rep[-1]]
            print(el)
            label = [x for x in el if x is not False]
            print(label)
            self.label = label[0]
            print("Label identified is ", label)
        return self

    def properties(self, label=False):
        self.byte_rep.append([["properties", str(label)]])
        from client.traversal.PropertiesStep import PropertiesStep
        return PropertiesStep(self.byte_rep)

    def as_(self, key):
        self.byte_rep[-1].append(["as", key])
        return self

    def repeat(self, traversal):
        # print(traversal)
        # print("Is byte representation")
        from client.traversal import RepeatStep
        return RepeatStep.RepeatStep(self.byte_rep).repeat_traversals(traversal)

    def bothE(self, label=None):
        # print("I'm inside bothE(). This was called from repeat")
        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["bothE", "T.label", label])
            else:
                self.byte_rep.append([["bothE"], ["T.label", label]])

            return EdgeStep.EdgeStep("both", self.byte_rep, self.anonymous).set_label(label)
        else:
            if self.anonymous:
                self.byte_rep.append(["bothE", "", ""])
            else:
                self.byte_rep.append([["bothE"], [], []])

            return EdgeStep.EdgeStep("both", self.byte_rep, self.anonymous)

    def outE(self, label=None):
        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["outE", "T.label", label])
            else:
                self.byte_rep.append([["outE"], ["T.label", label]])

            return EdgeStep.EdgeStep("out", self.byte_rep, self.anonymous).set_label(label)
        else:
            if self.anonymous:
                self.byte_rep.append(["outE", "", ""])
            else:
                self.byte_rep.append([["outE"], [], []])

            return EdgeStep.EdgeStep("out", self.byte_rep, self.anonymous)

    def inE(self, label=None):
        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["inE", "T.label", label])
            else:
                self.byte_rep.append([["inE"], ["T.label", label]])

            return EdgeStep.EdgeStep("in", self.byte_rep, self.anonymous).set_label(label)
        else:
            if self.anonymous:
                self.byte_rep.append(["inE", "", ""])
            else:
                self.byte_rep.append([["inE"], [], []])

            return EdgeStep.EdgeStep("in", self.byte_rep, self.anonymous)

    def both(self, label=None):
        if label is not None:
            self.byte_rep.append([["bothE"], ["T.label", label]])
            return EdgeStep.EdgeStep("both", self.byte_rep, self.anonymous).set_label(label).otherV()
        else:
            self.byte_rep.append([["bothE"], [], []])
            return EdgeStep.EdgeStep("both", self.byte_rep, self.anonymous).otherV()

    def out(self, label=None):
        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["outE", "T.label", label])
            else:
                self.byte_rep.append([["outE"], ["T.label", label]])
            return EdgeStep.EdgeStep("out", self.byte_rep, self.anonymous).set_label(label).inV()
        else:
            if self.anonymous:
                self.byte_rep.append(["outE", "", ""])
            else:
                self.byte_rep.append([["outE"], [], []])
            return EdgeStep.EdgeStep("out", self.byte_rep, self.anonymous).inV()

    def in_(self, label=None):
        if label is not None:
            if self.anonymous:
                self.byte_rep.append(["inE", "T.label", label])
            else:
                self.byte_rep.append([["inE"], ["T.label", label]])
            return EdgeStep.EdgeStep("in", self.byte_rep, self.anonymous).set_label(label).outV()
        else:
            if self.anonymous:
                self.byte_rep.append(["inE", "", ""])
            else:
                self.byte_rep.append([["inE"], [], []])
            return EdgeStep.EdgeStep("in", self.byte_rep, self.anonymous).outV()

    def __bytes__(self):
        return self.byte_rep
