# CryptoSentiment Analytics Dashboard

A real-time cryptocurrency sentiment analysis platform that explores the relationship between social media buzz and price volatility.

**Big Data Analytics Final Project**

Emre Akyol · Harmanpreet Chauhan · Mohamed Nasr

---

## Project Overview

This project analyzes how social media sentiment affects cryptocurrency price volatility. We collect real-time data from multiple APIs, store it in MongoDB, process it with Apache Spark, and visualize insights through an interactive web dashboard.

The system tracks six major cryptocurrencies (Bitcoin, Ethereum, Ripple, Solana, Dogecoin, Cardano) and correlates their price movements with the Fear & Greed Index and news sentiment from CryptoPanic.

---

## Architecture

The platform follows a 4-layer architecture:

**Layer 1 - Data Sources**
- CoinGecko API for price, volume, and market cap data
- Alternative.me for the Fear & Greed Index
- CryptoPanic for news headlines with vote-based sentiment

**Layer 2 - Storage**
- MongoDB NoSQL database with optimized indexes
- JSON file caching for offline operation

**Layer 3 - Analytics**
- Apache Spark for distributed MapReduce operations
- scikit-learn for machine learning predictions

**Layer 4 - Visualization**
- Web dashboard with ECharts visualizations
- Real-time updates every 2 minutes

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB 6.0+ (optional, for database features)
- Docker (optional, for containerized deployment)

### Installation

Clone the repository and install dependencies:

```
pip install -r requirements.txt
```

### Running the Dashboard

Start the complete system with:

```
python start_dashboard.py
```

This will fetch data, run analysis, and open the dashboard at http://localhost:8000

For a minimal setup without MongoDB:

```
python start_dashboard.py --no-mongodb --no-spark
```

### Docker Deployment

Start MongoDB and the dashboard together:

```
docker compose up -d
```

Access the dashboard at http://localhost:8000

View logs with:

```
docker logs -f crypto-dashboard
```

---

## Project Structure

```
CryptoSentiment/
│
├── Python Scripts
│   ├── fetch_crypto_data.py        CoinGecko API integration
│   ├── fetch_real_sentiment.py     Sentiment data collection
│   ├── mongodb_storage.py          Database operations
│   ├── real_data_ml_analysis.py    Machine learning models
│   ├── spark_mapreduce_analysis.py Distributed processing
│   └── start_dashboard.py          Main orchestrator
│
├── Web Dashboard
│   ├── index.html                  Main dashboard
│   ├── sentiment.html              Sentiment analysis page
│   ├── correlation.html            Correlation visualizations
│   ├── predictions.html            ML prediction interface
│   └── main.js                     Frontend logic
│
├── Jupyter Notebooks
│   ├── 01_Data_Collection.ipynb    Data fetching demonstrations
│   ├── 02_Data_Storage.ipynb       MongoDB operations
│   ├── 03_ML_Analysis.ipynb        Model training and evaluation
│   └── 04_Spark_MapReduce.ipynb    Distributed processing
│
├── Configuration
│   ├── requirements.txt            Python dependencies
│   ├── docker-compose.yml          Container orchestration
│   └── Dockerfile                  Container image definition
│
└── resources/data/                 Generated JSON data files
```

---

## Data Sources

### CoinGecko API

Provides real-time cryptocurrency market data:
- Current prices in USD
- 24-hour and 7-day price changes
- Market capitalization and trading volume
- 7-day hourly sparkline data (168 data points per coin)

Rate limit: 10-30 calls per minute (public API)

### Alternative.me Fear & Greed Index

A market sentiment indicator on a 0-100 scale:
- 0-24: Extreme Fear
- 25-49: Fear
- 50-54: Neutral
- 55-74: Greed
- 75-100: Extreme Greed

The index aggregates volatility, market momentum, social media trends, and Bitcoin dominance.

### CryptoPanic

Cryptocurrency news aggregator with community voting:
- Real-time news headlines from multiple sources
- Vote-based sentiment (positive/negative votes)
- Currency tags for relevant cryptocurrencies

---

## Machine Learning Models

Three regression models predict volatility and price changes:

**Random Forest Regressor**
- 100 decision trees with max depth of 3
- Best overall performance for volatility prediction
- Provides feature importance rankings

**Gradient Boosting Regressor**
- Sequential ensemble method
- 100 estimators with learning rate optimization
- Strong performance on price change prediction

**Linear Regression**
- Baseline model for comparison
- Interpretable coefficients
- Fastest training time

### Features Used

- Fear & Greed Index (normalized 0-1)
- Trading volume (normalized)
- Price (normalized)
- Social sentiment score

### Evaluation Metrics

- R² Score: Coefficient of determination
- RMSE: Root mean squared error
- MAE: Mean absolute error
- Cross-validation: 3-fold validation for robustness

---

## Spark MapReduce Operations

Five distributed processing operations demonstrate big data techniques:

1. **Sentiment Aggregation**: Map each cryptocurrency to its sentiment score
2. **Market Metrics**: Reduce to calculate total market cap and volume
3. **Volatility Classification**: Group cryptocurrencies by Low/Medium/High volatility
4. **Price Performance**: Classify into Gain/Loss categories
5. **Engagement Scoring**: Calculate sentiment-weighted volume scores

The system falls back to Python implementations when Spark is unavailable.

---

## Dashboard Pages

### Main Dashboard (index.html)
- Market overview with total cap, volume, and BTC dominance
- Fear & Greed gauge visualization
- Live price charts with multiple timeframes
- Architecture diagram and team information

### Sentiment Analysis (sentiment.html)
- 30-day Fear & Greed timeline
- Live news headlines from CryptoPanic
- Vote-based sentiment distribution
- Trending coins and topics

### Correlation Analysis (correlation.html)
- Scatter plots with regression lines
- Multi-variable correlation heatmap
- Statistical metrics (R², p-value)
- Feature importance visualization

### ML Predictions (predictions.html)
- Price predictions with confidence intervals
- Model comparison charts
- Backtesting visualizations
- All-crypto prediction summary

---

## Configuration Options

### Command Line Arguments

```
python start_dashboard.py [options]

Options:
  --no-mongodb    Skip MongoDB storage
  --no-spark      Skip Spark analysis
  --no-browser    Don't open browser automatically
  --port PORT     HTTP server port (default: 8000)
```

### Environment Variables

- `MONGODB_URI`: MongoDB connection string (default: mongodb://localhost:27017/)

---

## Notebooks

The four Jupyter notebooks provide detailed walkthroughs:

**01_Data_Collection.ipynb**
- API integration demonstrations
- Data quality validation
- Initial visualizations

**02_Data_Storage.ipynb**
- MongoDB collection setup
- Index creation and optimization
- Aggregation pipeline examples

**03_ML_Analysis.ipynb**
- Feature engineering
- Model training and evaluation
- Correlation analysis

**04_Spark_MapReduce.ipynb**
- RDD transformations
- MapReduce operations
- Distributed aggregations

---

## Dependencies

Core libraries:
- pandas, numpy, scipy for data processing
- requests for API calls
- pymongo for MongoDB operations
- pyspark for distributed processing
- scikit-learn for machine learning
- matplotlib, seaborn for static visualizations

Frontend:
- Tailwind CSS for styling
- ECharts for interactive charts
- Inter font family

---

## Troubleshooting

**MongoDB connection refused**
- Ensure MongoDB is running: `docker ps`
- Check the connection URI matches your setup

**CoinGecko rate limiting**
- The script includes 4-second delays between API calls
- Wait a few minutes if you hit rate limits

**Spark initialization errors**
- Ensure Java 21 is installed
- Set JAVA_HOME environment variable
- The system falls back to Python if Spark fails

**Dashboard not loading data**
- Check that JSON files exist in resources/data/
- Run the data collection step manually
- Check browser console for errors

---

## Acknowledgments

- CoinGecko for the cryptocurrency market data API
- Alternative.me for the Fear & Greed Index
- CryptoPanic for news aggregation
- Apache Spark for distributed processing capabilities
- MongoDB for flexible document storage
