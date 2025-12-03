#!/usr/bin/env python3
"""
Start Complete Dashboard with Real-Time Data
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("🚀 Starting Crypto Sentiment Analytics Dashboard")
    print("=" * 60)
    
    # Start real-time data fetcher
    print("\n📡 Starting real-time data fetcher...")
    fetcher_process = subprocess.Popen([
        sys.executable, 
        'fetch_crypto_data.py'
    ])
    
    # Wait for initial data
    print("⏳ Waiting for initial data fetch...")
    time.sleep(5)
    
    # Check if data file exists
    if os.path.exists('./resources/data/crypto-prices.json'):
        print("✅ Data file created successfully")
    else:
        print("❌ Error: Data file not found")
        fetcher_process.terminate()
        return
    
    # Start HTTP server
    print("\n🌐 Starting web server on http://localhost:8000")
    try:
        server_process = subprocess.Popen([
            sys.executable,
            '-m',
            'http.server',
            '8000'
        ])
        
        print("\n" + "=" * 60)
        print("✅ Dashboard is running!")
        print("=" * 60)
        print(f"📊 Dashboard: http://localhost:8000")
        print(f"📡 Data updates: Every 10 seconds")
        print(f"⌨️  Press Ctrl+C to stop")
        print("=" * 60)
        
        # Keep running
        fetcher_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        fetcher_process.terminate()
        if 'server_process' in locals():
            server_process.terminate()
        print("✅ Dashboard stopped")

if __name__ == "__main__":
    main()