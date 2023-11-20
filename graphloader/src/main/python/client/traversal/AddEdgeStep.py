from multipledispatch import dispatch
from uuid import UUID


class AddEdgeStep:
    def __init__(self, update=False, bytecode=None):
        self.byte_rep = [] if bytecode is None else bytecode if isinstance(bytecode, list) else []
        self.UPDATE = update
        self.ID = None
        self.LABEL = None
        self.PROPERTIES = {}
        self.SRC = None
        self.DST = None

    def __str__(self):
        return str(self.byte_rep)

    def withId(self, id='random'):
        self.ID = id.hex if isinstance(id, UUID) else id
        return self

    def withLabel(self, label='edge'):
        self.LABEL = label
        return self

    @dispatch(int)
    def from_(self, id):
        self.SRC = id
        return self

    @dispatch(str, str)
    def from_(self, property_key, property_val):
        self.SRC = {property_key: property_val}
        return self

    @dispatch(int)
    def to(self, id):
        self.DST = id
        return self

    @dispatch(str, str)
    def to(self, property_key, property_val):
        self.DST = {property_key: property_val}
        return self

    def property(self, property_key, property_value):
        if property_key not in self.PROPERTIES:
            self.PROPERTIES.update({property_key: [property_value]})
        else:
            self.PROPERTIES[property_key].append(property_value)
        return self

    def _generate_bytecode_(self):
        tmp_byte = [["AddEdge", str(self.UPDATE).lower()], ["T.id", str(self.ID)], ["T.label", self.LABEL]]

        from_byte = ["from"]
        if isinstance(self.SRC, dict):
            assert len(self.SRC) == 1
            property_key = list(self.SRC.keys())[0]
            property_val = list(self.SRC.values())[0]
            from_byte.extend([property_key, property_val])
        else:
            from_byte.extend(["T.id", str(self.SRC)])

        # print("from byte ", from_byte)

        to_byte = ["to"]
        if isinstance(self.DST, dict):
            assert len(self.DST) == 1
            property_key = list(self.DST.keys())[0]
            property_val = list(self.DST.values())[0]
            to_byte.extend([property_key, property_val])
        else:
            to_byte.extend(["T.id", str(self.DST)])

        # print("to byte ", to_byte)

        tmp_byte = tmp_byte + [from_byte] + [to_byte]

        # print("tmp byte ", tmp_byte)

        prop_byte = []
        for k, v in self.PROPERTIES.items():
            prop_code = ["properties", k]
            for elem in v:
                prop_code.append(str(elem))
            prop_byte.append(prop_code)

        # print("prop byte ", prop_byte)

        bytecode = tmp_byte + prop_byte
        # print("bytecode ", bytecode)

        if self._is_bytecode_already_present_(bytecode):
            return self.byte_rep
        else:
            self.byte_rep = tmp_byte + prop_byte if len(self.byte_rep) == 0 else [self.byte_rep, tmp_byte + prop_byte]

        return self

    def _is_bytecode_already_present_(self, bytecode):
        edge_ids = []
        for step in self.byte_rep:
            # print("step ", step)
            if step[0] == "T.id":
                if step[1] not in edge_ids:
                    edge_ids.append(step[1])
                    break
                break

        for step in bytecode:
            if step[0] == "T.id":
                if step[1] in edge_ids:
                    # print("present")
                    return True
        return False

    def next(self):
        from client.utils.common_resources import Commons
        from client.connection.ExecuteByteCode import ExecuteByteCode

        if self.SRC is None or self.DST is None:
            raise ValueError("Invalid edge added, please define the SRC/DST for respective edge")

        bytecode = Commons.get_bytecode()

        # print("Bytecode before")
        # print(self.byte_rep)
        self._generate_bytecode_()
        # print("bytecode after")
        # print(self.byte_rep)

        if len(bytecode) == 0:
            # print(f"Wrapping brackets around non existant bytecode {self.byte_rep}")
            byte_code = [self.byte_rep]
        else:
            # print(f"Wrapping brackets around existing bytecode {bytecode} and cuuent one {self.byte_rep}")
            byte_code = bytecode + [self.byte_rep]

        Commons.reset_bytecode()

        return ExecuteByteCode(byte_code).execute().to_json()

    def hold(self):
        from client.utils.common_resources import Commons

        if self.SRC is None or self.DST is None:
            raise ValueError("Invalid edge added, please define the SRC/DST for respective edge")

        self._generate_bytecode_()
        # print(f"Holding {self.byte_rep} in AddEdge")
        Commons.put_bytecode(self.byte_rep)
        # if len(self.byte_rep) > 2:
        #     Commons.put_bytecode(self.byte_rep)
        # else:
        #     for bytecode in self.byte_rep:
        #         Commons.put_bytecode(bytecode)
        return Commons.get_bytecode()
