# Analytical Report: Statistical Analysis and Dashboard Generation

## Overview
This repository contains a comprehensive framework for statistical analysis, automated reporting, and interactive dashboard generation. It is designed to compare analytical methods, validate results, and visualize statistical findings for research and quality control purposes.

## Key Features
- **Automated Statistical Analysis**: Perform descriptive statistics, ANOVA, post-hoc tests, and assumption checks.
- **Method Comparison**: Compare multiple analytical methods for accuracy, repeatability, and reliability.
- **Interactive Dashboards**: Generate dynamic dashboards to visualize statistical results and comparisons.
- **Automated Reporting**: Save statistical graphs and results in organized directories for reporting.
- **Google API Integration**: Fetch and process data from Google Sheets for analysis.
- **Custom Exception Handling**: Robust error handling and naming utilities for smooth execution.

## Project Structure
```
Analytical_report/
├── Automatic_Evaluation.ipynb          # Notebook for automated evaluation workflows
├── Class_format.ipynb                   # Notebook for class formatting utilities
├── Credentials/                         # Directory for API credentials
│   └── Credentials.json                 # Google API credentials
├── Dashboard_app/                       # Interactive dashboard application
│   ├── app.py                           # Main Dash application
│   ├── callbacks.py                     # Dashboard interactivity callbacks
│   ├── dashboard_tables.py              # Data table utilities
│   ├── dashboards_graphs.py             # Graph generation for dashboards
│   ├── folium_map.html                  # Map visualizations
│   ├── index.py                         # Dashboard entry point
│   ├── layout.py                        # Dashboard layout definitions
│   └── assets/                          # Static assets (CSS, images)
├── Data/                               # Raw and processed data storage
├── Functions/                           # Core analysis and utility functions
│   ├── __init__.py
│   ├── anova.py                         # ANOVA analysis
│   ├── anova_assumptions.py             # ANOVA assumption checks
│   ├── anova_graphs.py                  # ANOVA visualization
│   ├── automatic_dict.py                # Automated dictionary utilities
│   ├── automatization_funtions.py       # Automation utilities
│   ├── dashboard.py                     # Dashboard generation
│   ├── dashboard_graphs.py              # Dashboard graph utilities
│   ├── dashboard_tables.py              # Dashboard table utilities
│   ├── dataset.py                       # Dataset handling
│   ├── descript_stats_graphs.py         # Descriptive stats visualizations
│   ├── descriptive_statistics.py        # Descriptive statistics calculations
│   ├── exception_handeler.py            # Custom exception handling
│   ├── general_setup.py                 # General setup and configuration
│   ├── google_api.py                    # Google API integration
│   └── limits_analysis.py               # Analysis of limits and thresholds
├── Results/                             # Analysis results storage
│   ├── Test_validation/                 # Test validation results
│   └── ...                              # Organized by test, method, and date
└── Test_1/                              # Example test directory
```

## Installation
### Prerequisites
- Python 3.8+
- Poetry (recommended) or pip

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Analytical_report
   ```

2. Install dependencies:
   - Using Poetry:
     ```bash
     poetry install
     ```
   - Using pip:
     ```bash
     pip install -r requirements.txt
     ```

3. Set up credentials:
   - Place your Google API credentials in `Credentials/Credentials.json`.

## Usage
### Running the Dashboard
To launch the interactive dashboard:
```bash
cd Dashboard_app
python index.py
```
The dashboard will be available at `http://127.0.0.1:8050/`.

### Performing Analysis
1. **Prepare Data**: Place your dataset in the `Data/` directory or fetch it via Google Sheets.
2. **Run Analysis**: Use the Jupyter notebooks (`Automatic_Evaluation.ipynb`, `Class_format.ipynb`) or import the functions into your scripts.
3. **View Results**: Results are saved in the `Results/` directory, organized by test, method, and date.

### Example Workflow
```python
from Functions import descriptive_statistics as ds, anova as anova

# Load dataset
data = pd.read_csv('Data/your_dataset.csv')

# Perform descriptive statistics
desc_stats = ds.calculate_descriptive_stats(data)

# Perform ANOVA
anova_results = anova.perform_anova(data, group_col='Method', value_col='Measurement')
```

## Configuration
### General Setup
Modify `Functions/general_setup.py` to adjust:
- Plot styles and sizes
- Folder creation logic
- Default rounding for numerical outputs

### Dashboard Customization
Edit files in `Dashboard_app/` to customize:
- Layout (`layout.py`)
- Callbacks (`callbacks.py`)
- Graphs (`dashboard_graphs.py`)
- Tables (`dashboard_tables.py`)

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feat/your-feature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Contact
For questions or feedback, please contact:
- [Your Name] ([Your Email])
