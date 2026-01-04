#!/usr/bin/env python3
"""
View MongoDB Data - Inspection Tool
Shows what's stored in MongoDB database
"""

import pymongo
from pymongo import MongoClient
import json
from datetime import datetime

def view_mongodb_data():
    """View all data stored in MongoDB"""
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["crypto_sentiment_db"]
        
        print("=" * 70)
        print("MongoDB Database Viewer - Crypto Sentiment Analytics")
        print("=" * 70)
        
        # 1. Database Statistics
        print("\n📊 DATABASE STATISTICS")
        print("-" * 70)
        
        stats = db.command("dbStats")
        print(f"Database Name: {stats['db']}")
        print(f"Collections: {stats['collections']}")
        print(f"Documents: {stats['objects']}")
        print(f"Data Size: {stats['dataSize'] / 1024:.2f} KB")
        print(f"Storage Size: {stats['storageSize'] / 1024:.2f} KB")
        
        # 2. Collections Overview
        print("\n📚 COLLECTIONS OVERVIEW")
        print("-" * 70)
        
        collections = db.list_collection_names()
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"\n{collection_name}:")
            print(f"   Total Documents: {count}")
            
            # Get sample document
            sample = db[collection_name].find_one({}, {'_id': 0})
            if sample:
                print(f"   Sample Fields: {list(sample.keys())}")
        
        # 3. Crypto Prices Collection
        print("\n\n💰 CRYPTO PRICES COLLECTION")
        print("-" * 70)
        
        crypto_prices = db["crypto_prices"]
        cryptos = list(crypto_prices.find({}, {'_id': 0}).sort('price', -1))
        
        if cryptos:
            print(f"\nTotal Cryptocurrencies: {len(cryptos)}\n")
            print(f"{'Symbol':<10} {'Name':<15} {'Price':<15} {'Change 24h':<12} {'Market Cap':<15}")
            print("-" * 70)
            
            for crypto in cryptos:
                symbol = crypto.get('symbol', 'N/A')
                name = crypto.get('name', 'N/A')[:14]
                price = crypto.get('price', 0)
                change = crypto.get('change24h', 0)
                mcap = crypto.get('marketCap', 0)
                
                change_str = f"{change:+.2f}%" if change else "N/A"
                mcap_str = f"${mcap/1e9:.2f}B" if mcap else "N/A"
                
                print(f"{symbol:<10} {name:<15} ${price:<14,.2f} {change_str:<12} {mcap_str:<15}")
            
            # Show detailed view of one crypto
            print(f"\n\n📋 DETAILED VIEW - {cryptos[0]['name']} (BTC)")
            print("-" * 70)
            print(json.dumps(cryptos[0], indent=2, default=str))
        
        # 4. Sentiment Data Collection
        print("\n\n😊 SENTIMENT DATA COLLECTION")
        print("-" * 70)
        
        sentiment_data = db["sentiment_data"]
        latest_sentiment = sentiment_data.find_one(
            {}, 
            {'_id': 0},
            sort=[('timestamp', pymongo.DESCENDING)]
        )
        
        if latest_sentiment:
            overview = latest_sentiment.get('sentimentOverview', {})
            print(f"\nOverall Sentiment: {overview.get('overallSentiment', 'N/A')}")
            print(f"Total Mentions: {overview.get('totalMentions', 0):,}")
            print(f"Positive Mentions: {overview.get('positiveMentions', 0):,}")
            print(f"Negative Mentions: {overview.get('negativeMentions', 0):,}")
            print(f"Fear & Greed Index: {overview.get('fearGreedIndex', 'N/A')}")
            
            platforms = latest_sentiment.get('platformAnalysis', {})
            print(f"\n📱 Platform Analysis:")
            for platform, data in platforms.items():
                print(f"   {platform.title()}:")
                print(f"      Sentiment: {data.get('sentimentScore', 'N/A')}")
                print(f"      Volume: {data.get('mentionVolume', 0):,}")
                print(f"      Influence: {data.get('influenceScore', 'N/A')}%")
        
        # 5. Market Overview Collection
        print("\n\n📈 MARKET OVERVIEW HISTORY")
        print("-" * 70)
        
        market_overview = db["market_overview"]
        history_count = market_overview.count_documents({})
        print(f"\nTotal Historical Records: {history_count}")
        
        # Get latest 5 records
        latest_records = list(market_overview.find(
            {},
            {'_id': 0}
        ).sort('timestamp', pymongo.DESCENDING).limit(5))
        
        if latest_records:
            print(f"\nLatest 5 Records:")
            print(f"{'Timestamp':<25} {'Total Market Cap':<20} {'BTC Dominance':<15} {'Fear & Greed':<15}")
            print("-" * 70)
            
            for record in latest_records:
                ts = record.get('timestamp', datetime.now())
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                
                mcap = record.get('totalMarketCap', 0)
                btc_dom = record.get('btcDominance', 0)
                fg = record.get('fearGreedIndex', 0)
                
                print(f"{ts.strftime('%Y-%m-%d %H:%M:%S'):<25} ${mcap/1e12:<19.2f}T {btc_dom:<14.2f}% {fg:<15}")
        
        # 6. Query Examples
        print("\n\n💡 USEFUL MONGODB QUERIES")
        print("-" * 70)
        print("""
# Find specific cryptocurrency:
db.crypto_prices.findOne({symbol: "BTC"})

# Find cryptos with positive change:
db.crypto_prices.find({change24h: {$gt: 0}})

# Get average sentiment:
db.crypto_prices.aggregate([
  {$group: {_id: null, avgSentiment: {$avg: "$socialSentiment"}}}
])

# Sort by market cap:
db.crypto_prices.find().sort({marketCap: -1})

# Count high volatility cryptos:
db.crypto_prices.countDocuments({volatility: {$gt: 0.03}})
        """)
        
        print("\n" + "=" * 70)
        print("✅ MongoDB Data Inspection Complete!")
        print("=" * 70)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("\n💡 Make sure MongoDB is running:")
        print("   docker start crypto-mongodb")
        print("   OR")
        print("   docker run -d -p 27017:27017 --name crypto-mongodb mongo")

if __name__ == "__main__":
    view_mongodb_data()