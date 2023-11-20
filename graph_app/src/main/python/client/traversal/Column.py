class Column:

    @staticmethod
    def all_():
        return ["select", "C.all", ""]

    @staticmethod
    def id_():
        return ["select", "C.id", ""]

    @staticmethod
    def last():
        return "C.last"

    @staticmethod
    def first_all():
        return ["select", "C.firstAll", ""]

    @staticmethod
    def first_id():
        return ["select", "C.firstId", ""]
