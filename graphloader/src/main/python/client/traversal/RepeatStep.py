from client.traversal import Traversal
from client.traversal import DirectedEStep
from client.traversal import BothEStep


class RepeatStep(Traversal.Traversal):
    TIMES = 0
    UNTIL = None

    def __init__(self, byte_arr):
        super(RepeatStep, self).__init__()
        self.byte_rep = byte_arr
        self.REPEAT_BYTE_REP = None

    def repeat_traversals(self, traversals):
        self.byte_rep = self.byte_rep
        self.REPEAT_BYTE_REP = [["repeat"]] + traversals.__bytes__()
        self.byte_rep.append(self.REPEAT_BYTE_REP)
        return self

    def times(self, times):
        self.TIMES = times
        self.REPEAT_BYTE_REP.append(["times", str(times)])
        self._generate_repeat_bytecode_()
        return self

    def properties(self, label=False):
        self.byte_rep.append([["properties", str(label)]])
        from client.traversal.PropertiesStep import PropertiesStep
        return PropertiesStep(self.byte_rep)

    def until(self, until):
        self.UNTIL = until
        self.REPEAT_BYTE_REP.append(["until", until])
        self._generate_repeat_bytecode_()
        return self

    def bothE(self, label=None):
        # print(f"Bytecode before encountering bothE() is {self.byte_rep}")
        # self.byte_rep = [self.byte_rep]
        # print(f"Bytecode after encountering bothE() is {self.byte_rep}")

        if label is not None:
            self.byte_rep.append([["bothE"], ["T.label", label]])
            return BothEStep.BothEStep(self.byte_rep).set_label(label)
        else:
            self.byte_rep.append([["bothE"], [], []])
            return BothEStep.BothEStep(self.byte_rep)

    def outE(self, label=None):
        # self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["outE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).set_label(label)
        else:
            # print(f"Extending {self.byte_rep}")
            self.byte_rep.append([["outE"], [], []])
            return DirectedEStep.DirectedEStep("out", self.byte_rep)

    def inE(self, label=None):
        # self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["inE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).set_label(label)
        else:
            self.byte_rep.append([["inE"], [], []])
            return DirectedEStep.DirectedEStep("in", self.byte_rep)

    def both(self, label=None):
        # self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["bothE"], ["T.label", label]])
            return BothEStep.BothEStep(self.byte_rep).set_label(label).otherV()
        else:
            self.byte_rep.append([["bothE"], []])
            return BothEStep.BothEStep(self.byte_rep).otherV()

    def out(self, label=None):
        # print(f"Bytecode before encountering out() is {self.byte_rep}")
        # self.byte_rep = [self.byte_rep]
        # print(f"Bytecode after encountering out() is {self.byte_rep}")

        if label is not None:
            self.byte_rep.append([["outE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).set_label(label).inV()
        else:
            self.byte_rep.append([["outE"], []])
            return DirectedEStep.DirectedEStep("out", self.byte_rep).inV()

    def in_(self, label=None):
        # self.byte_rep = [self.byte_rep]

        if label is not None:
            self.byte_rep.append([["inE"], ["T.label", label]])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).set_label(label).outV()
        else:
            self.byte_rep.append([["inE"], []])
            return DirectedEStep.DirectedEStep("in", self.byte_rep).outV()

    def _generate_repeat_bytecode_(self):
        self.byte_rep[:-1].append(self.REPEAT_BYTE_REP)
        return self
