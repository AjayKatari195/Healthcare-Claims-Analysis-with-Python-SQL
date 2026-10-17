# Simple Healthcare Claims Analysis (Python + SQL)

One script that creates a small synthetic claims dataset, cleans it with pandas,
analyses denials, runs a SQL query with SQLite, and saves a chart.
No real patient data is used.

## Run
    pip install pandas numpy matplotlib
    python claims_analysis.py

## Functions
- `create_data()` - builds a messy dataset (duplicates, missing values, inconsistent payer names)
- `clean_data()` - removes duplicates, standardizes payer names, drops missing amounts
- `denial_rate_by_payer()` - denial rate per payer using pandas
- `top_denial_reasons()` - SQL query (GROUP BY) on the cleaned data
