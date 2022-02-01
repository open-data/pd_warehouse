PD Warehouse Scripts
====================

This script compares versions of the Open Canada proactive disclosure CSV files and
notes any changes. The script then creates or appends to a CSV file with a record
for each change. This provides easily accessible information about the changes to
the proactive disclosure data over time.

Installation
------------

The PD warehouse script is a Python 3 script. For full functionality it requires
some data migration scripts from the Canada CKAN Extension project available on
[GitHub](https://github.com/open-data/ckanext-canada/tree/master/bin/migrate) as
well as the [YAML schema definition files](https://github.com/open-data/ckanext-canada/tree/master/ckanext/canada/tables) 
from the same project. The script will automatically retrieve the schema files
from GitHub, but it is necessary to manually download the migration scripts for now.

To install, clone or download this project from GitHub, create a Python 3 virtual
environment, and install the required libraries.

    $ git clone https://github.com/open-data/pd-warehouse.git
    $ cd pd-warehouse
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

Then copy the migration scripts from the Canada CKAN Extension project to the "migrate"
directory in the pd_warehouse project.

    $ cp -R /path/to/ckanext-canada/bin/migrate ./migrate

The script will need access to the archived proactive disclosure CSV files 
for Open Canada. The script expects the archived files to be in a directory that
contains the tarred and gzipped PD CSV files for each day in the format pd-yyyymmdd.tar.gz

Example:

    /2021/
        /pd-20220101.tar.gz
        /pd-20220102.tar.gz
        /pd-20220103.tar.gz
    
The gzip file contents will be CSV files named using the following convention <CKAN PD type ID>.csv.

Example:

    /pd-20220101.tar.gz
        /ati.csv
        /ati-nil.csv
        /briefingt.csv
        /qpnotes.csv
        /qpnotes-nil.csv
        ...

Lastly, the script will write out the change report CSV files to the `warehouse_reports` directory.

Example:

    /warehouse_reports/
        /ati_warehouse.csv
        /ati-nil_warehouse.csv
        /briefingt_warehouse.csv
        ...

Running the script
-------------------

To run the script, activate the virtual environment and run the script with the
appropriate arguments.

- <pd_base_dir> is the path to the directory containing the PD CSV files.
- --start-date (_optional_) is the date to start the comparison from. 
- --end-date (_optional_) is the date to end the comparison at.
- --all (_optional_) will compare all dates in the directory.

If no dates are specified and all is not indicated, the script will compare the 
last two files in the pd_base_dir directory.

Examples
--------

Examples of using the warehouse script. Be sure to activate the virtual environment
before running the script.

1. Show help


    $ source venv/bin/activate
    $ python pd_warehouse.py --help

2. Compare the latest two files in the directory



    $ python pd_warehouse.py /path/to/pd_base_dir 


3. Compare all files in the directory


    $ python pd_warehouse.py /path/to/pd_base_dir --all


3. Compare files from 2022-01-01 to 2022-01-05


    $ python pd_warehouse.py /path/to/pd_base_dir --start-date 2022-01-01 --end-date 2022-01-05


4. Compare files from 2022-01-03 to the latest file in the directory


    $ python pd_warehouse.py /path/to/pd_base_dir --start-date 2022-01-03


5. Compare files from the earliest date up to 2022-01-05


    $ python pd_warehouse.py /path/to/pd_base_dir --end-date 2022-01-05

