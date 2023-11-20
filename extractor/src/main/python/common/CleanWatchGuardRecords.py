import sys, os

sys.path.append(os.path.abspath(os.getcwd() + "\\..\\..\\"))

from common.DataExtractionUtilities import watchguard_maps


class WatchGuardCleaner(object):
    def __init__(self, case_sensitivity):
        """ This class is to clean MsExchange NGIX logs """
        self.data = None
        self.clean_data = []
        self.case = case_sensitivity
        pass

    def fit(self, data):
        """

        Args:
            fname (str): The filename where the recods for WatchGuard are stored
        """
        self.data = data
        return self

    def clean_(self):
        if self.data is None:
            raise AttributeError("Please call fit() method with filename before calling clean method")

        # self.data = self.read_file()
        records = self.clean_and_transform_to_json()

        return records
    #
    # def read_file(self):
    #     with open(self.fname) as f:
    #         lines = f.read().splitlines()
    #     return lines

    def clean_and_transform_to_json(self):
        records = []
        for line in self.data:
            properties = line.split(",")

            objects = dict()
            for i in range(len(properties)):
                prop = properties[i]
                propName = "property{}".format(i)
                propName = watchguard_maps[propName]

                objects[propName] = prop

            objects = {k: v.strip() if isinstance(v, str) else v for k, v in objects.items()}

            if not self.case:
                objects = self.lowercase_values(objects)

            objects = self.expand_object(objects)

            records.append(objects)

        return records

    def lowercase_values(self, object):
        new_object = {}
        for k, v in object.items():
            if isinstance(v, str):
                new_object[k] = v.lower()
            else:
                new_object[k] = v

        return new_object

    def expand_object(self, object):
        new_object = {}
        for k, v in object.items():
            if ";" in v or "=" in v:
                vals = v.split(";")
                for kv in vals:
                    dd = kv.split("=")
                    if len(dd) > 1:
                        key = dd[0]
                        value = dd[1]
                        new_object[key.strip()] = value.strip()
                        # object.pop(k)
            else:
                new_object[k] = v
            if isinstance(v, str):
                new_object[k] = v.lower()
            else:
                new_object[k] = v

        return new_object


if __name__ == '__main__':
    import json

    rec_file = "B:\\Projects\\Freelancing\\data\\firstenergy_and_mithre2\\data2\\wgtraffic_beaconing.logs"

    cleaner = WatchGuardCleaner(case_sensitivity=False)
    cleaner.fit(rec_file)
    records = cleaner.clean_()

    json.dump(records, open("B:\\Projects\\Freelancing\\data\\firstenergy_and_mithre2\\data2\\clean\\wgtraffic_beaconing.logs", "w+"), indent=2)
