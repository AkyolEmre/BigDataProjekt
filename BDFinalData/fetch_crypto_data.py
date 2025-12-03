#!/usr/bin/env python3
"""
Enhanced Real-Time Crypto Data Fetcher with Auto-Refresh
Fetches live cryptocurrency data from Yahoo Finance API every 10 seconds
"""

import yfinance as yf
import json
import pandas as pd
from datetime import datetime
import numpy as np
import time
import threading
import os

class RealtimeCryptoFetcher:
    def __init__(self, update_interval=10):
        self.update_interval = update_interval
        self.running = False
        
        self.crypto_tickers = {
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'XRP-USD': 'Ripple',
            'SOL-USD': 'Solana',
            'DOGE-USD': 'Dogecoin',
            'ADA-USD': 'Cardano'
        }
        
        self.output_dir = './resources/data'
        self.output_file = os.path.join(self.output_dir, 'crypto-prices.json')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_realtime_price(self, ticker):
        try:
            crypto = yf.Ticker(ticker)
            info = crypto.info
            hist = crypto.history(period="1d", interval="1m")
            
            if hist.empty:
                hist = crypto.history(period="5d", interval="1h")
            
            return info, hist
        except Exception as e:
            print(f"⚠️ Error fetching {ticker}: {e}")
            return None, None
    
    def calculate_realtime_volatility(self, hist_data):
        if hist_data is None or hist_data.empty:
            return 0.02
        
        prices = hist_data['Close'].tolist()
        if len(prices) < 2:
            return 0.02
        
        returns = pd.Series(prices).pct_change().dropna()
        volatility = returns.std() if len(returns) > 0 else 0.02
        return abs(volatility)
    
    def calculate_sentiment(self, change_24h, volatility, volume_change):
        sentiment = np.tanh(change_24h / 10)
        volatility_factor = 1 - min(volatility * 10, 0.5)
        volume_factor = 1 + min(abs(volume_change) / 100, 0.3)
        
        final_sentiment = sentiment * volatility_factor * volume_factor
        return max(-1, min(1, final_sentiment))
    
    def fetch_data(self):
        print(f"\n🔄 Fetching at {datetime.now().strftime('%H:%M:%S')}")
        
        cryptocurrencies = []
        total_market_cap = 0
        total_volume = 0
        sentiments = []
        
        for ticker, name in self.crypto_tickers.items():
            info, hist_data = self.fetch_realtime_price(ticker)
            
            if info and hist_data is not None and not hist_data.empty:
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                previous_close = info.get('previousClose', current_price)
                
                change_24h = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0
                
                volume_24h = info.get('volume', info.get('regularMarketVolume', 0))
                avg_volume = info.get('averageVolume', volume_24h)
                volume_change = ((volume_24h - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
                
                market_cap = info.get('marketCap', 0)
                volatility = self.calculate_realtime_volatility(hist_data)
                
                sparkline = [round(p, 2) for p in hist_data['Close'].tail(20).tolist()]
                
                social_sentiment = self.calculate_sentiment(change_24h, volatility, volume_change)
                buzz_volume = int(min(volume_24h / 1e9, 100) * 1000 * (1 + abs(volume_change) / 100))
                buzz_volume = max(1000, min(buzz_volume, 100000))
                
                crypto_data = {
                    "symbol": ticker.replace('-USD', ''),
                    "name": name,
                    "price": round(current_price, 2),
                    "change24h": round(change_24h, 2),
                    "volume24h": int(volume_24h),
                    "volumeChange": round(volume_change, 2),
                    "marketCap": int(market_cap),
                    "volatility": round(volatility, 4),
                    "sparkline": sparkline,
                    "socialSentiment": round(social_sentiment, 2),
                    "buzzVolume": buzz_volume,
                    "lastUpdate": datetime.now().isoformat()
                }
                
                cryptocurrencies.append(crypto_data)
                total_market_cap += market_cap
                total_volume += volume_24h
                sentiments.append(social_sentiment)
                
                emoji = "🟢" if change_24h > 0 else "🔴"
                print(f"{emoji} {name}: ${current_price:,.2f} ({change_24h:+.2f}%)")
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0
        
        market_overview = {
            "totalMarketCap": int(total_market_cap),
            "totalVolume": int(total_volume),
            "btcDominance": round((cryptocurrencies[0]['marketCap'] / total_market_cap * 100), 2),
            "fearGreedIndex": int((avg_sentiment + 1) * 50),
            "socialSentiment": round(avg_sentiment, 2),
            "timestamp": datetime.now().isoformat(),
            "lastUpdate": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data = {
            "cryptocurrencies": cryptocurrencies,
            "marketOverview": market_overview,
            "metadata": {
                "updateInterval": self.update_interval,
                "lastFetch": datetime.now().isoformat()
            }
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Saved to: {self.output_file}")
        return data
    
    def auto_refresh(self):
        while self.running:
            try:
                self.fetch_data()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(self.update_interval)
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.auto_refresh, daemon=True)
            self.thread.start()
            print(f"🚀 Started (updating every {self.update_interval}s)")
            print("Press Ctrl+C to stop...")
    
    def stop(self):
        self.running = False
        print("🛑 Stopped")

if __name__ == "__main__":
    fetcher = RealtimeCryptoFetcher(update_interval=10)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        fetcher.fetch_data()
    else:
        fetcher.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            fetcher.stop()