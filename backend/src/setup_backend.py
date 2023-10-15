import os
import json
import subprocess
import argparse
from getpass import getpass

from src.globals import (SQL_LOCAL_INFO, KEY_PATH, PRIVATE_DATA, SQL_LOCAL_PASSWORD, LOCAL_SQL_DATABASE,
                             LOCAL_SQL_USERNAME, LOCAL_SQL_PORT, LOCAL_SQL_HOST, SCHEMA_PATH, TEAM_INFO_PATH)
from src.global_utils import get_from_private_data
from src.utils.encryption_keys import generate_key, load_key
from src.sql_db.init_sql_db import init_sql_db

def setup_backend(run_a: bool, run_p: bool, run_r: bool, run_s: bool):
    if run_a or run_p:
        generate_private_data()
    if run_a or run_r:
        install_requirements()
    if run_a or run_s:
        sql_db_setup()

    print('SUCCESS: Setup complete!')

def generate_private_data():
    print('LOG: Generating key...')
    generate_key()
    print('SUCCESS: Key created at ' + KEY_PATH + '...')

    fernet = load_key()
    print('SUCCESS: Loaded key from ' + KEY_PATH + '...')

    try:
        os.remove('private_data.ini')
        print('SUCCESS: Removed private_data.ini from your local directory...')
    except OSError:
        pass

    private_data_dict = {SQL_LOCAL_INFO: {}}

    private_data_dict[SQL_LOCAL_INFO][SQL_LOCAL_PASSWORD] = getpass('Enter your Postgresql password: ')
    private_data_str = str(json.dumps(private_data_dict))
    
    enc_priv_data = fernet.encrypt(private_data_str.encode())
    with open(PRIVATE_DATA, 'wb') as file:
        file.write(enc_priv_data)
        print('SUCCESS: Wrote your data to ' + PRIVATE_DATA + '...')
    
    print()

def install_requirements():
    print('LOG: Installing requirements...')
    try:
        subprocess.check_call(['pip', 'install', '-r', './backend/requirements.txt'])
        print("SUCCESS: Requirements installed successfully...")
    except subprocess.CalledProcessError:
        print("ERROR: An error occurred while installing requirements...")
    except FileNotFoundError:
        print("ERROR: pip command not found. Make sure you're in the virtual environment...")
    
    print()

def sql_db_setup():
    print('LOG: Setting up local SQL database...')
    
    sql_password = get_from_private_data(private_data_path=PRIVATE_DATA, section_key=SQL_LOCAL_INFO, value_key=SQL_LOCAL_PASSWORD)
    if init_sql_db(sql_user=LOCAL_SQL_USERNAME, sql_password=sql_password, sql_host=LOCAL_SQL_HOST, sql_port=LOCAL_SQL_PORT,
                   sql_database=LOCAL_SQL_DATABASE, schema_path=SCHEMA_PATH, team_info_path=TEAM_INFO_PATH):
        print('SUCCESS: Local SQL has been set up...')
    else:
        print('ERROR: Local SQL set up has failed...')

    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true', help='If used, it will perform all the following actions.')
    parser.add_argument('-p', '--private_data', action='store_true', help='If used, it will set up ' + PRIVATE_DATA + ' with you Postgresql password ecrypted.')
    parser.add_argument('-r', '--requirements', action='store_true', help='If used, it will install requirements.txt for you.')
    parser.add_argument('-s', '--sql_init', action='store_true', help='If used, it will set up the database on Postgresql.')

    args = parser.parse_args()

    setup_backend(run_a=args.all, run_p=args.private_data, run_r=args.requirements, run_s=args.sql_init)

if __name__ == "__main__":
    main()
