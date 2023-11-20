from client.traversal import VStep
from client.utils.common_resources import Commons
from client.traversal.AnonymousTraversal import __
from client.connection.SnowGraphConnection import SnowGraphConnection
from multipledispatch import dispatch
import uuid


class GraphTraversal(object):
    def __init__(self, conn: SnowGraphConnection):
        Commons.put_connection(conn)

    def V(self) -> VStep.VStep():
        return VStep.VStep()

    def E(self):
        return

    @dispatch()
    def addV(self):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(False).withId().withLabel()

    @dispatch()
    def addOrUpdateV(self):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(True).withId().withLabel()

    @dispatch(int)
    def addV(self, id):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(False).withId(id).withLabel()

    @dispatch(int)
    def addOrUpdateV(self, id):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(True).withId(id).withLabel()

    @dispatch(str)
    def addV(self, label):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(False).withLabel(label).withId()

    @dispatch(str)
    def addOrUpdateV(self, label):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(True).withLabel(label).withId()

    @dispatch(int, str)
    def addV(self, id, label):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(False).withId(id).withLabel(label)

    @dispatch(int, str)
    def addOrUpdateV(self, id, label):
        from client.traversal.AddVertexStep import AddVertexStep
        return AddVertexStep(True).withId(id).withLabel(label)

    @dispatch()
    def addE(self):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(False).withId().withLabel()

    @dispatch()
    def addOrUpdateE(self):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(True).withId().withLabel()

    @dispatch(uuid.UUID)
    def addE(self, id):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(False).withId(id).withLabel()

    @dispatch(uuid.UUID)
    def addOrUpdateE(self, id):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(True).withId(id).withLabel()

    @dispatch(str)
    def addE(self, label):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(False).withLabel(label).withId()

    @dispatch(str)
    def addOrUpdateE(self, label):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(True).withLabel(label).withId()

    @dispatch(uuid.UUID, str)
    def addE(self, id, label):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(False).withId(id).withLabel(label)

    @dispatch(uuid.UUID, str)
    def addOrUpdateE(self, id, label):
        from client.traversal.AddEdgeStep import AddEdgeStep
        return AddEdgeStep(True).withId(id).withLabel(label)


if __name__ == '__main__':
    # tr.V().with_("p1", "v1").as_("a").\
    #     outE().with_("ep1", "ep2").\
    #     inV("v2").\
    #     inE("e2").\
    #     outV().with_("p2", "v2").as_("b").\
    #     bothE().otherV().\
    #     project("a", "b").\
    #         by_(__.select("a")).\
    #         by_(__.select("b")).\
    # next()

    # tr.V().with_("p1", "v1").as_("a"). \
    #     outE("e1"). \
    #     inV("v2"). \
    #     outE("e2"). \
    #     inV().as_("b"). \
    #     project("a", "b"). \
    #     by_(__.select("a")). \
    #     by_(__.select("b")). \
    #     next()

    import pandas as pd
    from client.traversal.Column import Column as C

    conn = SnowGraphConnection()
    conn.set_host("localhost")
    conn.set_port(1000)
    tr = GraphTraversal(conn)

    # Tested:
    # bothE().otherV().repeat(bothE().otherV()) - Done - 708
    # bothE().otherV().repeat(outE().inV()) - Done - 90
    # bothE().otherV().repeat(inE().outV()) - Fail
    # bothE().otherV().repeat(in()) - Fail
    # bothE().otherV().repeat(both()) - Done - 708
    # bothE().otherV().repeat(out()) - Done - 90

    # outE().inV().repeat(bothE().otherV()) - Done - 708
    # outE().inV().repeat(outE().inV()) - Done - 90
    # outE().inV().repeat(inE().outV()) - FAIL
    # outE().inV().repeat(in()) - FAIL
    # outE().inV().repeat(both()) - Done - 708
    # outE().inV().repeat(out()) - Done - 90

    # inE().outV().repeat(bothE().otherV()) - Done - 708
    # inE().outV().repeat(outE().inV()) - Done - 90
    # inE().outV().repeat(inE().outV()) - FAIL
    # inE().outV().repeat(in()) - FAIL
    # inE().outV().repeat(both()) - Done - 708
    # inE().outV().repeat(out()) - Done - 90

    # BUGS Found:
    # 1: IN Directed traversals inside REPEAT doesn't work - RESOLVED
    # 2: When we do tr.V().with_("userName", "userName_0").out().repeat(__.out()), it repeats from root node and not the
    # traversed node because this is essentially combo of Traversal & Repeatstep and TraversalStep isn't implemented
    # result = tr.V().with_("userName", "userName_0").inE().outV().as_("a").repeat(__.inE().outV()).times(2).project(C.id_()).next()

    # result = tr.V().with_("ip", "192.168.0.101").inE().outV().with_("userName", "userName_0").as_("a").both().as_("b").repeat(__.inE().outV()).times(2).\
    #     out().as_("c").bothE().with_("counter", 1).as_("e").otherV().with_("userName", "userName_2").as_("d").project(C.all_()).next()

    from client.traversal.Predicates import P
    # result = tr.V().with_("ip", "192.168.0.101").inE().outV().as_("a").both().as_("b").repeat(__.inE().outV()).times(2). \
    #     out().as_("c").bothE().with_("counter", 1).as_("e").otherV().as_("d").project(C.all_()).dedup().count().next()

    # result = tr.V().with_("ip", "192.168.0.101").bothE().with_("counter", 1).otherV().with_("userName", "userName_0").out().inE().as_("e").outV().as_("a").project(C.all_()).next()

    import datetime as dt
    # pprint.pprint(result)
    # print(20*"------")
    # import traceback, time
    #
    # # result = tr.V().with_("ip", "192.168.0.101").outE().inV().out().repeat(__.inE().outV()).times(1).out().repeat(__.out()).times(1).out().out().properties().dedup().next()
    # # print(result)
    # success = {}
    # failures = {}
    #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").properties().dedup().next()
    # #     success[0] = {
    # #         "query": tr.V().properties().dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 0")
    # # except:
    # #     print("Exception in running query 0")
    # #     failures[0] = {"query": tr.V().with_("ip", "192.168.0.101").properties().dedup(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().properties().dedup().next()
    # #     success[1] = {
    # #         "query": tr.V().properties().dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 1")
    # # except:
    # #     print("Exception in running query 1")
    # #     failures[1] = {"query": tr.V().properties().dedup(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().project(C.all_()).next()
    # #     success[2] = {
    # #         "query": tr.V().project(C.all_()),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 2")
    # # except:
    # #     print("Exception in running query 2")
    # #     failures[2] = {"query": tr.V().project(C.all_()), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().project(C.all_()).dedup().next()
    # #     success[3] = {
    # #         "query":  tr.V().project(C.all_()).dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 3")
    # # except:
    # #     print("Exception in running query 3")
    # #     failures[3] = {"query": tr.V().project(C.all_()).dedup(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().out().dedup().properties().next()
    # #     success[4] = {
    # #         "query":  tr.V().out().dedup().properties().dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 4")
    # # except:
    # #     print("Exception in running query 4")
    # #     failures[4] = {"query": tr.V().out().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().in_().dedup().properties().next()
    # #     success[5] = {
    # #         "query":  tr.V().in_().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 5")
    # # except:
    # #     print("Exception in running query 5")
    # #     failures[5] = {"query": tr.V().in_().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().both().dedup().properties().next()
    # #     success[6] = {
    # #         "query":  tr.V().both().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 6")
    # # except:
    # #     print("Exception in running query 6")
    # #     failures[6] = {"query": tr.V().both().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().outE().dedup().properties().next()
    # #     success[7] = {
    # #         "query":  tr.V().outE().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 7")
    # # except:
    # #     print("Exception in running query 7")
    # #     failures[7] = {"query": tr.V().outE().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().inE().dedup().properties().next()
    # #     success[8] = {
    # #         "query":  tr.V().inE().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 8")
    # # except:
    # #     print("Exception in running query 8")
    # #     failures[8] = {"query": tr.V().inE().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().outE().inV().dedup().properties().next()
    # #     success[9] = {
    # #         "query":  tr.V().outE().inV().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 9")
    # # except:
    # #     print("Exception in running query 9")
    # #     failures[9] = {"query": tr.V().outE().inV().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().inE().outV().dedup().properties().next()
    # #     success[10] = {
    # #         "query":  tr.V().inE().outV().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 10")
    # # except:
    # #     print("Exception in running query 10")
    # #     failures[10] = {"query": tr.V().inE().outV().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    #
    # # try:
    # #     result = tr.V().bothE().otherV().dedup().properties().next()
    # #     success[11] = {
    # #         "query":  tr.V().bothE().otherV().dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 11")
    # # except:
    # #     print("Exception in running query 12")
    # #     failures[11] = {"query": tr.V().inE().outV().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().repeat(__.out()).times(1).dedup().properties().next()
    # #     success[12] = {
    # #         "query":  tr.V().repeat(__.out()).times(1).dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 12")
    # # except:
    # #     print("Exception in running query 13")
    # #     failures[12] = {"query": tr.V().inE().outV().dedup().properties(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE()).times(2).dedup().properties().next()
    # #     success[13] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE()).times(2).dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 13")
    # # except:
    # #     print("Exception in running query 14")
    # #     failures[13] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE()).times(2).dedup().properties(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().otherV()).times(2).dedup().properties().next()
    # #     success[14] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().otherV()).times(2).dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 14")
    # # except:
    # #     print("Exception in running query 14")
    # #     failures[14] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().otherV()).times(2).dedup().properties(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", P.within("192.168.0.101", "192.168.0.102", "192.168.0.103")).repeat(__.bothE().with_("counter", P.between(1, 3)).otherV().with_("some", "value")).times(2).dedup().properties().next()
    # #     success[15] = {
    # #         "query":  tr.V().with_("ip", P.within("192.168.0.101", "192.168.0.102", "192.168.0.103")).repeat(__.bothE().with_("counter", P.within(1, 2)).otherV().with_("some", "value")).times(2).dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 15")
    # # except:
    # #     print("Exception in running query 15")
    # #     failures[15] = {"query": tr.V().with_("ip", P.within("192.168.0.101", "192.168.0.102", "192.168.0.103")).repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).dedup().properties(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", P.between("192.168.0.101", "192.168.0.103")).repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).dedup().properties().next()
    # #     success[16] = {
    # #         "query":  tr.V().with_("ip", P.between("192.168.0.101", "192.168.0.103")).repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).dedup().properties(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 16")
    # # except:
    # #     print("Exception in running query 16")
    # #     failures[16] = {"query": tr.V().with_("ip", P.between("192.168.0.101", "192.168.0.103")).repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).dedup().properties(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).project(C.all_()).dedup().next()
    # #     success[17] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).project(C.all_()).dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 17")
    # # except:
    # #     print("Exception in running query 17")
    # #     failures[17] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.within(1, 2)).otherV()).times(2).out().withLabel(P.within("IP", "user")).project(C.all_()).dedup(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.lte(2)).otherV()).times(1).out().withLabel(P.within("IP", "user")).repeat(__.out()).times(1).project(C.all_()).dedup().next()
    # #     success[18] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.lte(2)).otherV()).times(1).out().withLabel(P.within("IP", "user")).repeat(__.out()).times(1).project(C.all_()).dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 18")
    # # except:
    # #     print("Exception in running query 18")
    # #     failures[18] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.lte(2)).otherV()).times(1).out().withLabel(P.within("IP", "user")).repeat(__.out()).times(1).project(C.all_()).dedup(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(1).out().withLabel(P.eq("IP")).repeat(__.out()).times(1).project(C.all_()).dedup().next()
    # #     success[19] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(1).out().withLabel(P.eq("IP")).repeat(__.out()).times(1).project(C.all_()).dedup(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 19")
    # # except:
    # #     print("Exception in running query 19")
    # #     failures[19] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(1).out().withLabel(P.eq("IP")).repeat(__.out()).times(1).project(C.all_()).dedup(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     # This query can't be done so alternative is bellow
    # #     # result = tr.V().count().next()
    # #     result = tr.V().project(C.all_()).dedup().count().next()
    # #     success[20] = {
    # #         "query":  tr.V().count(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 20")
    # # except:
    # #     print("Exception in running query 20")
    # #     failures[20] = {"query": tr.V().count(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().bothE().dedup().count().next()
    # #     success[21] = {
    # #         "query":  tr.V().bothE().dedup().count(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 21")
    # # except:
    # #     print("Exception in running query 21")
    # #     failures[21] = {"query": tr.V().bothE().dedup().count(), "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # # try:
    # #     result = tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(3).out().withLabel(P.eq("IP")).project(C.all_()).dedup().count().next()
    # #     success[22] = {
    # #         "query":  tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(3).out().withLabel(P.eq("IP")).project(C.all_()).dedup().count(),
    # #         "result": result
    # #     }
    # #     print("Success in executing query 22")
    # # except:
    # #     print("Exception in running query 22")
    # #     failures[22] = {"query": tr.V().with_("ip", "192.168.0.101").repeat(__.bothE().with_("counter", P.between(1, 3)).otherV()).times(3).out().withLabel(P.eq("IP")).project(C.all_()).dedup().count(),
    # #                     "trace": traceback.format_exc()}
    # # print(20*"------")
    # # time.sleep(30)
    # #
    # try:
    #     result = tr.V().with_("ip", "192.168.0.101").properties().dedup().count().next()
    #     success[23] = {
    #         "query":  tr.V().with_("ip", "192.168.0.101").properties().dedup().count(),
    #         "result": result
    #     }
    #     print("Success in executing query 23")
    # except:
    #     print("Exception in running query 23")
    #     failures[23] = {"query": tr.V().with_("ip", "192.168.0.101").properties().dedup().count(),
    #                     "trace": traceback.format_exc()}
    # print(20*"------")
    # # time.sleep(30)
    #
    # print("Success")
    # for k, v in success.items():
    #     print("IDX: ", k)
    #     print("QUery: " , v["query"])
    #     print("Results")
    #     print(v["result"])
    #     print(len(v["result"][0]))
    #     print(100*"=-")
    #
    # print("Failures")
    # for k, v in failures.items():
    #     print("IDX: ", k)
    #     print("QUery: " , v["query"])
    #     print("Traceback")
    #     print(v["trace"])
    #     print(100*"=-")
    #
    # exit(-1)
    #
    # result = tr.V().with_("userName", "userName_0").outE().inV().next()
    # print(pd.DataFrame(result))
    # print("-----")
    # result = tr.V().with_("userName", "userName_0").outE().inV().outE().inV().next()
    # print(pd.DataFrame(result))
    # print("-----")
    # result = tr.V().with_("userName", "userName_0").outE().inV().outE().inV().outE().inV().next()
    # print(pd.DataFrame(result))
    # print("-----")
    #
    # result = tr.V().with_("userName", "userName_0").outE().inV().out().outE().inV().next()
    # print(pd.DataFrame(result))
    # print("-----")
    #
    # result = tr.V().with_("ip", "192.168.0.500").outE().inV().out().next()
    # print(pd.DataFrame(result))
    # print("-----")
    # print(tr.V().with_("prop1", "prop2").outE("testEdge").inV().withLabel("testVertex").next())

    # [ [ [V], [p1, p2] ], [ [outE, testEdge] ], [ [inV, label1], [prop1, between(x1, x2)] ] ]
    # [ [ [V], [p1, p2], [as, A] ], [ [outE, testEdge] ], [ [inV, label1], [prop1, between(x1, x2)] ], [ [project], [by, A] ] ]
    # [ [ [V], [p1, p2], [as, A] ], [ [outE, testEdge] ], [ [inV, label1], [prop1, between(x1, x2)] ], [ [project], [by, count, A], [by, max, A] ] ]
    # [ [ [V], [p1, p2], [as, A] ], [ [outE, testEdge] ], [ [inV, label1], [prop1, between(x1, x2)] ], [ [project], [by, A, properties], [by, A, T.label] ] ]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [times, 3] ], [ [emitAll] ],  [ [inV, label1], [prop1, between(x1, x2)] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [times, 3] ], [ [emitN], [1, 2] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [times, 3] ], [ [emit], [A, B] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [times, 3] ], [ [emitN], [first, last] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [until, T.id.eq(123)] ], [ [emitN], [first, last] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [until, has(pr1, pr2)] ], [ [emitN], [first, last] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [until, dia.eq(10)] ], [ [emitN], [first, last] ]]
    # [ [ [V], [p1, p2] ], [ [repeat], [outE, label], [until, len.eq(10)] ], [ [emitN], [first, last] ]]
    # TODO : ByteCode for OderBy, Coalesce, GroupBy, Edges
    # [ [[E], [p1, p2]], [[inV, l1]], [[outE, e1], [pp1, pp2]], [[inV, l2], [pp3, t1]] ]

    # tr.addOrUpdateV(999, 'random').property("prop1", "propval1").property("prop2", "propval2").property("prop3", "propval3").hold()
    # tr.addOrUpdateV(1000, 'random').property("prop1", "propval1").property("prop2", "propval2").hold()
    # tr.addOrUpdateV(1001, 'random').hold()
    # tr.addV(1002, 'random').property("prop1", "propval1").property("prop2", "propval2").hold()
    # tr.addV(1003, 'random').property("random", "here").addE(uuid.uuid4(), "testEdge").property("counter", 5).to(999).hold()
    # tr.addV(1004, 'random').property("prop1", "propval1").property("prop2", "propval2").hold()
    #
    # eid = uuid.uuid3(uuid.NAMESPACE_DNS, "abc-123-d45")
    # tr.addOrUpdateE(eid).property("count", 1).from_(999).to(1000).hold()
    # eid = uuid.UUID('{e4bca40d-1879-414f-b8f4-93d39572bb79}')
    # print("++++++++++START+++++++++++++")
    # print(eid)
    # e = tr.addOrUpdateE(eid, "randomEdge").property("count", 20).property("eventTime", Commons.convert_time(dt.datetime.now())).from_(1).to(1001).next()
    # print(e)
    # print("++++++++++END+++++++++++++")
    # eid = uuid.UUID('{b41ba06c-bfd3-4373-b414-bb9bf82fa2b1}')
    # print("++++++++++START+++++++++++++")
    # print(eid)
    # e = tr.addOrUpdateE(eid, "randomEdge").property("count", 20).property("eventTime", Commons.convert_time(dt.datetime.now())).from_(1).to(2).next()
    # print(e)
    # print("++++++++++END+++++++++++++")
    # eid = uuid.UUID('{49ed1af9-b772-456d-8ae2-f1d284c26153}')
    # print("++++++++++START+++++++++++++")
    # print(eid)
    # e = tr.addOrUpdateE(eid, "randomEdge").property("count", 100).property("eventTime", Commons.convert_time(dt.datetime.now())).from_(2).to(3).hold()
    # print(e)
    # print("++++++++++END+++++++++++++")
    # eid = uuid.UUID('{46b15ec8-6f46-455b-b603-fd993a7ebc58}')
    # print("++++++++++START+++++++++++++")
    # print(eid)
    # e = tr.addOrUpdateE(eid, "randomEdge").property("count", 150).property("eventTime", Commons.convert_time(dt.datetime.now())).from_(3).to(1001).next()
    # print(e)
    # print("++++++++++END+++++++++++++")
    #
    # tr.addOrUpdateV(999, 'random').property("prop1", "propval1").property("prop1", "propval2").property("prop2", "propval3").hold()
    # tr.addOrUpdateV(1000, 'random').property("prop1", "propval1").property("prop2", "propval2").hold()
    # v = tr.addOrUpdateV(1001, 'random').next()

    # print(v)

    # r = tr.V().with_("userName", "bruce.cook").out("hasIP").union(
    #     __.outE("isEvent").with_("counter", P.gt(1)).inV().with_("ip", "192.168"),
    #     __.out("IPsCommunicated"),
    #     __.out("other").with_("testP", P.eq("something")),
    #     __.out("random").with_("counter", P.gte(5)).out("random2").with_("dataSource", "windows")
    # ).in_("hasIP").project(C.all_()).next()

    # r = tr.V().with_("userName", "bruce.cook").union(
    #     __.outE("isEvent").inV(),
    #     __.out("IPsCommunicated")
    # ).in_("hasIP").project(C.all_()).next()

    # r = tr.V().withId(785866).out().both().in_().project(C.id_()).dedup().next()

    # FAILS
    # r = tr.V().withId(785866).both().withLabel(P.eq("email")).union(__.both().withLabel(P.neq("user")), __.both().withLabel(P.eq("user"))).project(C.all_()).dedup().next()

    # r = tr.V().withId(785866).both().withLabel(P.eq("email")).coalesce(__.both(), __.both()).project(C.all_()).dedup().next()

    r = tr.V().withId(785866).both().withLabel(P.eq("email")).both().project(C.all_()).dedup().next()

    print(r)
