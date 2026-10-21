# SBI-ADS — Smart Business Intelligence & AI Decision Support System

## About the Project

SBI-ADS is a web-based business intelligence and decision support system designed to help businesses understand their sales data and make informed decisions. It allows users to upload sales datasets and view important business metrics, interactive visualizations, demand forecasts, and practical recommendations through a single dashboard.

The system combines data analysis, machine learning, and inventory intelligence to turn raw sales data into useful business insights. It is developed using Python and FastAPI, with a responsive web interface for presenting the results.

## Key Features

- **Sales Dashboard:** Displays key performance indicators (KPIs), including revenue, units sold, products, customers, and regional performance.
- **Dataset Upload:** Supports CSV and Excel files for sales data analysis.
- **Data Cleaning:** Handles missing values, duplicate records, and inconsistent data formats.
- **Interactive Visualizations:** Presents sales trends, product performance, regional comparisons, price distributions, and correlations.
- **Business Insights:** Identifies important patterns and highlights areas that may require attention.
- **Demand Forecasting:** Uses machine learning to estimate future weekly demand for products.
- **Model Evaluation:** Evaluates forecasting performance using metrics such as MAE, RMSE, R², and MAPE.
- **Anomaly Detection:** Identifies unusual changes in weekly product demand.
- **Decision Support:** Generates recommendations based on sales performance and analytical findings.
- **Inventory Intelligence:** Provides estimated stock recommendations based on forecast demand and a configurable safety buffer.
- **Data Quality Monitoring:** Reports missing values, duplicate records, and overall dataset quality.
- **Report Export:** Supports downloading an analysis report in JSON format.
- **User Interface:** Includes a responsive dashboard with dark and light themes.

## Technologies Used

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Data Analysis | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Data Visualization | Chart.js, Matplotlib |
| Database | SQLite (default), MySQL (optional) |
| API Server | Uvicorn |
| Dataset Formats | CSV, XLSX |

## How the System Works

1. The user uploads a sales dataset in CSV or Excel format.
2. The system checks the dataset, identifies relevant columns, and prepares the data for analysis.
3. It calculates key business metrics and generates visualizations and analytical insights.
4. Machine learning models estimate future product demand and evaluate forecasting performance.
5. The system identifies unusual demand patterns and generates business and inventory recommendations.
6. The results are presented through the dashboard for easier interpretation and decision-making.

## Project Structure

```text
SBI-ADS/
├── analytics/       # Data analysis and insight generation
├── backend/         # FastAPI routes and API logic
├── core/            # Application configuration
├── database/        # Database connection and schema
├── data/            # Sample data and runtime files
├── frontend/        # Dashboard interface and styling
├── ml/              # Forecasting and machine learning
├── main.py          # Application entry point
├── requirements.txt # Python dependencies
├── run.bat          # Windows startup script
├── run.sh           # Linux/macOS startup script
├── test_smoke.py    # Basic application/API test
└── README.md        # Project documentation
```

## Installation and Setup

### Prerequisites

Make sure the following are installed on your system:

- Python 3.10 or later
- pip (Python package installer)
- Git, if you are cloning the project from GitHub

### Step 1: Download the Project

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SBI-ADS
```

Alternatively, download the project as a ZIP file from GitHub and extract it.

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the Application

On Windows, run:

```powershell
.\run.bat
```

Alternatively, start the application manually:

```bash
uvicorn main:app --reload
```

### Step 5: Open the Dashboard

Once the server starts successfully, open the following URLs in your browser:

- **Dashboard:** http://127.0.0.1:8000/dashboard
- **API Documentation:** http://127.0.0.1:8000/docs
- **System Health:** http://127.0.0.1:8000/api/system/health

Keep the terminal running while using the application. Press `Ctrl + C` in the terminal to stop the server.

## Using the Application

1. Open the dashboard in your browser.
2. Upload a sales dataset in CSV or Excel format.
3. Select **Analyze Dataset** to begin processing.
4. Review the generated KPIs, charts, and business insights.
5. Explore demand forecasts, model evaluation results, anomaly alerts, and inventory recommendations.
6. Export the analysis report when required.

A sample dataset is provided in `data/sample_sales.csv` for testing the application.

## Database Configuration

SBI-ADS uses SQLite by default, so a separate database server is not required for basic use. The database schema is initialized automatically when the application starts.

The default database file is:

```text
data/sbi_ads.db
```

MySQL is also supported for configurations that require a separate database server. Refer to `.env.example` for the available configuration options.

## Machine Learning and Analytics

The forecasting module prepares weekly sales data and uses historical demand patterns, lag values, rolling averages, and calendar features to estimate future demand. It compares supported models and evaluates their performance using a chronological train-test split.

The anomaly detection module uses a robust statistical score to identify unusual demand patterns. These results, along with sales analytics and inventory calculations, help generate recommendations for business planning.

Forecasts and recommendations are estimates based on the available data. Their reliability depends on data quality, historical coverage, and changing business conditions.

## Testing

The project includes a basic application test script. To run it, start the application as required by the test setup, then execute:

```bash
python test_smoke.py
```

## Future Enhancements

Potential improvements include user authentication and role-based access, automated data updates, additional forecasting models, enhanced report formats, and deployment to a cloud platform.

## Project Purpose

The purpose of SBI-ADS is to demonstrate how data analytics and machine learning can be applied to business sales data to improve reporting, demand planning, and inventory-related decision-making.

---

**SBI-ADS — Turning Sales Data into Actionable Business Insights.**
