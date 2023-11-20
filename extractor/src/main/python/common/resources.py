class Resources:
    DATA: list = []
    DS: str = ""

    @staticmethod
    def put_data(data):
        Resources.DATA.append(data)

    @staticmethod
    def get_data():
        return Resources.DATA

    @staticmethod
    def put_ds(ds):
        Resources.DS = ds

    @staticmethod
    def get_ds():
        return Resources.DS
