from snowflake import connector
from utils.commons import Utilities
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json
import itertools
import numpy as np
import datetime as dt
from threading import current_thread
import subprocess
from collections import OrderedDict

LOG_TIME = dt.datetime.now().strftime("%Y%m%d_%H%M")
LOG_FNAME = f"../../resources/output/groupping_{LOG_TIME}.log"

print(LOG_FNAME)

GROUP_ASSIGNMENT_TRACKER = {}
ID_ASSIGNMENT_TRACKER = []


class AlertGroupings(object):
    def __init__(self, local=False, tbl="AllFindings", fname=None, addnl_prop=None, prop_type_map=None,
                 purge_prior_cols=False):
        if not local:
            if not tbl:
                raise AttributeError(f"Please pass a valid table to read from, got {tbl}")
            else:
                sql = f"select * from {tbl};"
            self.df: pd.DataFrame = self.read_snowflake_sql(sql)
        else:
            if not fname:
                raise AttributeError(f"Please pass a valid file name to read from, got {fname}")
            else:
                self.df: pd.DataFrame = self.read_all_findings(fname)

        self.df_ll = self.df.to_dict(orient='records')

        self.PROPERTIES_TO_INTERSECT_ON = ["instance_id", "instance_id2", "private_ip", "public_ip", "src_user_name",
                                           "src_caller_ip", "remote_ip", "local_ip", "s3_bucket_name"]

        self.PROPERTIES_TYPE_MAP = {"ip": ["private_ip", "public_ip", "src_caller_ip", "remote_ip", "local_ip"],
                                    "instance": ["instance_id"], "s3": ["s3_bucket_name"], "user_name": []}
        if addnl_prop:
            assert isinstance(addnl_prop, list)
            if purge_prior_cols:
                self.PROPERTIES_TO_INTERSECT_ON = addnl_prop
            else:
                self.PROPERTIES_TO_INTERSECT_ON.extend(addnl_prop)

        if prop_type_map:
            assert isinstance(prop_type_map, dict)
            if purge_prior_cols:
                self.PROPERTIES_TYPE_MAP = prop_type_map
            else:
                self.PROPERTIES_TYPE_MAP.update(prop_type_map)
        # self.IDS_ASSIGNED = list(range(1, len(self.df)+1))
        self.IDS_ASSIGNED = []
        self.RECURSION = True

    def read_snowflake_sql(self, sql):
        credential_dict = Utilities.load_properties("../../resources/credentials.properties")

        conn = URL(
            account=credential_dict["account"].split(".")[0],
            user=credential_dict["user"],
            password=credential_dict["password"],
            database=credential_dict["database"],
            schema=credential_dict["schema"],
            warehouse=credential_dict["warehouse"],
        )

        SNOWFLAKE_ENGINE = create_engine(conn)
        session = sessionmaker(bind=SNOWFLAKE_ENGINE)

        conn = SNOWFLAKE_ENGINE.connect()

        df = pd.read_sql(sql, conn)
        return df

    def read_all_findings(self, fname):
        print(fname)
        # df = pd.read_excel(fname, engine='openpyxl', index_col=0)
        df = pd.read_csv(fname)
        # df = df.head(200)
        return df

    def initialize_groups_for_alerts(self):
        self.df.at[0, "group"] = 0
        self.df.at[1:, "group"] = -1
        return self

    def get_property_map_for_groups(self):
        def g(rows):
            null_cols = rows.loc[:, (rows != -1).all()]
            unique_cols = null_cols.columns.tolist()
            unique_col_vals = {}
            for c in unique_cols:
                if c in self.PROPERTIES_TO_INTERSECT_ON:
                    unique_col_vals[c] = list(set(null_cols[c].unique().tolist()))
            return unique_col_vals

        group_maps = self.df.groupby("group")[self.df.columns.tolist()].apply(g)
        return group_maps

    def find_other_rows_with_similar_elems(self, curr_row, curr_idx):
        mask = ~curr_row.T.isna().values
        mask = mask.tolist()
        mask = [x[0] for x in mask]
        # mask = [x for x in mask]
        # print()
        valid_cells = curr_row.T[mask].T
        # print(valid_cells.T.loc[mask])
        # print(mask, valid_cells)
        valid_prop_map = valid_cells.to_dict()

        common_rows = []
        # for _ in range(len(self.df_ll)):
        #     row = pd.Series(self.df_ll[_])
        for _, row in self.df.iterrows():
        #     log_to_file(f"Comparing index {_+1} with {curr_idx+1}")
            if _ == curr_idx:
                continue
            else:
                if any(x in [y for y in row.to_frame().T.columns if y != "group"] for x in valid_prop_map.keys()):
                    # Checks if any of properties among the valid props in curr row, matches to any of valid props in
                    # other row, if true downstream ->
                    curr_row_not_na_cols_mask = ~row.T.isna().values
                    curr_row_not_na_cols_mask = curr_row_not_na_cols_mask.tolist()
                    valid_elems = row.T[curr_row_not_na_cols_mask].T

                    common_cols = set(list(valid_elems.to_dict().keys())).union(set(valid_prop_map.keys()))
                    # Use only non na cells/props from current row. These reduces number of iterations in next step.
                    # We end up eliminating iterating over cols which contain null either in curr_row or main_row
                    # And we compare against cols containing valid values only among family of columns.

                    # Find out the common columns b/w current row & the row being compared
                    for c in common_cols:
                        if c not in self.PROPERTIES_TO_INTERSECT_ON:
                            continue
                        # print("B:", row.to_frame().T[c].values.tolist()[0], list(valid_prop_map[c].values())[0], c)

                        # Added new logic: Now only check for same column, but check for family of cols
                        family_cols_key = [k for k, v in self.PROPERTIES_TYPE_MAP.items() if c in v][0]
                        # Find out the family key. For eg ip_address_1 falls under family IP.
                        family_oth_cols = self.PROPERTIES_TYPE_MAP[family_cols_key]
                        # Other columns of family also to be compared for equality
                        family_cols = list(set(family_oth_cols + [c]))

                        # log_to_file(f"Family cols for {c} are {family_cols}")
                        status = False
                        for fc in family_cols:
                            # curr_val = list(valid_prop_map[c])[0] if c in valid_prop_map else np.nan
                            curr_val = list(valid_prop_map[c].values())[0] if c in valid_prop_map else np.nan

                            row_val = row.to_frame().T[fc].values.tolist()[0]
                            # log_to_file(f"For family col {fc}, curr val (Using c) {curr_val} and row_val {row_val}")
                            if (pd.notna(curr_val) and pd.notna(row_val)) and (curr_val == row_val):

                                log_to_file(f"Found common element for row {curr_idx+1} index (added +1) with {_+1} idx on cols {c} and {fc}")
                                # print(f"Found common element for row {curr_idx+1} index (added +1) with {_+1} idx on cols {c} and {fc}")
                                common_rows.append([_, row, {curr_val: [c, fc]}])
                                # We will break from here if we find any common rows. If we find equality with 1st
                                # family column we don't need to do further iterations unnecessary
                                status = True
                                break

                            if status:
                                break

        # print(f"Num of common rows for idx {curr_idx+1} are {len(common_rows)}")
        # log_to_file(f"Num of common rows for idx {curr_idx+1} are {len(common_rows)}")
        return common_rows

    def reassign_groups_to_common_rows(self, common_rows, curr_group, curr_idx, keys, values, indices):
        for row_val in common_rows:
            idx = row_val[0]
            value_map = row_val[2]

            if value_map:
                value_matched = list(value_map.keys())[0]
                base_col = value_map[value_matched][0]
                matched_col = value_map[value_matched][1]
            else:
                value_matched = None
                base_col = None
                matched_col = None

            old_group = self.df.iloc[idx]['group']
            self.df.loc[self.df.index == idx, "group"] = curr_group
            # print(f"Changed group from {old_group} to {curr_group} for {idx+1} idx")

            if idx+1 not in GROUP_ASSIGNMENT_TRACKER:
                GROUP_ASSIGNMENT_TRACKER[idx+1] = OrderedDict()
                tracker_value_to_insert = OrderedDict({1: {"old_group": old_group, "new_group": curr_group, "keys": keys,
                                                           "values": values, "base_idx": curr_idx,
                                                           "lowest_group_indices": indices, "lowest_group": curr_group,
                                                           "map": {"value": value_matched, "base_col": base_col,
                                                                   "matched_col": matched_col}}})
                GROUP_ASSIGNMENT_TRACKER[idx+1] = tracker_value_to_insert
            else:
                tot_iter_done = max(GROUP_ASSIGNMENT_TRACKER[idx+1].keys())
                tracker_value_to_insert = OrderedDict({tot_iter_done+1: {"old_group": old_group, "values": values,
                                                                         "new_group": curr_group, "keys": keys,
                                                                         "base_idx": curr_idx,
                                                                         "lowest_group_indices": indices,
                                                                         "lowest_group": curr_group,
                                                                         "map": {"value": value_matched,
                                                                                 "base_col": base_col,
                                                                                 "matched_col": matched_col}}})
                GROUP_ASSIGNMENT_TRACKER[idx+1].update(tracker_value_to_insert)

        return self

    def create_new_group_value(self, group_maps):
        max_group_val = max(list(group_maps.keys()))
        return max_group_val + 1

    def execute(self):

        if self.RECURSION:
            df = self.execute_using_recursion()
            self.df = df
        else:
            for _, row in self.df.iterrows():
                log_to_file(50*"-")
                print(50*"-")
                print(f"Finding common elements for {_+1}th index (added +1) row")
                log_to_file(f"Finding common elements for {_+1}th index (added +1) row")
                # print(row)
                # print(pd.Series(row))
                t1 = dt.datetime.now()
                common_rows = self.find_other_rows_with_similar_elems(row.to_frame().T, _)
                # common_rows = self.find_other_rows_with_similar_elems(pd.Series(row), _)
                t2 = dt.datetime.now()
                print(f"Took {t2-t1} time to find common rows for above")
                log_to_file(f"Took {t2-t1} time to find common rows for above")
                if common_rows:
                    # print(f"Curr row: {row} and common: {common_rows} and assigning group as {row['group']} & {_}")
                    curr_grp = row["group"]

                    lowest_group, indices = self.find_lowest_assigned_group_from_common_elems(common_rows)
                    curr_grp = lowest_group

                    if curr_grp == -1:
                        group_maps = self.get_property_map_for_groups()
                        curr_grp = self.create_new_group_value(group_maps)

                    common_values = list(set([list(r[2].keys())[0] for r in common_rows if list(r[2].keys())]))
                    common_keys = [list(r[2].values())[0] for r in common_rows if r[2].values()]
                    common_unique_keys = list(set(itertools.chain(*common_keys)))

                    common_rows = common_rows + [[_, row, {}]]
                    self.reassign_groups_to_common_rows(common_rows, curr_grp, _+1, common_unique_keys, common_values, indices)
                    indices += [_+1]

                    print(f"Assigned rows with idx {indices} with group {curr_grp} due to {common_values} \
                          found on keys {common_unique_keys}")
                    log_to_file(f"Assigned rows with idx {indices} with group {curr_grp} due to {common_values} \
                                found on keys {common_unique_keys}")
                    # print(30*"=")
                else:
                    # print(f"No common rows found for {_}")
                    group_maps = self.get_property_map_for_groups()
                    new_grp = self.create_new_group_value(group_maps)
                    self.df.at[_, "group"] = new_grp
                    # print(self.df["group"].unique())
                    print(f"No common rows found & Assigned row {_} with group {new_grp}")

                with open("../../resources/output/group_assignment_tracker_1.json", "w+") as f:
                    json.dump(GROUP_ASSIGNMENT_TRACKER, f, indent=2)

            print(100*"=")
            print(self.df)
            group_maps = self.get_property_map_for_groups()
            json.dump(json.loads(group_maps.to_json()), open("../../resources/output/properties_groups_1.json", "w+"),
                      indent=1)

        return self.df

    def execute_using_recursion(self):
        self.initialize_groups_for_alerts()

        t1 = dt.datetime.now()
        df_grouped = self.group_rows_into_common_elements()
        log_to_file(f"Time taken to group {dt.datetime.now() - t1}")

        t1 = dt.datetime.now()
        dfs = self.group_rows_based_on_common_elems(df_grouped)
        # pprint.pprint(dfs)
        log_to_file(f"Time taken to group rows based on common elements {dt.datetime.now() - t1}")

        t1 = dt.datetime.now()
        common_rows_overall = self.find_matching_pairs_of_rows_for_each_row(dfs)
        # pprint.pprint(common_rows_overall)
        log_to_file(f"Time taken to group rows based on common elements {dt.datetime.now() - t1}")

        t1 = dt.datetime.now()
        iter = 1
        for _, row in self.df.iterrows():
            group_no = self.df["group"].max() + 1

            log_to_file(f"{len(self.IDS_ASSIGNED)}, {_ + 1}, {_ + 1 in self.IDS_ASSIGNED}")
            if _+1 in self.IDS_ASSIGNED:
                continue

            depth = 1
            self.reassign_groups(common_rows_overall, _+1, group_no, depth)
            log_to_file(self.IDS_ASSIGNED)
            log_to_file(50*"=")
            # ID_ASSIGNMENT_TRACKER = []
            # group_no += 1
            iter += 1

        print(f"Total iterations {iter}")
        print(f"Time taken to assign groups {dt.datetime.now() - t1}")
        return self.df

    @staticmethod
    def find_lowest_assigned_group_from_common_elems(common_elems):
        groups = []
        for elem in common_elems:
            grp = elem[1]["group"]
            if grp == -1:
                continue
            if grp not in groups:
                groups.append(grp)
        min_group = min(groups) if len(groups) > 0 else -1
        min_group_indices = [r[0]+1 for r in common_elems if r[1]["group"] == min_group]
        return min_group, min_group_indices

    def group_rows_into_common_elements(self):
        grouped = self.df.groupby(["id"]).apply(lambda x: x[[c for c in x.columns
                                                              if c != "id"]].to_dict("records")).\
            reset_index(name="attrs")
        df_grouped = self.df.merge(grouped, on="id")
        return df_grouped

    def group_rows_based_on_common_elems(self, df):
        dfs = {}
        for prop in self.PROPERTIES_TO_INTERSECT_ON:
            d = df.groupby([prop], dropna=True)["id"].apply(list).reset_index(name="ids")
            dfs[prop] = d
        return dfs

    def reassign_groups(self, common_rows_overall, row_idx, group, depth):
        commons = common_rows_overall[row_idx]
        matched_idx = []
        for val, matches in commons.items():
            for match in matches["match_pair"]:
                matched_idx.extend(match["matched_idx"])

        matched_idx = list(set(matched_idx))

        ID_ASSIGNMENT_TRACKER.append(row_idx)
        unique_ids_added = list(set(ID_ASSIGNMENT_TRACKER))
        matched_idx = [i for i in matched_idx if i not in unique_ids_added]
        log_to_file(f"Assigning {matched_idx} for {row_idx} with group {group}")
        # matched_idx = [x for x in matched_idx if x != row_idx]

        if matched_idx:
            for idx in matched_idx:
                self.reassign_groups(common_rows_overall, idx, group, depth)
                log_to_file(f"xxxxxxxxxx Assigned {row_idx} with group {group} as depth {depth}")
                self.df.loc[self.df.index == row_idx-1, "group"] = group
                ID_ASSIGNMENT_TRACKER.append(row_idx)
                depth += 1

                self.IDS_ASSIGNED.append(row_idx)
        else:
            log_to_file(f"------- Assigned {row_idx} with group {group} at depth {depth}")
            self.df.loc[self.df.index == row_idx-1, "group"] = group
            ID_ASSIGNMENT_TRACKER.append(row_idx)
            depth += 1

            self.IDS_ASSIGNED.append(row_idx)

        self.IDS_ASSIGNED = list(set(self.IDS_ASSIGNED))
        return self

    def find_matching_pairs_of_rows_for_each_row(self, dfs):
        common_rows_overall = {}
        for _, row in self.df.iterrows():
            row_id = row["id"]

            common_rows_for_row = {}
            for prop in self.PROPERTIES_TO_INTERSECT_ON:
                family_cols = [vals for vals in self.PROPERTIES_TYPE_MAP.values() if prop in vals][0]
                family_cols = list(set(family_cols))
                for fc in family_cols:
                    row_val = row[fc]
                    dd = dfs[fc]
                    rows = dd[dd[fc] == row_val]
                    common_rows = rows["ids"].tolist()

                    if common_rows:
                        common_rows = [i for i in common_rows[0] if i != row_id]

                    if common_rows:
                        # print(f"For row idx {row_id}, property {prop} matched with family col {fc} and value {row_val} and IDs matched {common_rows}")
                        common_rows = [str(c) for c in common_rows]
                        if row_val not in common_rows_for_row:
                            common_rows_for_row[row_val] = {"base_idx": row_id, "match_pair": [
                                {"base_col": prop, "matched_col": fc, "matched_idx": ",".join(common_rows)}
                            ]}
                        else:
                            match_pair = common_rows_for_row[row_val]["match_pair"]
                            match_pair.append(
                                {"base_col": prop, "matched_col": fc, "matched_idx": ",".join(common_rows)}
                            )

                            common_rows_for_row[row_val]["match_pair"] = match_pair

            if common_rows_for_row:
                dedup_common_rows = {}
                for val in common_rows_for_row.keys():
                    dedup_commons = [dict(t) for t in {tuple(d.items()) for d in common_rows_for_row[val]["match_pair"]}]
                    dedup_common_rows[val] = {}

                    for tmp in dedup_commons:
                        matched_indices = tmp["matched_idx"].split(",")
                        matched_indices = [int(i) for i in matched_indices]
                        tmp["matched_idx"] = matched_indices

                    dedup_common_rows[val]["match_pair"] = dedup_commons

                common_rows_overall[_+1] = dedup_common_rows
            else:
                common_rows_overall[_+1] = common_rows_for_row
        return common_rows_overall


def log_to_file(log, tag=None):
    def get_tot_lines_in_file():
        cmd = f"cat -n {LOG_FNAME} | tail -n 1 | cut -f1"
        out = subprocess.check_output(cmd, shell=True)
        out = eval(out)
        return out

    if tag:
        prefix = f"{tag} [{current_thread().getName()}]"
    else:
        prefix = f"[{current_thread().getName()}]"

    t_now = dt.datetime.now().strftime("%Y%m%d %H:%M:%S")
    with open(LOG_FNAME, "a+") as f:
        f.write(f"{t_now}: {prefix}: {log}\n")

    tot_lines = get_tot_lines_in_file()
    # lock.release()
    return tot_lines


if __name__ == '__main__':
    # sql = "select * from AllFindings;"
    # all_findings_df = read_snowflake_sql(sql)
    # all_findings_df.to_excel("../../resources/allfindings.xlsx")
    fname = "/Users/dkanhar/Documents/Groupping_Logic_test_data.csv"
    obj = AlertGroupings(local=True, fname=fname, addnl_prop=["ip_address_1", "ip_address_2", "ip_address_3",
                                                              "Ec2", "S3", "ip_address_4"],
                         prop_type_map={"ip": ["ip_address_1", "ip_address_2", "ip_address_3", "ip_address_4"],
                                        "instance": ["Ec2"], "user_name": [], "s3": ["S3"]},
                         purge_prior_cols=True)
    grouped_alerts = obj.execute()
    grouped_alerts.to_excel("../../resources/output/groped_alerts_vtest1_1.xlsx")
