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

        to_byte = ["to"]
        if isinstance(self.DST, dict):
            assert len(self.DST) == 1
            property_key = list(self.DST.keys())[0]
            property_val = list(self.DST.values())[0]
            to_byte.extend([property_key, property_val])
        else:
            to_byte.extend(["T.id", str(self.DST)])

        tmp_byte = tmp_byte + [from_byte] + [to_byte]

        prop_byte = []
        for k, v in self.PROPERTIES.items():
            prop_code = ["properties", k]
            for elem in v:
                prop_code.append(str(elem))
            prop_byte.append(prop_code)

        self.byte_rep = tmp_byte + prop_byte if len(self.byte_rep) == 0 else [self.byte_rep, tmp_byte + prop_byte]

        return self

    def next(self):
        from client.utils.common_resources import Commons
        from client.connection.ExecuteByteCode import ExecuteByteCode

        if self.SRC is None or self.DST is None:
            raise ValueError("Invalid edge added, please define the SRC/DST for respective edge")

        bytecode = Commons.get_bytecode()
        self._generate_bytecode_()

        if len(bytecode) == 0:
            byte_code = [self.byte_rep]
        else:
            byte_code = bytecode + [self.byte_rep]

        Commons.reset_bytecode()

        print("I'm inside next of AddEdgeStep with bytecode ", byte_code)
        return ExecuteByteCode(byte_code).execute().to_json()

    def hold(self):
        from client.utils.common_resources import Commons

        if self.SRC is None or self.DST is None:
            raise ValueError("Invalid edge added, please define the SRC/DST for respective edge")

        self._generate_bytecode_()
        Commons.put_bytecode(self.byte_rep)
        # if len(self.byte_rep) > 2:
        #     Commons.put_bytecode(self.byte_rep)
        # else:
        #     for bytecode in self.byte_rep:
        #         Commons.put_bytecode(bytecode)
        print("I'm inside hold of AddEdgeStep", len(self.byte_rep))
        return Commons.get_bytecode()
