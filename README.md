# GIC Data Engineer Take-Home Assessment
This code repository is a submission for GIC Data Engineer take-home.

## Setup instructions
1. Clone this repo to local
```
git clone https://github.com/PoeWunLee/gic-dataeng-interview-assessment.git 
```

2. Navigate to the root directory (gic-dataeng-interview-assessment), initialise a venv
```
cd gic-dataeng-interview-assessment
python -m venv .venv
```

3. Install required dependencies and packages from pyproject.toml (pip or poetry)
```
pip install .
poetry install
```

4. Create a .env file and initialise DB connection string env variabled name CNXN_STR.<br/>For the scope of this assessment, sqlite3 is used and CNXN_STR is set to a .db filename (e.g. 'gic.db')<br/>

    Powershell:
    ```
    New-Item -Path .env -ItemType File -Value "CNXN_STR='gic.db'"
    ```
    Bash:
    ```
    echo "CNXN_STR='gic.db'" > .env
    ```

## Assumptions/Scope of take-home submission

1. Incoming Funds Data 
- arrives monthly and consistent as CSV file format
- file structure and naming are consistent across months
- filenames will always have EOM date (with year, month, day details) and fund name
- for a given month, each fund only has one csv file. Files are not resent or duped.

2. Reference data
- all insturments and symbols in incoming data are available in master reference dataset
- master reference dataset is assumed to be clean and complete for pricing

3. Fund coverage
- submission covers the scope for N datasets. logic to onboarding/decomm metadata of new funds beyond the 10 funds in this submission is out of scope.

4. Pricing/Valuation
- utilising most recent available price data, prior to the specified date should there be gaps

5. Execution of the solution
- assumed to be run locally without orchestration/scheduling or production deployments

## Design Decision Notes


## Gaps to productionise from submission
1. Incremental ingestion and handling
2. Orchestration
3. Data Quality management
4. Table/query/view performance considerations (e.g. indexing)