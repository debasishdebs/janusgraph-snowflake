class AddVertexStep:
    def __init__(self, update=False):
        self.byte_rep = []
        self.UPDATE = update
        self.ID = None
        self.LABEL = None
        self.PROPERTIES = {}

    def __str__(self):
        return str(self.byte_rep)

    def withId(self, id='random'):
        self.ID = id
        return self

    def withLabel(self, label='vertex'):
        self.LABEL = label
        return self

    def property(self, property_key, property_value):
        if property_key not in self.PROPERTIES:
            self.PROPERTIES.update({property_key: [property_value]})
        else:
            self.PROPERTIES[property_key].append(property_value)
        return self

    def addE(self, id, label):
        from client.traversal.AddEdgeStep import AddEdgeStep
        self._generate_bytecode_()
        return AddEdgeStep(False, self.byte_rep).withLabel(label).withId(id).from_(self.ID)

    def _generate_bytecode_(self):
        tmp_byte = [["AddVertex", str(self.UPDATE).lower()], ["T.id", str(self.ID)], ["T.label", self.LABEL]]
        prop_byte = []
        for k, v in self.PROPERTIES.items():
            prop_code = ["properties", k]
            for elem in v:
                prop_code.append(str(elem))
            prop_byte.append(prop_code)
        self.byte_rep = tmp_byte + prop_byte
        return self

    def next(self):
        from client.utils.common_resources import Commons
        from client.connection.ExecuteByteCode import ExecuteByteCode

        bytecode = Commons.get_bytecode()
        self._generate_bytecode_()

        if len(bytecode) == 0:
            byte_code = [self.byte_rep]
        else:
            byte_code = bytecode + [self.byte_rep]

        Commons.reset_bytecode()

        # print("I'm inside next of AddVertexStep with bytecode ", byte_code)
        return ExecuteByteCode(byte_code).execute().to_json()

    def hold(self):
        from client.utils.common_resources import Commons
        self._generate_bytecode_()
        # print(f"Holding {self.byte_rep} in AddEdge")
        Commons.put_bytecode(self.byte_rep)
        return Commons.get_bytecode()
