from multipledispatch import dispatch
import datetime


class P:
    @staticmethod
    @dispatch(str, str)
    def between(start, end):
        print("1")
        return Predicates(["between", start, end])

    @staticmethod
    @dispatch(int, int)
    def between(start, end):
        print("2")
        return Predicates(["between", str(start), str(end)])

    @staticmethod
    @dispatch(datetime.datetime, datetime.datetime)
    def between(start, end):
        print("3")
        return Predicates(["between", "time", start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")])

    @staticmethod
    def in_(*args):
        return

    @staticmethod
    def within(*args):
        bytecode = ["within"]
        for x in args:
            bytecode.extend([str(x)])
        return Predicates(bytecode)

    @staticmethod
    def gte(value):
        return Predicates(["gte", str(value)])

    @staticmethod
    def lte(value):
        return Predicates(["lte", str(value)])

    @staticmethod
    def gt(value):
        return Predicates(["gt", str(value)])

    @staticmethod
    def lt(value):
        return Predicates(["lt", str(value)])

    @staticmethod
    def eq(value):
        return Predicates(["eq", str(value)])

    @staticmethod
    def or_(*args):
        bytecode = ["or"]
        for x in args:
            bytecode.extend([str(x)])
        return Predicates(bytecode)


class Predicates:
    def __init__(self, bytecode: list):
        self.BYTECODE = bytecode
        pass

    def get(self):
        return self.BYTECODE
