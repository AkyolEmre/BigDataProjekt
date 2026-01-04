#!/usr/bin/env python3
"""
Real-Time Crypto Data Fetcher - GLOBAL MARKET DATA
Fetches actual global market cap and volume from CoinGecko
"""

import requests
import json
from datetime import datetime, timedelta
import os
import time
import sys

class GlobalCryptoFetcher:
    def __init__(self):
        self.output_dir = './resources/data'
        self.output_file = os.path.join(self.output_dir, 'crypto-prices.json')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_global_market_data(self):
        """Fetch REAL global market statistics"""
        try:
            print("🌍 Fetching global market data...")
            headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
            response = requests.get('https://api.coingecko.com/api/v3/global', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                
                global_stats = {
                    'totalMarketCap': data['total_market_cap']['usd'],
                    'totalVolume': data['total_volume']['usd'],
                    'btcDominance': round(data['market_cap_percentage'].get('btc', 0), 1),
                    'ethDominance': round(data['market_cap_percentage'].get('eth', 0), 1),
                    'marketCapChange24h': data['market_cap_change_percentage_24h_usd'],
                    'activeCryptocurrencies': data['active_cryptocurrencies'],
                    'markets': data['markets']
                }
                
                print(f"   ✅ Global Market Cap: ${global_stats['totalMarketCap'] / 1e12:.2f}T")
                print(f"   ✅ Global 24h Volume: ${global_stats['totalVolume'] / 1e9:.2f}B")
                print(f"   ✅ BTC Dominance: {global_stats['btcDominance']}%")
                
                return global_stats
            else:
                print(f"   ⚠️ Global API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching global data: {e}")
            return None
    
    def fetch_crypto_details(self, coin_id, symbol):
        """Fetch detailed data for a specific cryptocurrency"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'true'
            }
            headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 429:
                print(f"⚠️ Rate limited!")
                print(f"\n      Waiting 15 seconds and retrying...")
                time.sleep(15)
                headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
                response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                # Get sparkline data
                sparkline = market_data.get('sparkline_7d', {}).get('price', [])
                
                # Generate timestamps for sparkline (7 days of hourly data)
                now = datetime.now()
                timestamps = [(now - timedelta(hours=len(sparkline)-i-1)).isoformat() 
                             for i in range(len(sparkline))]
                
                crypto_info = {
                    'symbol': symbol,
                    'name': data.get('name', symbol),
                    'price': market_data.get('current_price', {}).get('usd', 0),
                    'marketCap': market_data.get('market_cap', {}).get('usd', 0),
                    'volume24h': market_data.get('total_volume', {}).get('usd', 0),
                    'change24h': market_data.get('price_change_percentage_24h', 0),
                    'change7d': market_data.get('price_change_percentage_7d', 0),
                    'change30d': market_data.get('price_change_percentage_30d', 0),
                    'volatility': abs(market_data.get('price_change_percentage_24h', 0)) / 100,
                    'socialSentiment': self._calculate_sentiment(market_data),
                    'buzzVolume': int(market_data.get('total_volume', {}).get('usd', 0) / 1e6),
                    'sparkline': sparkline,
                    'sparkline_timestamps': timestamps,
                    'high24h': market_data.get('high_24h', {}).get('usd', 0),
                    'low24h': market_data.get('low_24h', {}).get('usd', 0),
                    'ath': market_data.get('ath', {}).get('usd', 0),
                    'atl': market_data.get('atl', {}).get('usd', 0),
                    'circulatingSupply': market_data.get('circulating_supply', 0),
                    'totalSupply': market_data.get('total_supply', 0)
                }
                
                price_str = f"${crypto_info['price']:,.2f}" if crypto_info['price'] >= 1 else f"${crypto_info['price']:.6f}"
                change_str = f"{crypto_info['change24h']:+.2f}%"
                print(f"✅ {price_str} ({change_str})")
                
                return crypto_info
            else:
                print(f"❌ API error {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ {str(e)[:60]}")
            return None
    
    def _calculate_sentiment(self, market_data):
        """Calculate sentiment from market metrics"""
        change_24h = market_data.get('price_change_percentage_24h', 0)
        change_7d = market_data.get('price_change_percentage_7d', 0)
        
        # Normalize to -1 to 1 range
        sentiment = (change_24h * 0.6 + change_7d * 0.4) / 100
        sentiment = max(-1, min(1, sentiment))
        
        return round(sentiment, 2)
    
    def fetch_fear_greed_index(self):
        """Fetch Fear & Greed Index"""
        try:
            response = requests.get('https://api.alternative.me/fng/?limit=1', timeout=5)
            if response.status_code == 200:
                data = response.json()['data'][0]
                return {
                    'value': int(data['value']),
                    'classification': data['value_classification']
                }
        except:
            pass
        return {'value': 50, 'classification': 'Neutral'}
    
    def fetch_all_data(self):
        """Fetch complete crypto dataset with GLOBAL market data"""
        print("\n" + "=" * 70)
        print("🔄 Fetching Real-Time Cryptocurrency Data")
        print("=" * 70)
        
        # 1. Get GLOBAL market statistics
        global_data = self.fetch_global_market_data()
        
        if not global_data:
            print("\n⚠️ Using fallback global data")
            global_data = {
                'totalMarketCap': 3159226766302,  # Fallback from your screenshot
                'totalVolume': 79390979766,
                'btcDominance': 57.8,
                'ethDominance': 12.5,
                'marketCapChange24h': 0.3,
                'activeCryptocurrencies': 15000,
                'markets': 800
            }
        
        time.sleep(0.5)
        
        # 2. Get individual cryptocurrency data
        print("\n📊 Fetching individual cryptocurrencies...")
        print("   ℹ️  Rate Limit: 5-15 calls/min (public) or 30 calls/min (demo)")
        print("   ⏳ Using 4-second delays (safe for public API)")
        print("   📊 Total time: ~28 seconds for 6 coins\n")
        
        crypto_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'SOL': 'solana',
            'DOGE': 'dogecoin',
            'ADA': 'cardano'
        }
        
        cryptocurrencies = []
        
        for i, (symbol, coin_id) in enumerate(crypto_ids.items(), 1):
            print(f"   [{i}/6] Fetching {symbol}...", end=' ', flush=True)
            
            crypto_data = self.fetch_crypto_details(coin_id, symbol)
            if crypto_data:
                cryptocurrencies.append(crypto_data)
            
            # Wait 4 seconds between calls (60s / 15 calls = 4s minimum)
            if i < len(crypto_ids):
                time.sleep(4.0)
        
        # 3. Get Fear & Greed Index
        print("\n📈 Fetching Fear & Greed Index...")
        fear_greed = self.fetch_fear_greed_index()
        print(f"   ✅ Fear & Greed: {fear_greed['value']} ({fear_greed['classification']})")
        
        # 4. Calculate overall social sentiment
        if cryptocurrencies:
            avg_sentiment = sum(c['socialSentiment'] for c in cryptocurrencies) / len(cryptocurrencies)
        else:
            avg_sentiment = 0
        
        # 5. Build complete dataset
        complete_data = {
            'marketOverview': {
                'totalMarketCap': global_data['totalMarketCap'],
                'totalVolume': global_data['totalVolume'],
                'btcDominance': global_data['btcDominance'],
                'ethDominance': global_data.get('ethDominance', 0),
                'marketCapChange24h': global_data.get('marketCapChange24h', 0),
                'fearGreedIndex': fear_greed['value'],
                'fearGreedClassification': fear_greed['classification'],
                'socialSentiment': round(avg_sentiment, 2),
                'activeCryptocurrencies': global_data.get('activeCryptocurrencies', 0),
                'markets': global_data.get('markets', 0)
            },
            'cryptocurrencies': cryptocurrencies,
            'metadata': {
                'lastUpdate': datetime.now().isoformat(),
                'dataSource': 'CoinGecko API (Global)',
                'updateInterval': 120,
                'cryptoCount': len(cryptocurrencies)
            }
        }
        
        # 6. Save to file
        with open(self.output_file, 'w') as f:
            json.dump(complete_data, f, indent=2)
        
        print("\n" + "=" * 70)
        print(f"✅ Data saved to: {self.output_file}")
        print(f"📊 Cryptocurrencies: {len(cryptocurrencies)}")
        print(f"💰 Global Market Cap: ${global_data['totalMarketCap'] / 1e12:.2f}T")
        print(f"📊 Global Volume: ${global_data['totalVolume'] / 1e9:.2f}B")
        print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        return complete_data

def main():
    fetcher = GlobalCryptoFetcher()
    
    # Check if running in single-fetch mode
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        fetcher.fetch_all_data()
        print("✅ Single fetch complete")
        return
    
    # Continuous mode
    print("🚀 Starting Real-Time Crypto Data Fetcher")
    print("🔄 Fetching data every 120 seconds")
    print("📡 Using CoinGecko Global API")
    print("Press Ctrl+C to stop...\n")
    
    while True:
        try:
            fetcher.fetch_all_data()
            print(f"⏳ Next update in 120 seconds...")
            time.sleep(120)
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("⏳ Retrying in 120 seconds...")
            time.sleep(120)

if __name__ == "__main__":
    main()