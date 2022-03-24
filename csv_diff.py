import json
import requests
import sys
import csv
import os
import codecs
from sys import stderr, stdout, argv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_fieldnames(fields):
    fieldnames = ",".join([f['id'] for f in fields])+",record_created,record_modified,user_modified,owner_org,log_date,log_activity"
    return fieldnames


def csv_to_dict(csv_file, primary_keys):
    csv_dict = {}
    with open(csv_file, encoding='utf-8-sig', errors="ignore") as f:
        hashcsv = csv.DictReader(f, dialect='excel')
        for row_num, row in enumerate(hashcsv):
            primary_fields = [str(row[t]) for t in primary_keys]
            uid = '-'.join(primary_fields)
            csv_dict[uid] = row
    return csv_dict


def compare_dicts(prev, curr):
    removed_keys = []
    added_keys = []
    modified_keys = []
    for key in prev:
        if not key in curr:
            removed_keys.append(key)
    for key in curr:
        if not key in prev:
            added_keys.append(key)
        else:
            for field in curr[key]:
                if curr[key][field] != prev[key][field]:
                    modified_keys.append(key)
                    break
    return removed_keys, added_keys, modified_keys


def add_metadata_fields(prev, curr, rkeys, akeys, mkeys, date):
    results = {}
    result_keys=[]
    for key in akeys:
        curr[key]["log_date"] = date
        curr[key]["log_activity"] = 'C'
        results[key] = curr[key]
        result_keys.append(key)

    for key in mkeys:
        curr[key]["log_date"] = date
        curr[key]["log_activity"] = 'M'
        results[key] = curr[key]
        result_keys.append(key)

    for key in rkeys:
        prev[key]["log_date"] = date
        prev[key]["log_activity"] = 'D'
        results[key] = prev[key]
        result_keys.append(key)

    return results, result_keys


prev_csv, current_csv, endpoint, datestamp, outfile = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]

field_info = requests.get(endpoint, timeout=100, verify=False).json()


# Grab the primary key fields from the datatype reference endpoint
current_csv_resource = current_csv.split('_')[-1].replace('.csv','')
pk_fields = [f['primary_key'][0] for f in field_info['resources'] if current_csv_resource == f['resource_name']]
fields = [f['fields'] for f in field_info['resources'] if current_csv_resource == f['resource_name']]
fieldnames = get_fieldnames(fields[0]).split(",")

pk_fields.append('owner_org')

old_csv_dict = csv_to_dict(prev_csv, pk_fields)
new_csv_dict = csv_to_dict(current_csv, pk_fields)

removed_keys, added_keys, modified_keys = compare_dicts(old_csv_dict, new_csv_dict)

result_rows, result_keys = add_metadata_fields(old_csv_dict,new_csv_dict,removed_keys,added_keys,modified_keys,datestamp)

if result_rows:
    print("writing to {0}".format(outfile))
    with open(outfile, 'a', encoding='utf-8-sig') as f:
        warehouse = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', restval='', extrasaction='ignore', lineterminator='\n')
        if not os.path.isfile(outfile):
            warehouse.writeheader()
        for row in result_keys:
            output_row = {}
            for key in fieldnames:
                output_row[key] = result_rows[row][key]
            warehouse.writerow(output_row)
        f.close()

else:
    print("No changes detected between files")