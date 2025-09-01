# pyFMgr: Personal Finance Manager

pyFMgr is a Python-based personal finance manager designed to help you track, analyze, and manage your financial transactions. It supports importing bank statements, categorizing transactions, and provides a web dashboard for easy visualization and management.

## Features
- Import bank and Chase statements (CSV)
- Store transactions in a SQLite database
- Categorize and group transactions
- Web dashboard for viewing, adding, and editing transactions
- Data visualization and summary reports

## Project Structure
```
├── main.py                # Entry point for CLI operations
├── webapp/                # Flask web application
│   ├── app.py             # Main web app logic
│   ├── static/            # JS, CSS files
│   └── templates/         # HTML templates
├── database/              # Database logic
│   └── db.py              # DB connection and queries
├── importers/             # Import logic for bank/Chase statements
│   ├── bank.py
│   ├── chase.py
│   └── base.py
├── data/                  # Example CSV data files
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── income_giving.ipynb    # Jupyter notebook for analysis
├── grouped_output.csv     # Example output
├── init_db.py             # Script to initialize the database
├── finance.db             # SQLite database file
```

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```pwsh
   git clone <repo-url>
   cd pyFMgr
   ```
2. Install dependencies:
   ```pwsh
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```pwsh
   python init_db.py
   ```

### Usage
#### Import Transactions
Run the main script to import transactions:
```pwsh
python main.py
```

#### Start the Web Dashboard
```pwsh
python webapp/app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

#### Jupyter Notebook
Explore `income_giving.ipynb` for custom analysis and reporting.

## Testing
Run tests with:
```pwsh
python -m unittest discover webapp/tests
```

## Contributing
This finance manager is intended for personal use and was created to help the author manage finances according to their own needs. Contributions from others are not expected, as the project serves primarily as a personal tool.



