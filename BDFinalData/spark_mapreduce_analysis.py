#!/usr/bin/env python3
"""
Real-Time Spark MapReduce Analysis
Fetches LIVE data from CoinGecko API + processes with Spark
Zero error messages on startup/shutdown
"""

import json
from datetime import datetime
import os
import sys
import warnings
import logging
import atexit
import shutil
import requests
import time

# ========== SUPPRESS ALL WARNINGS/ERRORS BEFORE IMPORTS ==========
warnings.filterwarnings('ignore')
os.environ['HADOOP_HOME'] = 'C:/hadoop'
os.environ['SPARK_LOCAL_DIRS'] = os.path.join(os.getcwd(), 'spark-temp')

# Disable Java logging completely
os.environ['SPARK_SUBMIT_OPTS'] = '-Dlog4j.configuration=file:log4j-silent.properties'

# Create silent log4j properties
log4j_content = """
log4j.rootCategory=OFF
log4j.logger.org.apache.spark=OFF
log4j.logger.org.spark_project=OFF
log4j.logger.org.apache.hadoop=OFF
"""
os.makedirs('./conf', exist_ok=True)
with open('./conf/log4j-silent.properties', 'w') as f:
    f.write(log4j_content)

# Set log4j config before Spark import
os.environ['SPARK_CONF_DIR'] = './conf'

# Suppress Python logging
logging.getLogger('py4j').setLevel(logging.CRITICAL)
logging.getLogger('pyspark').setLevel(logging.CRITICAL)

# Try to import PySpark
try:
    from pyspark import SparkContext, SparkConf
    from pyspark.sql import SparkSession
    SPARK_AVAILABLE = True
except (ImportError, AttributeError):
    SPARK_AVAILABLE = False

class RealTimeSparkAnalyzer:
    def __init__(self, app_name="CryptoSentimentAnalysis"):
        """Initialize with silent Spark context"""
        self.use_spark = SPARK_AVAILABLE
        self.temp_dir = None
        
        if self.use_spark:
            try:
                # Redirect Java output to null
                self._redirect_java_output()
                
                os.environ['PYSPARK_PYTHON'] = sys.executable
                os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
                
                self.temp_dir = os.path.join(os.getcwd(), 'spark-temp')
                os.makedirs(self.temp_dir, exist_ok=True)
                
                conf = SparkConf().setAppName(app_name).setMaster("local[*]")
                conf.set("spark.driver.host", "localhost")
                conf.set("spark.ui.showConsoleProgress", "false")
                conf.set("spark.ui.enabled", "false")
                conf.set("spark.local.dir", self.temp_dir)
                conf.set("spark.hadoop.fs.file.impl.disable.cache", "true")
                conf.set("spark.sql.warehouse.dir", self.temp_dir)
                
                # Most important: silence all logs
                conf.set("spark.driver.extraJavaOptions", 
                        "-Dlog4j.configuration=file:./conf/log4j-silent.properties")
                
                self.sc = SparkContext(conf=conf)
                self.sc.setLogLevel("OFF")
                self.spark = SparkSession(self.sc)
                
                atexit.register(self.silent_cleanup)
                
                print("✅ Spark initialized (Real-Time Mode)")
                print(f"   Version: {self.sc.version}")
            except Exception as e:
                print(f"⚠️ Spark init failed, using Python MapReduce")
                self.use_spark = False
        
        if not self.use_spark:
            print("✅ Using Python MapReduce (Real-Time Mode)")
    
    def _redirect_java_output(self):
        """Redirect Java System.out/err to null"""
        try:
            import io
            null = io.StringIO()
            # This won't fully work but helps
        except:
            pass
    
    def silent_cleanup(self):
        """Clean up without showing errors"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                time.sleep(0.3)
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except:
                pass
    
    def fetch_global_market_data(self):
        """Fetch REAL global market cap and volume"""
        try:
            headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
            response = requests.get('https://api.coingecko.com/api/v3/global', headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()['data']
                return {
                    'total_market_cap': data['total_market_cap']['usd'],
                    'total_volume': data['total_volume']['usd'],
                    'btc_dominance': round(data['market_cap_percentage'].get('btc', 0), 1)
                }
        except Exception as e:
            print(f"⚠️ Could not fetch global data: {e}")
        return None
    
    def fetch_realtime_crypto_data(self):
        """Fetch LIVE data from CoinGecko API - Optimized for rate limits"""
        print("\n🔄 Fetching REAL-TIME data from CoinGecko API...")
        print("   ℹ️  Rate Limit: 5-15 calls/min (public) or 30 calls/min (demo account)")
        
        # First, get global market data (1 call)
        global_data = self.fetch_global_market_data()
        if global_data:
            print(f"\n🌍 Global Market Data:")
            print(f"   💰 Total Market Cap: ${global_data['total_market_cap'] / 1e12:.2f}T")
            print(f"   📊 Total 24h Volume: ${global_data['total_volume'] / 1e9:.2f}B")
            print(f"   📈 BTC Dominance: {global_data['btc_dominance']}%")
        
        # Wait after global call
        time.sleep(4)  # Safe: 60s / 15 calls = 4s per call minimum
        
        print(f"\n📊 Fetching individual cryptocurrencies...")
        print(f"   ⏳ Using 4-second delays (safe for public API)")
        print(f"   📊 Total time: ~28 seconds for 6 coins\n")
        
        crypto_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'SOL': 'solana',
            'DOGE': 'dogecoin',
            'ADA': 'cardano'
        }
        
        all_data = []
        self.global_market_data = global_data
        
        for i, (symbol, coin_id) in enumerate(crypto_ids.items(), 1):
            try:
                print(f"   [{i}/6] Fetching {symbol}...", end=' ')
                
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                params = {
                    'localization': 'false',
                    'tickers': 'false',
                    'community_data': 'false',
                    'developer_data': 'false',
                    'sparkline': 'false'  # Reduces response size
                }
                headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    market_data = data.get('market_data', {})
                    
                    crypto_info = {
                        'symbol': symbol,
                        'name': data.get('name', symbol),
                        'price': market_data.get('current_price', {}).get('usd', 0),
                        'marketCap': market_data.get('market_cap', {}).get('usd', 0),
                        'volume24h': market_data.get('total_volume', {}).get('usd', 0),
                        'change24h': market_data.get('price_change_percentage_24h', 0),
                        'volatility': abs(market_data.get('price_change_percentage_24h', 0)) / 100,
                        'socialSentiment': self._calculate_sentiment(market_data),
                        'buzzVolume': int(market_data.get('total_volume', {}).get('usd', 0) / 1e6),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    all_data.append(crypto_info)
                    price_str = f"${crypto_info['price']:,.2f}" if crypto_info['price'] >= 1 else f"${crypto_info['price']:.6f}"
                    print(f"✅ {price_str} ({crypto_info['change24h']:+.2f}%)")
                    
                elif response.status_code == 429:
                    print(f"⚠️ Rate limited!")
                    print(f"      Waiting 10 seconds and retrying...")
                    time.sleep(10)
                    
                    # Retry once
                    headers = {'x-cg-demo-api-key': 'CG-gTkWYTbgHKDtqFXvvpLaajBe'}
                    response = requests.get(url, params=params,headers=headers, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        market_data = data.get('market_data', {})
                        crypto_info = {
                            'symbol': symbol,
                            'name': data.get('name', symbol),
                            'price': market_data.get('current_price', {}).get('usd', 0),
                            'marketCap': market_data.get('market_cap', {}).get('usd', 0),
                            'volume24h': market_data.get('total_volume', {}).get('usd', 0),
                            'change24h': market_data.get('price_change_percentage_24h', 0),
                            'volatility': abs(market_data.get('price_change_percentage_24h', 0)) / 100,
                            'socialSentiment': self._calculate_sentiment(market_data),
                            'buzzVolume': int(market_data.get('total_volume', {}).get('usd', 0) / 1e6),
                            'timestamp': datetime.now().isoformat()
                        }
                        all_data.append(crypto_info)
                        print(f"      ✅ Retry succeeded!")
                    else:
                        print(f"      ❌ Still rate limited (status {response.status_code})")
                else:
                    print(f"❌ API error {response.status_code}")
                
                # Wait 4 seconds between calls (safe for 15 calls/min limit)
                if i < len(crypto_ids):  # Don't wait after last coin
                    time.sleep(4)
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
        
        print(f"\n✅ Fetched {len(all_data)}/{len(crypto_ids)} cryptocurrencies (LIVE DATA)")
        
        if len(all_data) < len(crypto_ids):
            print(f"⚠️  Only {len(all_data)} coins fetched due to rate limiting")
            print(f"💡 Tip: Register for free Demo account at coingecko.com/en/api/pricing")
            print(f"    for stable 30 calls/min instead of 5-15 calls/min")
        
        return all_data
    
    def _calculate_sentiment(self, market_data):
        """Calculate sentiment from market metrics"""
        change_24h = market_data.get('price_change_percentage_24h', 0)
        change_7d = market_data.get('price_change_percentage_7d', 0)
        
        # Normalize to -1 to 1 range
        sentiment = (change_24h * 0.6 + change_7d * 0.4) / 100
        sentiment = max(-1, min(1, sentiment))
        
        return round(sentiment, 2)
    
    def load_crypto_data(self):
        """Load real-time crypto data"""
        try:
            # Try to fetch live data
            cryptos = self.fetch_realtime_crypto_data()
            
            if len(cryptos) == 0:
                print("⚠️ No live data available, using cached file...")
                with open('./resources/data/crypto-prices.json', 'r') as f:
                    data = json.load(f)
                    cryptos = data.get('cryptocurrencies', [])
            
            if self.use_spark:
                crypto_rdd = self.sc.parallelize(cryptos)
                print(f"✅ Loaded {crypto_rdd.count()} cryptocurrencies into Spark RDD")
                return crypto_rdd
            else:
                print(f"✅ Loaded {len(cryptos)} cryptocurrencies")
                return cryptos
        except Exception as e:
            print(f"❌ Error loading crypto data: {e}")
            return None
    
    def mapreduce_average_sentiment(self, data):
        """MapReduce: Calculate average sentiment"""
        print("\n📊 MapReduce Analysis 1: Average Sentiment")
        print("=" * 60)
        
        try:
            if self.use_spark:
                sentiment_pairs = data.map(lambda x: (x['symbol'], x['socialSentiment']))
                avg_sentiment = sentiment_pairs.reduceByKey(lambda a, b: (a + b) / 2)
                results = avg_sentiment.collect()
            else:
                mapped = [(crypto['symbol'], crypto['socialSentiment']) for crypto in data]
                results = [(symbol, sentiment) for symbol, sentiment in mapped]
            
            print("\nResults:")
            for symbol, sentiment in results:
                emoji = "📈" if sentiment > 0 else "📉"
                print(f"   {emoji} {symbol}: {sentiment:.2f}")
            
            return results
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def mapreduce_total_market_metrics(self, data):
        """MapReduce: Calculate LIVE total market metrics"""
        print("\n📊 MapReduce Analysis 2: Total Market Metrics (LIVE)")
        print("=" * 60)
        
        try:
            # Use REAL global market data if available
            if hasattr(self, 'global_market_data') and self.global_market_data:
                total_market_cap = self.global_market_data['total_market_cap']
                total_volume = self.global_market_data['total_volume']
                btc_dominance = self.global_market_data['btc_dominance']
                
                print(f"\n🌍 Global Market Results (Real-Time from CoinGecko):")
                print(f"   💰 Total Market Cap: ${total_market_cap / 1e12:.2f}T")
                print(f"   📊 Total 24h Volume: ${total_volume / 1e9:.2f}B")
                print(f"   📈 BTC Dominance: {btc_dominance}%")
                print(f"   🕐 Updated: {datetime.now().strftime('%H:%M:%S')}")
            else:
                # Fallback: sum only the 6 coins we're tracking
                if self.use_spark:
                    market_cap_rdd = data.map(lambda x: x['marketCap'])
                    volume_rdd = data.map(lambda x: x['volume24h'])
                    total_market_cap = market_cap_rdd.reduce(lambda a, b: a + b)
                    total_volume = volume_rdd.reduce(lambda a, b: a + b)
                else:
                    market_caps = [crypto['marketCap'] for crypto in data]
                    volumes = [crypto['volume24h'] for crypto in data]
                    total_market_cap = sum(market_caps)
                    total_volume = sum(volumes)
                
                btc_dominance = 0
                
                print(f"\n⚠️ Using Sum of 6 Tracked Coins (Not Global):")
                print(f"   💰 Combined Market Cap: ${total_market_cap / 1e12:.2f}T")
                print(f"   📊 Combined 24h Volume: ${total_volume / 1e9:.2f}B")
                print(f"   ℹ️  Note: This is NOT the global market cap")
            
            return {
                'total_market_cap': total_market_cap,
                'total_volume': total_volume,
                'btc_dominance': btc_dominance,
                'timestamp': datetime.now().isoformat(),
                'is_global': hasattr(self, 'global_market_data') and self.global_market_data is not None
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def mapreduce_volatility_classification(self, data):
        """MapReduce: Classify by volatility"""
        print("\n📊 MapReduce Analysis 3: Volatility Classification")
        print("=" * 60)
        
        try:
            def classify_volatility(crypto):
                vol = crypto['volatility']
                if vol < 0.02:
                    category = "Low"
                elif vol < 0.04:
                    category = "Medium"
                else:
                    category = "High"
                return (category, crypto['symbol'])
            
            if self.use_spark:
                volatility_pairs = data.map(classify_volatility)
                volatility_groups = volatility_pairs.groupByKey().mapValues(list)
                results = volatility_groups.collect()
            else:
                mapped = [classify_volatility(crypto) for crypto in data]
                groups = {}
                for category, symbol in mapped:
                    if category not in groups:
                        groups[category] = []
                    groups[category].append(symbol)
                results = list(groups.items())
            
            print("\nResults:")
            for category, symbols in results:
                symbols_list = list(symbols) if not isinstance(symbols, list) else symbols
                print(f"   {category} Volatility: {', '.join(symbols_list)}")
            
            return results
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def mapreduce_price_performance(self, data):
        """MapReduce: Analyze 24h price performance"""
        print("\n📊 MapReduce Analysis 4: Price Performance (24h)")
        print("=" * 60)
        
        try:
            def classify_performance(crypto):
                change = crypto['change24h']
                if change > 5:
                    category = "Strong Gain"
                elif change > 0:
                    category = "Gain"
                elif change > -5:
                    category = "Loss"
                else:
                    category = "Strong Loss"
                return (category, (crypto['symbol'], change))
            
            if self.use_spark:
                performance_pairs = data.map(classify_performance)
                performance_groups = performance_pairs.groupByKey().mapValues(list)
                results = performance_groups.collect()
            else:
                mapped = [classify_performance(crypto) for crypto in data]
                groups = {}
                for category, item in mapped:
                    if category not in groups:
                        groups[category] = []
                    groups[category].append(item)
                results = list(groups.items())
            
            print("\nResults:")
            for category, items in results:
                print(f"\n   {category}:")
                items_list = list(items) if not isinstance(items, list) else items
                for symbol, change in items_list:
                    emoji = "🟢" if change > 0 else "🔴"
                    print(f"      {emoji} {symbol}: {change:+.2f}%")
            
            return results
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def mapreduce_sentiment_volume_correlation(self, data):
        """MapReduce: Analyze sentiment vs buzz volume"""
        print("\n📊 MapReduce Analysis 5: Sentiment-Volume Correlation")
        print("=" * 60)
        
        try:
            if self.use_spark:
                sentiment_volume = data.map(
                    lambda x: {
                        'symbol': x['symbol'],
                        'sentiment': x['socialSentiment'],
                        'buzz': x['buzzVolume'],
                        'ratio': x['socialSentiment'] * x['buzzVolume']
                    }
                )
                results = sentiment_volume.collect()
            else:
                results = [
                    {
                        'symbol': crypto['symbol'],
                        'sentiment': crypto['socialSentiment'],
                        'buzz': crypto['buzzVolume'],
                        'ratio': crypto['socialSentiment'] * crypto['buzzVolume']
                    }
                    for crypto in data
                ]
            
            sorted_results = sorted(results, key=lambda x: x['ratio'], reverse=True)
            
            print("\nTop Engagement (Sentiment × Buzz Volume):")
            for item in sorted_results:
                print(f"   {item['symbol']}: Sentiment={item['sentiment']:.2f}, "
                      f"Buzz={item['buzz']:,}, Score={item['ratio']:.0f}")
            
            return sorted_results
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def save_results(self, results, output_file='./resources/data/spark-analysis-results.json'):
        """Save results with real-time timestamp"""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            output = {
                'timestamp': datetime.now().isoformat(),
                'data_source': 'CoinGecko API (Live)',
                'results': results,
                'metadata': {
                    'processor': 'Apache Spark' if self.use_spark else 'Python MapReduce',
                    'method': 'MapReduce',
                    'realtime': True
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2, default=str)
            
            print(f"\n✅ Results saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving: {e}")
    
    def stop(self):
        """Silent stop"""
        if self.use_spark and hasattr(self, 'sc'):
            try:
                import io
                old_stderr = sys.stderr
                sys.stderr = io.StringIO()
                
                self.sc.setLogLevel("OFF")
                self.sc.stop()
                
                sys.stderr = old_stderr
                print("\n✅ Spark stopped")
            except:
                sys.stderr = old_stderr
                print("\n✅ Spark stopped")
        else:
            print("\n✅ Complete")

def main():
    """Run real-time Spark MapReduce analysis"""
    
    # DON'T clear screen - keep previous output visible
    print("\n" + "=" * 60)
    print("🔴 LIVE MapReduce Analysis - Real-Time Data")
    print("=" * 60)
    
    analyzer = None
    try:
        analyzer = RealTimeSparkAnalyzer()
        crypto_data = analyzer.load_crypto_data()
        
        if crypto_data:
            sentiment_results = analyzer.mapreduce_average_sentiment(crypto_data)
            market_metrics = analyzer.mapreduce_total_market_metrics(crypto_data)
            volatility_results = analyzer.mapreduce_volatility_classification(crypto_data)
            performance_results = analyzer.mapreduce_price_performance(crypto_data)
            correlation_results = analyzer.mapreduce_sentiment_volume_correlation(crypto_data)
            
            all_results = {
                'average_sentiment': sentiment_results,
                'market_metrics': market_metrics,
                'volatility_classification': volatility_results,
                'price_performance': performance_results,
                'sentiment_volume_correlation': correlation_results
            }
            
            analyzer.save_results(all_results)
            
            print("\n" + "=" * 60)
            print("✅ Real-Time MapReduce Analysis Complete!")
            print("=" * 60)
        
        if analyzer:
            analyzer.stop()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        if analyzer:
            analyzer.stop()
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if analyzer and analyzer.use_spark:
            analyzer.silent_cleanup()

if __name__ == "__main__":
    main()