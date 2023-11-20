from client.traversal import AnonymousTraversal
from client.connection.ExecuteByteCode import ExecuteByteCode


class ProjectStep:
    COLUMNS = None
    SKIP_BY = False

    def __init__(self, byte_arr=None):
        # By step is optional

        super().__init__()

        if byte_arr is None:
            self.byte_rep = ["project"]
        else:
            self.byte_rep = byte_arr.append([["project"]])
            self.byte_rep = byte_arr

    def columns(self, cols):
        self.COLUMNS = cols
        self.byte_rep[-1][-1].append(cols[0]) if len(cols) == 1 else self.byte_rep[-1][-1].extend(cols)
        return self

    def by_(self, tr):
        """

        Args:
            tr (AnonymousTraversal.__):

        Returns:

        """

        if self.SKIP_BY:
            raise AttributeError("You passed a Column in project but called by_() which is invalid operation")

        # print("By in project")
        # print(tr)
        # print(self.byte_rep[-1])
        # print(self.byte_rep)
        # print(["by"].extend(tr))
        # print(["by", *tr])
        by_byte = ["by"]
        by_byte.extend(tr)
        # print(by_byte)
        # print("end by")
        self.byte_rep[-1].append(by_byte)

        return self

    def __str__(self):
        return str(self.byte_rep)

    def dedup(self):
        by_byte = [["dedup"]]
        # print("Deduplicate found in project")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def limit(self, limit_num):
        by_byte = [["limit", str(limit_num)]]
        # print("Limit found in project")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def count(self):
        by_byte = [["count"]]
        # print("Count found in project")
        # print(by_byte)
        # print(self.byte_rep)
        self.byte_rep.append(by_byte)
        # print(self.byte_rep)
        return self

    def next(self):
        # print("I'm inside next of ProjectStep")
        # print(self.byte_rep)
        # self.byte_rep[-1][-1].extend(self.COLUMNS) if len(self.COLUMNS[0]) == 1 else self.byte_rep[-1][-1].extend(self.COLUMNS)
        # print(self.byte_rep)
        # print(self.byte_rep)
        return ExecuteByteCode(self.byte_rep).execute().to_json()
