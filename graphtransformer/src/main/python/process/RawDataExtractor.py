from gen.graphdb_pb2 import IncomingDataFormat, WindowsRecord, MsExchangeRecord, WatchGuardRecord


class RawDataExtractor:
    WINDOWS_RECORD: WindowsRecord = None
    WATCHGUARD_RECORD: WatchGuardRecord = None
    SYSMON_RECORD = None
    MSEXCHANGE_RECORD: MsExchangeRecord = None

    def __init__(self, data: IncomingDataFormat):
        """

        Args:
            data:
        """
        self.DATA = data

    @staticmethod
    def is_custom_property_present(message, property_name):
        try:
            getattr(message, property_name)
            return True
        except AttributeError:
            return False

    def extract(self):
        if RawDataExtractor.is_custom_property_present(self.DATA, "windowsRecord"):
            self.WINDOWS_RECORD = self.DATA.windowsRecord

        if RawDataExtractor.is_custom_property_present(self.DATA, "exchangeRecords"):
            self.MSEXCHANGE_RECORD = self.DATA.exchangeRecords

        if RawDataExtractor.is_custom_property_present(self.DATA, "networkRecords"):
            self.WATCHGUARD_RECORD = self.DATA.networkRecords

        return self

    def convert(self):
        records = {
            "windows": self._convert_windows_records_to_graph_() if len(self.WINDOWS_RECORD) > 0 else self.WINDOWS_RECORD,
            "msexchange": self._convert_exchange_records_to_graph_() if len(self.MSEXCHANGE_RECORD) > 0 else self.MSEXCHANGE_RECORD,
            "watchguard": self._convert_network_records_to_graph_() if len(self.WATCHGUARD_RECORD) > 0 else self.WATCHGUARD_RECORD
        }

        return records

    def _convert_windows_records_to_graph_(self):
        keys = [field.name for field in self.WINDOWS_RECORD[0].DESCRIPTOR.fields]

        records = []
        for row in self.WINDOWS_RECORD:
            record = {}
            for key in keys:
                if RawDataExtractor.is_custom_property_present(row, key):
                    record[key] = getattr(row, key)
            records.append(record)

        return records

    def _convert_exchange_records_to_graph_(self):
        keys = [field.name for field in self.MSEXCHANGE_RECORD[0].DESCRIPTOR.fields]

        records = []
        for row in self.MSEXCHANGE_RECORD:
            record = {}
            for key in keys:
                if RawDataExtractor.is_custom_property_present(row, key):
                    record[key] = getattr(row, key)
            records.append(record)

        return records

    def _convert_network_records_to_graph_(self):
        keys = [field.name for field in self.WATCHGUARD_RECORD[0].DESCRIPTOR.fields]

        records = []
        for row in self.WATCHGUARD_RECORD:
            record = {}
            for key in keys:
                if RawDataExtractor.is_custom_property_present(row, key):
                    record[key] = getattr(row, key)
            records.append(record)

        return records
