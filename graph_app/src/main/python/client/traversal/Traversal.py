from client.connection.ExecuteByteCode import ExecuteByteCode


class Traversal(object):
    def __init__(self):
        self.byte_rep = []

    def next(self):
        print("I'm inside next of Traversal")
        print(self.byte_rep)

        is_repeat_query = self._is_repeat_query_()
        if is_repeat_query:
            valid_repeat_query = self._is_valid_repeat_query_()
            if valid_repeat_query:
                valid_project_step = self._contains_project_step_()

                # return ExecuteByteCode(self.byte_rep).execute()
                # TODO
                if valid_project_step:
                    return ExecuteByteCode(self.byte_rep).execute().to_json()
                else:
                    raise AttributeError("Please use project() step with repeat() step")
            else:
                raise AttributeError("Please use times/until to specify end condition for REPEAT")
        else:
            return ExecuteByteCode(self.byte_rep).execute().to_json()

    def _contains_project_step_(self):
        project_step = None
        for step in self.byte_rep:
            if step[0][0] == "project":
                project_step = step

        for step in self.byte_rep:
            if step[0][0] == "properties":
                project_step = step

        if project_step is not None:
            return True
        return False

    def _is_valid_repeat_query_(self):
        repeat_step = None
        for step in self.byte_rep:
            if step[0][0] == "repeat":
                repeat_step = step

        if repeat_step is not None:
            for substep in repeat_step:
                if substep[0] == "times" or substep[0] == "until":
                    return True
            return False
        return False

    def _is_repeat_query_(self):
        repeat_step = None
        for step in self.byte_rep:
            if step[0][0] == "repeat":
                repeat_step = step
        if repeat_step is None:
            return False
        else:
            return True

    def dedup(self):
        by_byte = [["dedup"]]
        # print("Deduplicate found in traversal")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def limit(self, limit_num):
        by_byte = [["limit", str(limit_num)]]
        # print("Limit found in traversal")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def count(self):
        by_byte = [["count"]]
        # print("Count found in traversal")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def as_(self, key):
        self.byte_rep.append(["as", key])
        # print("Saving the key as " + key)
        return self

    def coalesce(self, *args):
        # When coalesce is called, basically each traversal inside coalesce appended to original traversal,
        # each is executed independently by conjugating it and retrieving the 1st or available element
        from client.traversal.CoalesceStep import CoalesceStep

        print("Inside coalesce step")
        print(f"traversals are {args}")
        print(f"traversals are {[x.__bytes__() for x in args]}")
        print(f"Bytecode till now {self.byte_rep}")

        # bytecode_till_now = self.byte_rep
        # traversals = []
        # for arg in args:
        #     bytecode = arg.__bytes__()
        #     bytecode = [["coalesce"]] + bytecode
        #     # traversal = [bytecode_till_now, bytecode]
        #     bytecode_till_now.append(bytecode)
        # print(f"Final bytecode is {bytecode_till_now}")

        if len(self.byte_rep) < 3:
            return CoalesceStep([self.byte_rep]).with_traversals(args)
        else:
            return CoalesceStep(self.byte_rep).with_traversals(args)

    def union(self, *args):
        # When coalesce is called, basically each traversal inside coalesce appended to original traversal,
        # each is executed independently by conjugating it and retrieving the 1st or available element
        from client.traversal.UnionStep import UnionStep

        print("Inside union step")
        print(f"traversals are {args}")
        print(f"traversals are {[x.__bytes__() for x in args]}")
        print(f"Bytecode till now {self.byte_rep}")

        if len(self.byte_rep) < 3:
            return UnionStep([self.byte_rep]).with_traversals(args)
        else:
            return UnionStep(self.byte_rep).with_traversals(args)

    def project(self, *args):
        from client.traversal import ProjectStep

        # print(type(args))
        # print(args)

        assert type(args) == list or type(args) == tuple
        assert len(args) > 0

        if len(args) == 1:
            columns = args[0]
            if isinstance(columns, list):
                step = ProjectStep.ProjectStep(self.byte_rep).columns(args)
                step.SKIP_BY = True
            else:
                step = ProjectStep.ProjectStep(self.byte_rep).columns(args)
        else:
            for a in args:
                if isinstance(a, list):
                    raise AttributeError(f"When passing Column.{a}, you can't have multiple values passed to project()")
                assert type(a) == str
                if a in ["C.all", "C.id", "C.firstAll", "C.firstId", "C.last", "C.selectN"]:
                    raise AttributeError(f"Please use different key, as {a} is reserved key")

            step = ProjectStep.ProjectStep(self.byte_rep).columns(args)

        if len(args) == 0:
            raise ValueError("Invalid invocation of project() step. No side effects to project by passed")

        return step

    def __str__(self):
        return str(self.byte_rep)
