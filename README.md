# NBA_Prediction_V3

## Software requirements

- Python 3.11: https://www.python.org/downloads/
- Postgresql v15: https://www.postgresql.org/download/

## Getting started

1. Install the software requirements listed above.

2. Run the following commands to setup your virtual environment:

```
cd ./backend
python3 -m venv .   # create virtual environment for installing dependencies in root directory

cd ..
./backend/Scripts/activate  # run this to activate your virtual environment if it isn't activated already
```

3. Run the following command to set up the repo:

```
python3 ./backend/src/setup_backend.py -a
```

4. Make sure the database and tables were created correctly. Open your PSQL terminal and sign in. Run the following in the terminal:

```
\c nba_db                       # Run if you did not select the nba_db database upon signing in
SHOW SEARCH_PATH;               # Make sure the search path is set to nba_db_schema
\d                              # Check the tables gamelogs and teaminfo were created under the correct schema
SELECT * FROM teaminfo;         # Check if there is information about the teams
quit                            # Leave the psql terminal
```

5. Get data from the previous NBA seasons (populates gamelogs table)
```
python3 ./backend/src/sql_db/update_sql_db.py
```

## Reactivating the environment

```
./Scripts/activate
```

## Requirements management

To add/remove dependencies please use:

```
pip install/uninstall [package_name]
pip freeze > ./backend/requirements.txt
```

For installing packages, use `pip install -r ./backend/requirements.txt` OR `python3 ./backend/src/setup_backend.py -r`

## Repository setup script

The usage of the script is the following:

```
usage: setup_backend.py [-h] [-a] [-p] [-r] [-s]

options:
  -h, --help          show this help message and exit
  -a, --all           If used, it will perform all the following actions.
  -p, --private_data  If used, it will set up private_data.txt with your Postgresql password ecrypted.
  -r, --requirements  If used, it will install requirements.txt for you.
  -s, --sql_init      If used, it will set up the database on Postgresql.
```
