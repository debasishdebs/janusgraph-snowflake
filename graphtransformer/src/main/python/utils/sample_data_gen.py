import json
import os

from gen.graphdb_pb2 import IncomingDataFormat, MsExchangeRecord, WindowsRecord, WatchGuardRecord
from utils.constants import TIME_PROPERTIES, GEO_PROPERTIES, Commons


class SampleDataGenerator:
    SAMPLE_DATA_DIRECTORY = "D:\\Projects\\Projects\\Freelancing\\Elysium Analytics\\" \
                                            "graphdb-in-snowflake\\snowflake-graphdb\\sample\\"

    MSEXCHANGE_RECORD_FILE = "msexchange_phishing_1565175929_120h_2019-08-07.extracted.records"
    SEPC_RECORD_FILE = "symantecendpoint_1565181764_120h_2019-08-07.extracted.records"
    SYSMON_RECORD_FILE = "sysmon_phishing_1565180893_120h_2019-08-07.extracted.records"
    WATCHGUARD_DHCP_RECORD_FILE = "watchguard_dhcp_1565182738_120h_2019-08-07.extracted.records"
    WATCHGUARD_DOMAINS_RECORD_FILE = "wgguard_domains_1565181161_120h_2019-08-07.extracted.records"
    WATCHGUARD_NETWORK_RECORD_FILE = "wgtraffic_1565173483_1dd_2019-08-07extracted.records"
    WINDOWS_RECORD_FILE = "windows_phishing_1565175929_120h_2019-08-07.extracted.records"

    def __init__(self):
        self.MSEXCHANGE_DATA = None
        self.SPEC_DATA = None
        self.SYSMON_DATA = None
        self.WATCHGUARD_DHCP_DATA = None
        self.WATCHGUARD_DOMAINS_DATA = None
        self.WATCHGUARD_NETWORK_DATA = None
        self.WINDOWS_DATA = None

    def extract(self):
        self.MSEXCHANGE_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.MSEXCHANGE_RECORD_FILE)))
        self.SPEC_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.SEPC_RECORD_FILE)))
        self.SYSMON_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.SYSMON_RECORD_FILE)))
        self.WATCHGUARD_DHCP_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.WATCHGUARD_DHCP_RECORD_FILE)))
        self.WATCHGUARD_DOMAINS_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.WATCHGUARD_DOMAINS_RECORD_FILE)))
        # self.WATCHGUARD_NETWORK_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.WATCHGUARD_NETWORK_RECORD_FILE)))
        self.WINDOWS_DATA = json.load(open(os.path.abspath(self.SAMPLE_DATA_DIRECTORY + self.WINDOWS_RECORD_FILE)))

    def _clean_records_(self):
        for data_records in [self.MSEXCHANGE_DATA, self.SPEC_DATA, self.SYSMON_DATA, self.WINDOWS_DATA]:#, self.WATCHGUARD_NETWORK_DATA]:
            for record in data_records:
                for k in record.keys():
                    if "-" in k:
                        record[k.replace("-", "_")] = record.pop(k)
        return self

    def generate(self):
        self._clean_records_()
        self._clean_records_()

        msexchange_records = self._convert_msexchange_to_protobuf_()
        windows_records = self._convert_windows_to_protobuf_()
        # wgtraffic_records = self._convert_watchguard_to_protobuf_()
        # sysmon = self._convert_sysmon_to_protobuf_()

        data = IncomingDataFormat()
        data.windowsRecord.extend(windows_records)
        data.exchangeRecords.extend(msexchange_records)
        # data.networkRecords.extend(wgtraffic_records)
        # data.windowsRecord.extend(sysmon)
        return data

    def _generate_time_and_geo_fields_(self, record):
        time_fields = {}
        geo_fields = {}
        for field in TIME_PROPERTIES:
            if field in record:
                record_value = record[field]
                time_proto = Commons.time_string_to_time_protobuf(record_value)
                time_fields[field] = time_proto

                record[field] = time_proto

        for field in GEO_PROPERTIES:
            if field in record:
                record_value = record[field]
                geo_proto = Commons.geo_string_to_geo_protobuf(record_value)
                geo_fields[field] = geo_proto

                record[field] = geo_proto

        return record

    def _convert_msexchange_to_protobuf_(self):
        msexchange_records = []
        for record in self.MSEXCHANGE_DATA:
            row = self._generate_time_and_geo_fields_(record)
            msexchange_record = MsExchangeRecord(**row)
            msexchange_records.append(msexchange_record)
        return msexchange_records

    def _convert_windows_to_protobuf_(self):
        windows_records = []
        for record in self.WINDOWS_DATA:
            row = self._generate_time_and_geo_fields_(record)
            rrow = dict()
            for k, v in row.items():
                if k in self.WINDOWS_IGNORE:
                    continue
                rrow[self.__convert_column_name_for_windows__(k)] = v
            windows_record = WindowsRecord(**rrow)
            windows_records.append(windows_record)
        return windows_records

    WINDOWS_IGNORE = ["Keywords", "SourceName", "ProviderGuid", "Version", "Task", "OpcodeValue", "RecordNumber",
                      "ThreadID", "Channel", "Message", "SubjectLogonId", "TargetLogonId", "AuthenticationPackageName",
                      "TransmittedServices", "LmPackageName", "KeyLength", "ImpersonationLevel", "SourceModuleName",
                      "SourceModuleType", "ActivityID", "PrivilegeList", "RestrictedAdminMode", "VirtualAccount",
                      "TargetLinkedLogonId", "ElevatedToken", "ObjectServer", "ObjectType", "ObjectName", "HandleId",
                      "AccessMask", "SamAccountName", "DisplayName", "UserPrincipalName", "ScriptPath", "ProfilePath",
                      "UserWorkstations", "PasswordLastSet", "AccountExpires", "PrimaryGroupId", "AllowedToDelegateTo",
                      "OldUacValue", "NewUacValue", "UserAccountControl", "UserParameters", "SidHistory", "LogonHours",
                      "MemberName", "MemberSid"]

    def __convert_column_name_for_windows__(self, k):
        if k == "EventTime": return "EVENT_TIME"
        if k == "Hostname": return "HOSTNAME"
        if k == "Keywords": return "KEYWORDS"
        if k == "EventType": return "EVENT_TYPE"
        if k == "EventID": return "EVENT_ID"
        if k == "LogonType": return "LOGON_TYPE"
        return k

    def _convert_watchguard_to_protobuf_(self):
        wgtraffic_records = []
        for record in self.WATCHGUARD_NETWORK_DATA:
            row = self._generate_time_and_geo_fields_(record)
            wgtraffic_record = WatchGuardRecord(**row)
            wgtraffic_records.append(wgtraffic_record)
        return wgtraffic_records

    def _convert_sysmon_to_protobuf_(self):
        sysmon_records = []
        for record in self.SYSMON_DATA:
            row = self._generate_time_and_geo_fields_(record)
            sysmon_record = WindowsRecord(**row)
            sysmon_records.append(sysmon_record)
        return sysmon_records


if __name__ == '__main__':
    gen = SampleDataGenerator()
    gen.extract()
    data = gen.generate()

    print(data)
