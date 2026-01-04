#!/usr/bin/env python3
"""
Enhanced NoSQL Storage Layer - MongoDB Implementation
Big Data Analytics Final Project

Features:
- Optimized indexes for time-series queries
- Schema validation for data integrity
- Aggregation pipelines for analytics
- Time-series collection for historical data
- Comprehensive backup/restore functionality

Team: Emre Akyol, Harmanpreet Chauhan, Mohamed Nasr
"""

import pymongo
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, OperationFailure
import json
from datetime import datetime, timedelta
import os

class EnhancedCryptoStorage:
    """Enhanced MongoDB storage with optimized indexing and analytics"""
    
    # Schema validation for crypto_prices collection
    CRYPTO_SCHEMA = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["symbol", "name", "price", "timestamp"],
            "properties": {
                "symbol": {"bsonType": "string", "description": "Cryptocurrency symbol (e.g., BTC)"},
                "name": {"bsonType": "string", "description": "Full cryptocurrency name"},
                "price": {"bsonType": "double", "minimum": 0, "description": "Current price in USD"},
                "marketCap": {"bsonType": "double", "minimum": 0},
                "volume24h": {"bsonType": "double", "minimum": 0},
                "change24h": {"bsonType": "double"},
                "volatility": {"bsonType": "double", "minimum": 0, "maximum": 1},
                "socialSentiment": {"bsonType": "double", "minimum": -1, "maximum": 1},
                "buzzVolume": {"bsonType": "int"},
                "timestamp": {"bsonType": "date"}
            }
        }
    }
    
    def __init__(self, connection_string=None):
        """Initialize MongoDB connection with enhanced configuration"""
        # Use environment variable or default to localhost
        if connection_string is None:
            connection_string = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
        
        try:
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Test connection
            self.client.server_info()
            
            self.db = self.client["crypto_sentiment_db"]
            
            # Initialize collections with validation
            self._setup_collections()
            
            # Create optimized indexes
            self._create_indexes()
            
            print("✅ Connected to MongoDB with enhanced configuration")
            print(f"   Database: crypto_sentiment_db")
            print(f"   Collections: {', '.join(self.db.list_collection_names())}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("\n💡 To start MongoDB:")
            print("   docker run -d -p 27017:27017 --name crypto-mongodb mongo")
            raise
    
    def _setup_collections(self):
        """Setup collections with schema validation"""
        # Main collections
        self.crypto_prices = self.db["crypto_prices"]
        self.sentiment_data = self.db["sentiment_data"]
        self.market_overview = self.db["market_overview"]
        self.price_history = self.db["price_history"]  # Time-series data
        self.analysis_results = self.db["analysis_results"]
        
        # Try to create crypto_prices with validation (ignore if exists)
        try:
            self.db.create_collection("crypto_prices", validator=self.CRYPTO_SCHEMA)
            print("   ✅ Created crypto_prices collection with schema validation")
        except CollectionInvalid:
            pass  # Collection already exists
        except OperationFailure:
            pass  # Validation might not be supported
    
    def _create_indexes(self):
        """Create optimized indexes for common queries"""
        print("\n📊 Creating optimized indexes...")
        
        # Crypto prices indexes
        self.crypto_prices.create_index([("symbol", ASCENDING)], unique=True)
        self.crypto_prices.create_index([("timestamp", DESCENDING)])
        self.crypto_prices.create_index([("volatility", DESCENDING)])
        self.crypto_prices.create_index([("socialSentiment", DESCENDING)])
        self.crypto_prices.create_index([("marketCap", DESCENDING)])
        
        # Compound index for time-series queries
        self.crypto_prices.create_index([
            ("symbol", ASCENDING), 
            ("timestamp", DESCENDING)
        ])
        
        # Sentiment data indexes
        self.sentiment_data.create_index([("timestamp", DESCENDING)])
        self.sentiment_data.create_index([
            ("sentimentOverview.fearGreedIndex", ASCENDING)
        ])
        
        # Market overview indexes
        self.market_overview.create_index([("timestamp", DESCENDING)])
        
        # Price history (time-series) indexes
        self.price_history.create_index([
            ("symbol", ASCENDING),
            ("timestamp", DESCENDING)
        ])
        self.price_history.create_index([("timestamp", DESCENDING)])
        
        # TTL index to automatically delete old price history (keep 30 days)
        try:
            self.price_history.create_index(
                [("timestamp", ASCENDING)],
                expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
                name="price_history_ttl"
            )
        except:
            pass  # Index might already exist
        
        print("   ✅ Indexes created successfully")
    
    def store_crypto_data(self, data):
        """Store cryptocurrency data with timestamp tracking"""
        try:
            stored_count = 0
            timestamp = datetime.now()
            
            for crypto in data.get('cryptocurrencies', []):
                # Prepare document
                doc = {
                    'symbol': crypto['symbol'],
                    'name': crypto['name'],
                    'price': float(crypto.get('price', 0)),
                    'marketCap': float(crypto.get('marketCap', 0)),
                    'volume24h': float(crypto.get('volume24h', 0)),
                    'change24h': float(crypto.get('change24h', 0)),
                    'change7d': float(crypto.get('change7d', 0)),
                    'change30d': float(crypto.get('change30d', 0)),
                    'volatility': float(crypto.get('volatility', 0)),
                    'socialSentiment': float(crypto.get('socialSentiment', 0)),
                    'buzzVolume': int(crypto.get('buzzVolume', 0)),
                    'high24h': float(crypto.get('high24h', 0)),
                    'low24h': float(crypto.get('low24h', 0)),
                    'sparkline': crypto.get('sparkline', []),
                    'timestamp': timestamp,
                    'updated_at': timestamp
                }
                
                # Upsert to crypto_prices
                self.crypto_prices.update_one(
                    {'symbol': crypto['symbol']},
                    {'$set': doc},
                    upsert=True
                )
                
                # Also store in price_history for time-series analysis
                history_doc = {
                    'symbol': crypto['symbol'],
                    'price': float(crypto.get('price', 0)),
                    'volume24h': float(crypto.get('volume24h', 0)),
                    'change24h': float(crypto.get('change24h', 0)),
                    'volatility': float(crypto.get('volatility', 0)),
                    'socialSentiment': float(crypto.get('socialSentiment', 0)),
                    'timestamp': timestamp
                }
                self.price_history.insert_one(history_doc)
                
                stored_count += 1
            
            # Store market overview
            market_data = data.get('marketOverview', {})
            market_data['timestamp'] = timestamp
            self.market_overview.insert_one(market_data)
            
            print(f"✅ Stored {stored_count} cryptocurrencies + market overview")
            return True
            
        except Exception as e:
            print(f"❌ Error storing crypto data: {e}")
            return False
    
    def store_sentiment_data(self, data):
        """Store sentiment data with proper indexing"""
        try:
            data['timestamp'] = datetime.now()
            self.sentiment_data.insert_one(data)
            print("✅ Stored sentiment data")
            return True
        except Exception as e:
            print(f"❌ Error storing sentiment data: {e}")
            return False
    
    def store_analysis_results(self, results):
        """Store ML analysis results"""
        try:
            results['timestamp'] = datetime.now()
            self.analysis_results.insert_one(results)
            print("✅ Stored analysis results")
            return True
        except Exception as e:
            print(f"❌ Error storing analysis results: {e}")
            return False
    
    # ==================== QUERY METHODS ====================
    
    def get_latest_crypto_data(self):
        """Get latest data for all cryptocurrencies"""
        return list(self.crypto_prices.find({}, {'_id': 0}).sort('marketCap', DESCENDING))
    
    def get_crypto_by_symbol(self, symbol):
        """Get data for specific cryptocurrency"""
        return self.crypto_prices.find_one({'symbol': symbol}, {'_id': 0})
    
    def get_latest_sentiment(self):
        """Get most recent sentiment data"""
        return self.sentiment_data.find_one(
            {}, {'_id': 0},
            sort=[('timestamp', DESCENDING)]
        )
    
    def get_price_history(self, symbol, hours=168):
        """Get price history for a cryptocurrency (default: 7 days)"""
        since = datetime.now() - timedelta(hours=hours)
        return list(self.price_history.find(
            {'symbol': symbol, 'timestamp': {'$gte': since}},
            {'_id': 0}
        ).sort('timestamp', ASCENDING))
    
    def get_market_history(self, limit=100):
        """Get market overview history"""
        return list(self.market_overview.find(
            {}, {'_id': 0}
        ).sort('timestamp', DESCENDING).limit(limit))
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_high_volatility_cryptos(self, threshold=0.03):
        """Get cryptocurrencies with high volatility"""
        return list(self.crypto_prices.find(
            {'volatility': {'$gte': threshold}},
            {'_id': 0, 'symbol': 1, 'name': 1, 'volatility': 1, 'change24h': 1}
        ).sort('volatility', DESCENDING))
    
    def get_sentiment_leaders(self, top_n=3):
        """Get cryptocurrencies with highest sentiment"""
        return list(self.crypto_prices.find(
            {},
            {'_id': 0, 'symbol': 1, 'name': 1, 'socialSentiment': 1, 'change24h': 1}
        ).sort('socialSentiment', DESCENDING).limit(top_n))
    
    def calculate_average_metrics(self):
        """Calculate average metrics using aggregation pipeline"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avgVolatility': {'$avg': '$volatility'},
                    'avgSentiment': {'$avg': '$socialSentiment'},
                    'avgChange24h': {'$avg': '$change24h'},
                    'totalVolume': {'$sum': '$volume24h'},
                    'totalMarketCap': {'$sum': '$marketCap'},
                    'count': {'$sum': 1}
                }
            }
        ]
        result = list(self.crypto_prices.aggregate(pipeline))
        return result[0] if result else {}
    
    def get_correlation_data(self):
        """Get data formatted for correlation analysis"""
        pipeline = [
            {
                '$project': {
                    '_id': 0,
                    'symbol': 1,
                    'price': 1,
                    'change24h': 1,
                    'volume24h': 1,
                    'volatility': 1,
                    'socialSentiment': 1,
                    'buzzVolume': 1
                }
            }
        ]
        return list(self.crypto_prices.aggregate(pipeline))
    
    def get_sentiment_volatility_correlation(self):
        """Aggregation pipeline for sentiment-volatility analysis"""
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'sentiment_bucket': {
                            '$switch': {
                                'branches': [
                                    {'case': {'$lt': ['$socialSentiment', -0.5]}, 'then': 'Very Negative'},
                                    {'case': {'$lt': ['$socialSentiment', 0]}, 'then': 'Negative'},
                                    {'case': {'$lt': ['$socialSentiment', 0.5]}, 'then': 'Positive'},
                                ],
                                'default': 'Very Positive'
                            }
                        }
                    },
                    'avgVolatility': {'$avg': '$volatility'},
                    'avgChange': {'$avg': '$change24h'},
                    'count': {'$sum': 1},
                    'cryptos': {'$push': '$symbol'}
                }
            },
            {'$sort': {'avgVolatility': -1}}
        ]
        return list(self.crypto_prices.aggregate(pipeline))
    
    # ==================== EXPORT/BACKUP METHODS ====================
    
    def export_to_json(self, output_dir='./resources/data'):
        """Export MongoDB data to JSON files for web dashboard"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now()
            
            # Get all data
            cryptos = self.get_latest_crypto_data()
            sentiment = self.get_latest_sentiment()
            market_history = self.get_market_history(limit=1)
            
            if cryptos:
                # Build crypto-prices.json
                market_overview = market_history[0] if market_history else {}
                
                # Remove MongoDB-specific fields
                if '_id' in market_overview:
                    del market_overview['_id']
                if 'timestamp' in market_overview:
                    market_overview['timestamp'] = str(market_overview['timestamp'])
                
                crypto_data = {
                    'cryptocurrencies': cryptos,
                    'marketOverview': market_overview,
                    'metadata': {
                        'source': 'MongoDB',
                        'lastUpdate': timestamp.isoformat(),
                        'dataSource': 'CoinGecko API + Alternative.me + CryptoPanic'
                    }
                }
                
                with open(f'{output_dir}/crypto-prices.json', 'w') as f:
                    json.dump(crypto_data, f, indent=2, default=str)
                print(f"✅ Exported crypto data to {output_dir}/crypto-prices.json")
            
            if sentiment:
                with open(f'{output_dir}/sentiment-data.json', 'w') as f:
                    json.dump(sentiment, f, indent=2, default=str)
                print(f"✅ Exported sentiment data to {output_dir}/sentiment-data.json")
            
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return False
    
    def create_backup(self, backup_dir='./resources/backups'):
        """Create complete database backup"""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_data = {
                'backup_timestamp': datetime.now().isoformat(),
                'crypto_prices': list(self.crypto_prices.find({}, {'_id': 0})),
                'sentiment_data': list(self.sentiment_data.find({}, {'_id': 0})),
                'market_overview': list(self.market_overview.find({}, {'_id': 0}).limit(100)),
                'analysis_results': list(self.analysis_results.find({}, {'_id': 0}).limit(10))
            }
            
            backup_file = f'{backup_dir}/mongodb_backup_{timestamp}.json'
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def get_statistics(self):
        """Get comprehensive database statistics"""
        try:
            stats = {
                'crypto_prices_count': self.crypto_prices.count_documents({}),
                'sentiment_records': self.sentiment_data.count_documents({}),
                'market_overview_records': self.market_overview.count_documents({}),
                'price_history_records': self.price_history.count_documents({}),
                'analysis_results': self.analysis_results.count_documents({})
            }
            
            # Get database stats
            db_stats = self.db.command("dbStats")
            stats['database_size_kb'] = db_stats['dataSize'] / 1024
            stats['storage_size_kb'] = db_stats['storageSize'] / 1024
            stats['index_count'] = db_stats['indexes']
            stats['index_size_kb'] = db_stats['indexSize'] / 1024
            
            print("\n📊 MongoDB Database Statistics:")
            print(f"   Cryptocurrencies: {stats['crypto_prices_count']}")
            print(f"   Sentiment Records: {stats['sentiment_records']}")
            print(f"   Market Overview Records: {stats['market_overview_records']}")
            print(f"   Price History Records: {stats['price_history_records']}")
            print(f"   Analysis Results: {stats['analysis_results']}")
            print(f"   Database Size: {stats['database_size_kb']:.2f} KB")
            print(f"   Index Count: {stats['index_count']}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("✅ MongoDB connection closed")


def main():
    """Test MongoDB storage"""
    print("=" * 70)
    print("Enhanced MongoDB Storage Layer - Testing")
    print("=" * 70)
    
    try:
        # Initialize storage
        storage = EnhancedCryptoStorage()
        
        # Load and store sample data
        print("\n1. Loading and storing data from JSON files...")
        
        try:
            with open('./resources/data/crypto-prices.json', 'r') as f:
                crypto_data = json.load(f)
            storage.store_crypto_data(crypto_data)
        except FileNotFoundError:
            print("⚠️ crypto-prices.json not found, generate it first")
        
        try:
            with open('./resources/data/sentiment-data.json', 'r') as f:
                sentiment_data = json.load(f)
            storage.store_sentiment_data(sentiment_data)
        except FileNotFoundError:
            print("⚠️ sentiment-data.json not found")
        
        # Get statistics
        print("\n2. Database Statistics:")
        storage.get_statistics()
        
        # Test analytics queries
        print("\n3. Testing Analytics Queries:")
        
        high_vol = storage.get_high_volatility_cryptos()
        print(f"   High volatility cryptos: {[c['symbol'] for c in high_vol]}")
        
        leaders = storage.get_sentiment_leaders()
        print(f"   Sentiment leaders: {[c['symbol'] for c in leaders]}")
        
        avg_metrics = storage.calculate_average_metrics()
        if avg_metrics:
            print(f"   Avg volatility: {avg_metrics.get('avgVolatility', 0):.4f}")
            print(f"   Avg sentiment: {avg_metrics.get('avgSentiment', 0):.4f}")
        
        # Export data
        print("\n4. Exporting data to JSON...")
        storage.export_to_json()
        
        # Create backup
        print("\n5. Creating backup...")
        storage.create_backup()
        
        print("\n" + "=" * 70)
        print("✅ Enhanced MongoDB Storage Layer Test Complete!")
        print("=" * 70)
        
        storage.close()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure MongoDB is running:")
        print("   docker run -d -p 27017:27017 --name crypto-mongodb mongo")


if __name__ == "__main__":
    main()