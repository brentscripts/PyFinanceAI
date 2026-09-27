# pyFinanceAI

pyFinanceAI is a Python-based personal finance manager I built specifically for my own financial needs. It helps me track, analyze, and manage my transactions, supporting single-entry or bulk imports from my bank and credit card statements. I can categorize and edit transactions and view everything through a web dashboard for easy visualization.

## Features
- Import bank and credit card statements (CSV)
- Store transactions in a local SQLite database
- Categorize and group transactions for better insights
- Web dashboard for viewing, adding, and editing transactions
- Data visualization and summary reports
- Fully tailored for my personal finance workflow

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
├── pyproject.toml         # Python dependencies (core + dev extras)
├── income_giving.ipynb    # Jupyter notebook for analysis
├── grouped_output.csv     # Example output
├── init_db.py             # Script to initialize the database
├── finance.db             # SQLite database file
```


## Getting Started

### Prerequisites
- Python 3.8+ and pip (for local development)
- Docker and Docker Compose (for containerized deployment)

### Local Installation
1. Clone the repository:
   ```pwsh
   git clone <repo-url>
   cd pyFMgr
   ```
2. Create and activate a virtual environment:
   ```pwsh
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```pwsh
   pip install -e ".[dev]"
   ```
   This installs the app plus dev tools (pytest, etc.). For a production-only install without dev tools, drop the extras:
   ```pwsh
   pip install -e .
   ```
4. Set up environment variables:
   ```pwsh
   cp .env.example .env
   ```
   Then edit `.env` and set `SECRET_KEY` to any random string. `DATABASE` can stay as `finance.db` for local use. The app will not start without these — `webapp/app.py` reads them directly from the environment.
5. Initialize the database:
   ```pwsh
   python init_db.py
   ```

### Docker Deployment
1. Build and start the app with Docker Compose:
   ```pwsh
   docker-compose up -d --build
   ```
   This will:
   - Build the Docker image (code is baked in, not mounted from your project folder)
   - Start the app on [http://localhost:5000](http://localhost:5000)
   - Persist the database in a named volume (`finance_data`, mounted at `/app/data`)
   - Load environment variables from your `.env` file

2. Initialize the database inside the container (only needed the first time, since the volume starts empty):
   ```pwsh
   docker-compose exec pyfmgr python init_db.py
   ```

3. To stop the app:
   ```pwsh
   docker-compose down
   ```

4. To also install dev/test dependencies in the image, edit `docker-compose.yml` and set:
   ```yaml
   args:
     DEV_INSTALL: "true"
   ```

### Usage
#### Import Transactions
Run the main script to import transactions:
```pwsh
python main.py
```

#### Start the Web Dashboard (Locally)
```pwsh
python webapp/app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

#### Jupyter Notebook
Explore `income_giving.ipynb` for custom analysis and reporting.

## Testing
Run tests with pytest (requires the `dev` extras — `pip install -e ".[dev]"`):
```pwsh
pytest
```
The unittest-style runner still works too:
```pwsh
python -m unittest discover webapp/tests
```

## Contributing
This finance manager is intended for personal use and was created to help the author manage finances according to their own needs. Contributions from others are not expected, as the project serves primarily as a personal tool.



