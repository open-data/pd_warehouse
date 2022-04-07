import argparse
import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile


def run_migrations(source_dir, target_dir):

    for csvfile in os.listdir(source_dir):
        print("Migrating {0} from directory {1} to {2}".format(csvfile, source_dir, target_dir))
        proc = subprocess.Popen([sys.executable, 'migrate_all.py', pathlib.Path.joinpath(source_dir, csvfile),
                                 pathlib.Path.joinpath(target_dir, csvfile)])
        if proc.wait():
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Run the CKAN PD Migrations scripts against all the archived files in a directory')
    parser.add_argument('-d', '--dir', help='Directory to migrate', required=True)
    parser.add_argument('-t', '--target', help='Target directory', required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print('Directory {0) does not exist'.format(args.dir))
        exit(1)
    elif not os.path.isdir(args.target):
        print('Target directory {0} does not exist'.format(args.target))
        exit(1)

    for tar_file in os.listdir(args.dir):
        if not tar_file.endswith('.tar.gz'):
            continue
        print('Migrating {0}'.format(tar_file))
        with tempfile.TemporaryDirectory() as tmp_dir1:
            with tempfile.TemporaryDirectory() as tmp_dir2:
                print('Extracting {0} to {1}'.format(tar_file, tmp_dir1))
                tar = tarfile.open(os.path.join(args.dir, tar_file))
                tar.extractall(tmp_dir1)
                tar.close()
                run_migrations(tmp_dir1, tmp_dir2)

                tar2 = tarfile.open(os.path.join(args.target, tar_file), 'w:gz')
                print('Creating {0}'.format(tar_file))
                for root, dirs, files in os.walk(tmp_dir2):
                    for file in files:
                        tar2.add(os.path.join(root, file))
                tar2.close()

