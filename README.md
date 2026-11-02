# WasteWise — Smart Food Waste Analytics

WasteWise is a Python web application for logging food preparation and leftovers, analyzing waste patterns, and generating simple rule-based insights for a campus mess or cafeteria.

## Features
- Record date, meal, food item, prepared quantity, served quantity, and leftovers.
- Persistent storage using SQLite.
- Dashboard KPIs and interactive Plotly charts.
- Edit and delete food logs.
- Import/export CSV files.
- Rule-based observations from recorded data.
- Input validation to prevent impossible quantities.

## Tech stack
Python, Streamlit, Pandas, Plotly, SQLite (`sqlite3`).

## Run locally (Windows)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Data validation rules
- Prepared quantity must be greater than zero.
- Served and leftover quantities cannot be negative.
- Served quantity plus leftovers cannot exceed prepared quantity.
- Quantities are measured in kilograms.

## Project structure
- `app.py`: Streamlit interface and page routing.
- `database.py`: SQLite table and CRUD operations.
- `analytics.py`: summaries and rule-based insights.
- `charts.py`: Plotly visualizations.
- `data/sample_waste.csv`: sample records for testing.

## Notes
The insights are descriptive rules, not machine-learning predictions. Use real, consistently recorded data before making operational decisions.
