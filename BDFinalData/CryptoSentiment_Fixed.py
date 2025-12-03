#!/usr/bin/env python3
"""
Fixed Crypto Sentiment Analysis with Machine Learning
This script fixes the cross_val_score import error and provides proper ML analysis
"""

import pandas as pd
import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Load the real cryptocurrency and sentiment data"""
    
    # Load real crypto data
    with open('./resources/data/crypto-prices.json', 'r') as f:
        crypto_data = json.load(f)
    
    # Create a dataset combining crypto metrics with sentiment
    data = []
    for crypto in crypto_data['cryptocurrencies']:
        data.append({
            'symbol': crypto['symbol'],
            'name': crypto['name'],
            'price': crypto['price'],
            'change_24h': crypto['change24h'],
            'volume_24h': crypto['volume24h'],
            'market_cap': crypto['marketCap'],
            'volatility': crypto['volatility'],
            'sentiment': crypto['socialSentiment'],
            'buzz_volume': crypto['buzzVolume']
        })
    
    return pd.DataFrame(data)

def perform_ml_analysis(df):
    """Perform machine learning analysis on the crypto sentiment data"""
    
    print("=== MACHINE LEARNING MODELS ===")
    print(f"Dataset shape: {df.shape}")
    print(f"Features: {list(df.columns)}")
    
    # Prepare features and target
    # We'll predict volatility based on sentiment and buzz volume
    features = ['sentiment', 'buzz_volume', 'change_24h', 'volume_24h']
    X = df[features].fillna(0)
    y = df['volatility'].fillna(0)
    
    print(f"Features for ML: {features}")
    print(f"Target variable: volatility")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("\n--- Random Forest Model ---")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = rf_model.predict(X_test_scaled)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    print(f"Mean Squared Error: {mse:.6f}")
    print(f"R-squared Score: {r2:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
    
    # Feature importance
    feature_importance = rf_model.feature_importances_
    print(f"\nFeature Importance:")
    for i, feature in enumerate(features):
        print(f"{feature}: {feature_importance[i]:.4f}")
    
    # Cross-validation (FIXED: Added proper import)
    print(f"\n--- Cross-Validation ---")
    try:
        cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='r2')
        print(f"Cross-validation R² scores: {cv_scores}")
        print(f"Average CV R² score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    except Exception as e:
        print(f"Cross-validation error: {e}")
    
    # Additional analysis: Predict price change based on sentiment
    print(f"\n--- Price Change Prediction ---")
    X_price = df[['sentiment', 'buzz_volume', 'volatility']].fillna(0)
    y_price = df['change_24h'].fillna(0)
    
    X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(X_price, y_price, test_size=0.3, random_state=42)
    
    scaler_p = StandardScaler()
    X_train_p_scaled = scaler_p.fit_transform(X_train_p)
    X_test_p_scaled = scaler_p.transform(X_test_p)
    
    rf_price_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_price_model.fit(X_train_p_scaled, y_train_p)
    
    y_pred_p = rf_price_model.predict(X_test_p_scaled)
    
    mse_p = mean_squared_error(y_test_p, y_pred_p)
    r2_p = r2_score(y_test_p, y_pred_p)
    
    print(f"Price Change Prediction - MSE: {mse_p:.6f}, R²: {r2_p:.4f}")
    
    # Feature importance for price prediction
    feature_importance_p = rf_price_model.feature_importances_
    print(f"Feature Importance for Price Prediction:")
    for i, feature in enumerate(['sentiment', 'buzz_volume', 'volatility']):
        print(f"{feature}: {feature_importance_p[i]:.4f}")
    
    return {
        'volatility_model': rf_model,
        'price_model': rf_price_model,
        'scaler': scaler,
        'price_scaler': scaler_p,
        'metrics': {
            'volatility_mse': mse,
            'volatility_r2': r2,
            'price_mse': mse_p,
            'price_r2': r2_p
        }
    }

def create_correlation_analysis(df):
    """Create correlation analysis between sentiment and market metrics"""
    
    print(f"\n=== CORRELATION ANALYSIS ===")
    
    # Calculate correlations
    correlation_matrix = df[['sentiment', 'buzz_volume', 'volatility', 'change_24h', 'volume_24h']].corr()
    
    print("Correlation Matrix:")
    print(correlation_matrix.round(4))
    
    # Key correlations
    sentiment_volatility_corr = df['sentiment'].corr(df['volatility'])
    sentiment_price_change_corr = df['sentiment'].corr(df['change_24h'])
    buzz_volatility_corr = df['buzz_volume'].corr(df['volatility'])
    
    print(f"\nKey Correlations:")
    print(f"Sentiment vs Volatility: {sentiment_volatility_corr:.4f}")
    print(f"Sentiment vs Price Change: {sentiment_price_change_corr:.4f}")
    print(f"Buzz Volume vs Volatility: {buzz_volatility_corr:.4f}")
    
    return correlation_matrix

def generate_insights(df, ml_results, correlation_matrix):
    """Generate actionable insights from the analysis"""
    
    print(f"\n=== INSIGHTS & RECOMMENDATIONS ===")
    
    # High sentiment cryptocurrencies
    high_sentiment = df.nlargest(3, 'sentiment')[['name', 'sentiment', 'change_24h', 'volatility']]
    print(f"\nTop 3 Cryptocurrencies by Sentiment:")
    print(high_sentiment.to_string(index=False))
    
    # High volatility cryptocurrencies
    high_volatility = df.nlargest(3, 'volatility')[['name', 'volatility', 'sentiment', 'change_24h']]
    print(f"\nTop 3 Cryptocurrencies by Volatility:")
    print(high_volatility.to_string(index=False))
    
    # Model performance insights
    volatility_r2 = ml_results['metrics']['volatility_r2']
    price_r2 = ml_results['metrics']['price_r2']
    
    print(f"\nModel Performance:")
    print(f"Volatility Prediction R²: {volatility_r2:.4f}")
    print(f"Price Change Prediction R²: {price_r2:.4f}")
    
    if volatility_r2 > 0.3:
        print("✓ Good volatility prediction capability")
    else:
        print("⚠ Limited volatility prediction capability")
    
    if price_r2 > 0.3:
        print("✓ Good price change prediction capability")
    else:
        print("⚠ Limited price change prediction capability")
    
    # Trading insights
    print(f"\nTrading Insights:")
    
    # Find cryptocurrencies with high sentiment but low volatility (potential stable growth)
    stable_positive = df[(df['sentiment'] > 0.5) & (df['volatility'] < 0.04)]
    if not stable_positive.empty:
        print(f"Stable positive sentiment cryptos: {', '.join(stable_positive['symbol'].tolist())}")
    
    # Find cryptocurrencies with high buzz and high volatility (potential trading opportunities)
    high_activity = df[(df['buzz_volume'] > df['buzz_volume'].median()) & (df['volatility'] > df['volatility'].median())]
    if not high_activity.empty:
        print(f"High activity cryptos (buzz + volatility): {', '.join(high_activity['symbol'].tolist())}")
    
    return {
        'high_sentiment': high_sentiment,
        'high_volatility': high_volatility,
        'stable_positive': stable_positive,
        'high_activity': high_activity
    }

def main():
    """Main execution function"""
    
    print("Crypto Sentiment Analysis with Machine Learning")
    print("=" * 60)
    
    # Load data
    df = load_data()
    print(f"Loaded data for {len(df)} cryptocurrencies")
    
    # Perform ML analysis
    ml_results = perform_ml_analysis(df)
    
    # Create correlation analysis
    correlation_matrix = create_correlation_analysis(df)
    
    # Generate insights
    insights = generate_insights(df, ml_results, correlation_matrix)
    
    # Save results
    results = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'cryptocurrencies': df.to_dict('records'),
        'ml_metrics': ml_results['metrics'],
        'correlations': correlation_matrix.to_dict(),
        'insights': {
            'high_sentiment': insights['high_sentiment'].to_dict('records'),
            'high_volatility': insights['high_volatility'].to_dict('records'),
            'stable_positive': insights['stable_positive'].to_dict('records') if not insights['stable_positive'].empty else [],
            'high_activity': insights['high_activity'].to_dict('records') if not insights['high_activity'].empty else []
        }
    }
    
    with open('./resources/data/ml-analysis-results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Analysis complete! Results saved to ml-analysis-results.json")
    
    return results

if __name__ == "__main__":
    main()