from client.traversal import BothEStep
from client.traversal import DirectedEStep
from client.traversal import Traversal
from multipledispatch import dispatch
from client.traversal.Predicates import Predicates


class VStep(Traversal.Traversal):
    def __init__(self):
        super().__init__()
        self.byte_rep = [["V"]]

    @dispatch(str, Predicates)
    def with_(self, prop_name, prop_val: Predicates):
        self.byte_rep.append([prop_name, *prop_val.get()])
        return self

    @dispatch(str, str)
    def with_(self, prop_name, prop_val):
        self.byte_rep.append([prop_name, prop_val])
        return self

    @dispatch(str, int)
    def with_(self, prop_name, prop_val):
        self.byte_rep.append([prop_name, prop_val])
        return self

    @dispatch(str, float)
    def with_(self, prop_name, prop_val):
        self.byte_rep.append([prop_name, prop_val])
        return self

    @dispatch(int)
    def withId(self, id_val):
        self.byte_rep.append(["T.id", str(id_val)])
        return self

    @dispatch(Predicates)
    def withId(self, id_val: Predicates):
        self.byte_rep.append(["T.id", *id_val.get()])
        # print(self.byte_rep)
        return self

    def withLabel(self, label):
        is_labelized = any([True if "T.label" == x[0] else False for x in self.byte_rep])
        if not is_labelized:
            self.byte_rep.append(["T.label", label])
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
        #
        # print(self.byte_rep)
        # print("is byte rep in withLabel till now")
        # self.byte_rep.append(["T.label", label])
        # print(self.byte_rep)
        # print("and after is")
        # return self

    def properties(self, label=False):
        self.byte_rep = [self.byte_rep]
        self.byte_rep.append([["properties", str(label)]])
        from client.traversal.PropertiesStep import PropertiesStep
        return PropertiesStep(self.byte_rep)

    def bothE(self, label=None):
        self.byte_rep = [self.byte_rep]
        print("Bytecode in vstep ", self.byte_rep)
        if label is not None:
            self.byte_rep.append([["bothE"], ["T.label", label]])
            return BothEStep.BothEStep(self.byte_rep).set_label(label)
        else:
            self.byte_rep.append([["bothE"], [], []])
            return BothEStep.BothEStep(self.byte_rep)

    def outE(self, label=None):
        self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["outE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).set_label(label)
        else:
            # print(f"Extending {self.byte_rep}")
            self.byte_rep.append([["outE"], [], []])
            return DirectedEStep.DirectedEStep("out", self.byte_rep)

    def inE(self, label=None):
        self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["inE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).set_label(label)
        else:
            self.byte_rep.append([["inE"], [], []])
            return DirectedEStep.DirectedEStep("in", self.byte_rep)

    def both(self, label=None):
        self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["bothE"], ["T.label", label]])
            return BothEStep.BothEStep(self.byte_rep).set_label(label).otherV()
        else:
            self.byte_rep.append([["bothE"], []])
            return BothEStep.BothEStep(self.byte_rep).otherV()

    def out(self, label=None):
        self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["outE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).set_label(label).inV()
        else:
            self.byte_rep.append([["outE"], []])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).inV()

    def in_(self, label=None):
        self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["inE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).set_label(label).outV()
        else:
            self.byte_rep.append([["inE"], []])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).outV()

    def repeat(self, traversal):
        print(traversal)
        # print("Is byte representation")
        from client.traversal import RepeatStep
        return RepeatStep.RepeatStep([self.byte_rep]).repeat_traversals(traversal)
