from client.traversal import Traversal
from client.traversal import BothEStep
from client.traversal import DirectedEStep


class UnionStep(Traversal.Traversal):
    def __init__(self, byte_rep):
        super().__init__()
        print(f"Bytecode for union step is {byte_rep}")
        self.byte_rep = byte_rep

    def with_traversals(self, traversals):
        for traversal in traversals:
            bytecode = traversal.__bytes__()
            bytecode = [["union"]] + bytecode
            self.byte_rep.append(bytecode)

        print(f"The bytecode after applying coalesce step is {self.byte_rep}")
        return self

    def bothE(self, label=None):
        # self.byte_rep = [self.byte_rep]

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
        # self.byte_rep = [self.byte_rep]

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

    def repeat(self, traversal):
        print(traversal)
        print("Is byte representation inside coalesce step")
        from client.traversal import RepeatStep
        return RepeatStep.RepeatStep([self.byte_rep]).repeat_traversals(traversal)
