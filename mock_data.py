import argparse
import csv
import datetime
import names
import os
import pathlib
import random


parser = argparse.ArgumentParser(description="Create mock data for PD Warehouse based on some existing data.")
parser.add_argument("--report_dir", type=pathlib.Path, required=True,
                    help="The directory containing archived warehouse reports CSV files.")
parser.add_argument("--mockdata_dir", type=pathlib.Path, required=True,
                    help="The directory to write out the warehouse reports CSV files.")
args = parser.parse_args()
reports = sorted(os.listdir(args.report_dir))

mock_users = []
for i in range(40):
    mock_users.append(names.get_full_name().replace(' ', '_').lower())

print("Reading reports from {0} and writing to {1}".format(args.report_dir, args.mockdata_dir))

for report in reports:
    report_file = pathlib.Path.joinpath(args.report_dir, report)
    mock_file = pathlib.Path.joinpath(args.mockdata_dir, report)
    if not os.path.isfile(report_file) or not report_file.suffix == '.csv':
        continue
    with open(pathlib.Path.joinpath(args.report_dir, report), encoding='utf-8-sig', errors="ignore") as f:
        source_csv = csv.DictReader(f, dialect='excel')
        field_names = source_csv.fieldnames.copy()
        field_names.insert(len(field_names) - 1, 'record_created')
        field_names.insert(len(field_names) - 1, 'record_updated')
        field_names.insert(len(field_names) - 1, 'user_modified')

        print(f"Processing {report}..")
        with open(mock_file, 'w', encoding='utf-8-sig', errors="ignore") as f1:
            warehouse = csv.DictWriter(f1, fieldnames=field_names, delimiter=',', restval='', extrasaction='ignore',
                                       lineterminator='\n', quotechar='"', quoting=csv.QUOTE_ALL)
            warehouse.writeheader()
            count = 0
            for row_num, row in enumerate(source_csv):
                log_date = datetime.datetime.strptime(row['log_date'], '%Y-%m-%d')
                random_created = log_date - datetime.timedelta(hours=random.randint(1, 12))
                if str(row['log_activity']).upper() in ['C', 'D', 'M']:
                    row['record_created'] = random_created.isoformat()
                    row['record_updated'] = random_created.isoformat()
                    row['user_modified'] = random.choice(mock_users)
                    warehouse.writerow(row)
                    count += 1
            f1.close()
            print('{} records written to {}'.format(count, report))
        f.close()
