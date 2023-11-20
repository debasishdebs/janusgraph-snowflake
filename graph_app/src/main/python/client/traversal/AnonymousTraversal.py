# from client.traversal import BothEStep
# from client.traversal import DirectedEStep
from client.traversal import EdgeStep


class __:
    def __init__(self):
        super().__init__()
        pass

    @staticmethod
    def select(key):
        # print("Selecting key " + key)
        return ["select", key, ""]

    @staticmethod
    def bothE(label=None):
        # print("bothE() in __")
        byte_rep = []
        if label is not None:
            byte_rep.append(["bothE", "T.label", label])
            return EdgeStep.EdgeStep("both", byte_rep, True).set_label(label)
        else:
            byte_rep.append(["bothE", "", ""])
            return EdgeStep.EdgeStep("both", byte_rep, True)

    @staticmethod
    def inE(label=None):
        byte_rep = []
        # print("inE() in __")
        if label is not None:
            byte_rep.append(["inE", "T.label", label])
            return EdgeStep.EdgeStep("in", byte_rep, True).set_label(label)
        else:
            byte_rep.append(["inE", "", ""])
            return EdgeStep.EdgeStep("in", byte_rep, True)

    @staticmethod
    def outE(label=None):
        byte_rep = []
        # print("outE() in __")
        if label is not None:
            byte_rep.append(["outE", "T.label", label])
            return EdgeStep.EdgeStep("out", byte_rep, True).set_label(label)
        else:
            byte_rep.append(["outE", "", ""])
            return EdgeStep.EdgeStep("out", byte_rep, True)

    # @staticmethod
    # def otherV(label=None):
    #     return
    #
    # @staticmethod
    # def inV(label=None):
    #     return
    #
    # @staticmethod
    # def outV(label=None):
    #     return

    @staticmethod
    def both(label=None):
        byte_rep = []
        if label is not None:
            byte_rep.append(["bothE", "T.label", label])
            return EdgeStep.EdgeStep("both", byte_rep, True).set_label(label).otherV()
        else:
            byte_rep.append(["bothE", "", ""])
            return EdgeStep.EdgeStep("both", byte_rep, True).otherV()

    @staticmethod
    def out(label=None):
        byte_rep = []
        if label is not None:
            byte_rep.append(["outE", "T.label", label])
            return EdgeStep.EdgeStep("out", byte_rep, True).set_label(label).inV()
        else:
            byte_rep.append(["outE", "", ""])
            return EdgeStep.EdgeStep("out", byte_rep, True).inV()

    @staticmethod
    def in_(label=None):
        byte_rep = []
        if label is not None:
            byte_rep.append(["inE", "T.label", label])
            return EdgeStep.EdgeStep("in", byte_rep, True).set_label(label).outV()
        else:
            byte_rep.append(["inE", "", ""])
            return EdgeStep.EdgeStep("in", byte_rep, True).outV()
