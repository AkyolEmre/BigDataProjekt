#!/usr/bin/env python3
"""
CryptoSentiment Dashboard - Complete Orchestrator
Big Data Analytics Final Project

Team: Emre Akyol, Harmanpreet Chauhan, Mohamed Nasr
"""

import os
import sys
import time
import json
import threading
import signal
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuration
HTTP_PORT = 8000
DATA_DIR = './resources/data'
REFRESH_INTERVAL = 120  # seconds

class DashboardOrchestrator:
    """Main orchestrator for the CryptoSentiment dashboard"""
    
    def __init__(self):
        self.processes = []
        self.http_server = None
        self.running = True
        self.data_ready = False
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def print_banner(self):
        """Print startup banner"""
        print("Crypto Sentiment")
    
    def step(self, number, title, status="running"):
        """Print step status"""
        print(f"\n Step {number}: {title}")
        print("=" * 60)
    
    def run_data_collection(self):
        """Step 1: Collect cryptocurrency data"""
        self.step(1, "Data Collection (CoinGecko API)")
        
        try:
            # Use the correct class name: GlobalCryptoFetcher
            from fetch_crypto_data import GlobalCryptoFetcher
            fetcher = GlobalCryptoFetcher()
            data = fetcher.fetch_all_data()
            
            if data and 'cryptocurrencies' in data:
                print(f" Fetched {len(data['cryptocurrencies'])} cryptocurrencies")
                print(f" Market cap: ${data['marketOverview'].get('totalMarketCap', 0)/1e12:.2f}T")
                return True
        except ImportError as e:
            print(f" Import Error: {e}")
            print("  Checking for cached data...")
        except Exception as e:
            print(f" Error: {e}")
            print("   Checking for cached data...")
            
        if os.path.exists(f"{DATA_DIR}/crypto-prices.json"):
            print(" Using cached crypto-prices.json")
            return True
        
        return False
    
    def run_sentiment_collection(self):
        """Step 2: Collect sentiment data"""
        self.step(2, "Sentiment Collection (Alternative.me + CryptoPanic)")
        
        try:
            # Use the correct class name: EnhancedSentimentFetcher
            from fetch_real_sentiment import EnhancedSentimentFetcher
            fetcher = EnhancedSentimentFetcher()
            data = fetcher.fetch_all_data()
            
            if data:
                fg = data.get('sentimentOverview', {}).get('fearGreedIndex', 'N/A')
                print(f" Fear & Greed Index: {fg}")
                return True
        except ImportError as e:
            print(f" Import Error: {e}")
        except Exception as e:
            print(f" Error: {e}")
            
        if os.path.exists(f"{DATA_DIR}/sentiment-data.json"):
            print(" Using cached sentiment-data.json")
            return True
        
        return False
    
    def run_mongodb_storage(self):
        """Step 3: Store data in MongoDB"""
        self.step(3, "MongoDB Storage (NoSQL Layer)")
        
        try:
            from mongodb_storage import EnhancedCryptoStorage
            storage = EnhancedCryptoStorage()
            
            # Load and store crypto data
            crypto_file = f"{DATA_DIR}/crypto-prices.json"
            if os.path.exists(crypto_file):
                with open(crypto_file, 'r') as f:
                    crypto_data = json.load(f)
                storage.store_crypto_data(crypto_data)
            
            # Load and store sentiment data
            sentiment_file = f"{DATA_DIR}/sentiment-data.json"
            if os.path.exists(sentiment_file):
                try:
                    with open(sentiment_file, 'r') as f:
                        sentiment_data = json.load(f)
                    storage.store_sentiment_data(sentiment_data)
                except:
                    pass
            
            storage.get_statistics()
            storage.close()
            return True
            
        except ImportError:
            print(f" pymongo not installed")
            print("  Data will be served from JSON files")
            return False
        except Exception as e:
            print(f" MongoDB not available: {e}")
            print("  Data will be served from JSON files")
            print("\n  To enable MongoDB:")
            print("      docker run -d -p 27017:27017 --name crypto-mongodb mongo")
            return False
    
    def run_ml_analysis(self):
        """Step 4: Run ML analysis"""
        self.step(4, "Machine Learning Analysis")
        
        try:
            from real_data_ml_analysis import RealDataMLAnalyzer
            analyzer = RealDataMLAnalyzer()
            
            df, fear_greed = analyzer.load_real_data()
            if df is not None:
                analyzer.analyze_correlations(df)
                analyzer.predict_volatility(df)
                analyzer.predict_price_change(df)
                analyzer.analyze_fear_greed_impact(df, fear_greed)
                analyzer.save_results()
                return True
        except ImportError as e:
            print(f" Import Error: {e}")
            print("   Dashboard will work without ML predictions")
        except Exception as e:
            print(f" ML analysis error: {e}")
            print("  Dashboard will work without ML predictions")
        
        return False
    
    def run_spark_analysis(self):
        """Step 5: Run Spark MapReduce analysis"""
        self.step(5, "Spark MapReduce Analysis")
        
        try:
            from spark_mapreduce_analysis import RealTimeSparkAnalyzer
            
            analyzer = RealTimeSparkAnalyzer()
            crypto_data = analyzer.load_crypto_data()
            
            if crypto_data:
                # Run MapReduce operations
                sentiment_results = analyzer.mapreduce_average_sentiment(crypto_data)
                market_metrics = analyzer.mapreduce_total_market_metrics(crypto_data)
                volatility_results = analyzer.mapreduce_volatility_classification(crypto_data)
                performance_results = analyzer.mapreduce_price_performance(crypto_data)
                
                all_results = {
                    'average_sentiment': sentiment_results,
                    'market_metrics': market_metrics,
                    'volatility_classification': volatility_results,
                    'price_performance': performance_results
                }
                
                analyzer.save_results(all_results)
                analyzer.stop()
                return True
                
        except ImportError as e:
            print(f" Import Error: {e}")
            print("  Dashboard will work without Spark analysis")
        except Exception as e:
            print(f" Spark error: {e}")
            print("  Dashboard will work without Spark analysis")
        
        return False
    
    def start_http_server(self):
        """Step 6: Start HTTP server"""
        self.step(6, "Web Dashboard Server")
        
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress request logging
        
        try:
            self.http_server = HTTPServer(('', HTTP_PORT), QuietHandler)
            
            # Start server in background thread
            server_thread = threading.Thread(target=self.http_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            print(f" HTTP server running on port {HTTP_PORT}")
            return True
            
        except Exception as e:
            print(f" Failed to start HTTP server: {e}")
            return False
    
    def print_dashboard_urls(self):
        """Print dashboard URLs"""
        print("\n" + "=" * 60)
        print(" DASHBOARD READY!")
        print("=" * 60)
        print(f"""
    Main Dashboard:      http://localhost:{HTTP_PORT}/index.html
    Sentiment Analysis:  http://localhost:{HTTP_PORT}/sentiment.html
    Correlation:         http://localhost:{HTTP_PORT}/correlation.html
    ML Predictions:      http://localhost:{HTTP_PORT}/predictions.html
        """)
        print("=" * 60)
        print("   Press Ctrl+C to stop the dashboard")
        print("=" * 60)
    
    def run_background_updates(self):
        """Run periodic data updates in background"""
        def update_loop():
            while self.running:
                time.sleep(REFRESH_INTERVAL)
                if not self.running:
                    break
                    
                print(f"\n Auto-refresh at {datetime.now().strftime('%H:%M:%S')}")
                try:
                    self.run_data_collection()
                    self.run_sentiment_collection()
                except Exception as e:
                    print(f" Update error: {e}")
        
        update_thread = threading.Thread(target=update_loop)
        update_thread.daemon = True
        update_thread.start()
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        print("\n\n Shutting down CryptoSentiment Dashboard...")
        self.running = False
        
        if self.http_server:
            self.http_server.shutdown()
        
        print(" Goodbye!")
        sys.exit(0)
    
    def run(self, skip_mongodb=False, skip_spark=False, open_browser=True):
        """Run the complete dashboard pipeline"""
        self.print_banner()
        
        print(f"\n Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Data directory: {os.path.abspath(DATA_DIR)}")
        
        # Step 1: Crypto Data
        crypto_ok = self.run_data_collection()
        if not crypto_ok:
            print("\n Cannot proceed without cryptocurrency data")
            print("   Please ensure crypto-prices.json exists in resources/data/")
            return False
        
        time.sleep(1)
        
        # Step 2: Sentiment Data
        self.run_sentiment_collection()
        
        time.sleep(1)
        
        # Step 3: MongoDB (optional)
        if not skip_mongodb:
            self.run_mongodb_storage()
        else:
            self.step(3, "MongoDB Storage (Skipped)", "skip")
        
        time.sleep(1)
        
        # Step 4: ML Analysis
        self.run_ml_analysis()
        
        time.sleep(1)
        
        # Step 5: Spark Analysis (optional)
        if not skip_spark:
            self.run_spark_analysis()
        else:
            self.step(5, "Spark MapReduce Analysis (Skipped)", "skip")
        
        time.sleep(1)
        
        # Step 6: HTTP Server
        server_ok = self.start_http_server()
        if not server_ok:
            return False
        
        self.data_ready = True
        
        # Print URLs
        self.print_dashboard_urls()
        
        # Open browser
        if open_browser:
            time.sleep(1)
            try:
                webbrowser.open(f"http://localhost:{HTTP_PORT}/index.html")
            except:
                pass
        
        # Start background updates
        self.run_background_updates()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CryptoSentiment Dashboard - Big Data Analytics Project"
    )
    parser.add_argument(
        '--no-mongodb', 
        action='store_true', 
        help='Skip MongoDB storage'
    )
    parser.add_argument(
        '--no-spark', 
        action='store_true', 
        help='Skip Spark analysis'
    )
    parser.add_argument(
        '--no-browser', 
        action='store_true', 
        help='Do not open browser automatically'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000, 
        help='HTTP server port (default: 8000)'
    )
    
    args = parser.parse_args()
    
    global HTTP_PORT
    HTTP_PORT = args.port
    
    orchestrator = DashboardOrchestrator()
    orchestrator.run(
        skip_mongodb=args.no_mongodb,
        skip_spark=args.no_spark,
        open_browser=not args.no_browser
    )


if __name__ == "__main__":
    main()