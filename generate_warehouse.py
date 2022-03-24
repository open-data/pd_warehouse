#!/usr/bin/env python3
"""
Creates Warehouse for all PD-Types found in archived backups.

Arguments:
pd_backup_dir - directory of archived backups
operation - '-d' to compare last 2 backups (default), '-a' to compare all backups.
"""
import tarfile
import sys
import os
import pathlib
import subprocess
import shutil
import tempfile
from datetime import datetime
import argparse


parser = argparse.ArgumentParser(description="Run warehouse script. By default, it runs on the last 2 backups.")
parser.add_argument("pd_backup_dir", type=pathlib.Path,
                    help="The directory containing archived PD backups. It should contain tarred and gzipped files"
                         "in the format pd-YYYYMMDD.tar.gz")
parser.add_argument("--start_date", type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                    action='store', help="The date to start the warehouse processing from. Format: YYYY-MM-DD")
parser.add_argument("--end_date", type=lambda s: datetime.strptime(s, '%Y-%m-%d'), action='store',
                    help="The date to stop on. If not specified, the script will run until the end of the directory. "
                         "If no start date is specified, the script will run from the beginning of the directory. "
                         "Format: YYYY-MM-DD")
parser.add_argument("-a", "--all", action='store_true', help="Compare all backups.")
args = parser.parse_args()

tar_array = sorted(os.listdir(args.pd_backup_dir))

if not args.all:
    if args.start_date and not args.end_date:
        tar_array = [tar for tar in tar_array if args.start_date <= datetime.strptime(tar[3:11], '%Y%m%d')]
    elif args.start_date and args.end_date:
        tar_array = [tar for tar in tar_array if
                     args.start_date <= datetime.strptime(tar[3:11], '%Y%m%d') <= args.end_date]
    elif args.end_date and not args.start_date:
        tar_array = [tar for tar in tar_array if args.end_date >= datetime.strptime(tar[3:11], '%Y%m%d')]
    else:
        tar_array = tar_array[-2:]

if len(tar_array) < 2:
    print("Not enough backups to compare.")
    sys.exit(1)

prev = ''
curr = ''


def get_base(tfile):
    base = os.path.basename(tfile)
    pd_name = os.path.splitext(os.path.splitext(base)[0])[0]
    return pd_name


def extract(tfile, dest):
    fpath = os.path.join(os.path.curdir,  dest)
    tar = tarfile.open(os.path.join(args.pd_backup_dir, tfile))
    tar.extractall(path=fpath)
    tar.close()
    return fpath


def run_migrations(fpath, temp_dir):

    for csvfile in os.listdir(fpath):
        print("Migrating {0} from directory {1}".format(csvfile, fpath))
        proc = subprocess.Popen([sys.executable, 'migrate_all.py', fpath+'/'+csvfile, temp_dir+'/'+fpath+'m_'+csvfile])
        if proc.wait():
            sys.exit(1)


def csv_diff(prev_csv, curr_csv, endpoint, outfile):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")

    print("Getting difference between {0} and {1}".format(prev_csv, curr_csv))
    proc = subprocess.Popen([sys.executable, 'csv_diff.py', temp_dir+'/'+prev_csv, temp_dir+'/'+curr_csv, endpoint,
                             dt_string, outfile])
    if proc.wait():
        sys.exit(1)


if not os.path.exists('warehouse_reports'):
    os.mkdir('warehouse_reports')

while tar_array:
    with tempfile.TemporaryDirectory() as temp_dir:
        if not tar_array:
            break
        if not prev:
            prev = tar_array.pop(0)
            curr = tar_array.pop(0)
        else:
            prev = curr
            curr = tar_array.pop(0)

        prev_base = get_base(prev)
        curr_base = get_base(curr)

        # Extract zipped backups
        prev_path = extract(prev, prev_base)
        curr_path = extract(curr, curr_base)

        # Migrate all CSVs
        run_migrations(prev_path, temp_dir)
        run_migrations(curr_path, temp_dir)

        # Delete extracted directories
        shutil.rmtree(prev_path)
        shutil.rmtree(curr_path)

        # Match Migrated CSVs
        csv_array = sorted(os.listdir(temp_dir))
        prev_array = [a for a in csv_array if prev_base in a]
        curr_array = [a for a in csv_array if curr_base in a]

        for curr_csv in curr_array:
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            print(dt_string)
            pdfile = curr_csv.split('_')[1]
            pdtype = pdfile.split('.')[0]
            schema = pdtype
            if 'nil' in pdtype or 'std' in pdtype:
                schema = schema.split('-')[0]
            prev_csv_matches = [string for string in prev_array if pdfile in string]
            if prev_csv_matches:
                csv_diff(prev_csv_matches[0], curr_csv,
                    'https://open.canada.ca/data/en/recombinant-schema/{0}.json'.format(schema),
                    'warehouse_reports/{0}_warehouse.csv'.format(pdtype))


