"""
Test Script - Verify Your Setup
DSCI-560 Lab 4

Run this script to verify your setup is working correctly
"""

import sys
import importlib

def test_imports():
    """Test if all required packages are installed"""
    print("=" * 70)
    print("TESTING PACKAGE INSTALLATION")
    print("=" * 70)
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'polygon': 'polygon-api-client',
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {install_name:.<30} installed")
        except ImportError:
            print(f"✗ {install_name:.<30} NOT installed")
            missing_packages.append(install_name)
    
    if missing_packages:
        print(f"\n⚠ Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✓ All required packages are installed!")
        return True


def test_config():
    """Test if configuration is set up correctly"""
    print("\n" + "=" * 70)
    print("TESTING CONFIGURATION")
    print("=" * 70)
    
    try:
        import config
        
        # Check API key
        if config.POLYGON_API_KEY == "YOUR_API_KEY_HERE":
            print("✗ API Key not configured")
            print("  Please set your Polygon.io API key in config.py")
            return False
        else:
            print(f"✓ API Key configured (first 5 chars: {config.POLYGON_API_KEY[:5]}...)")
        
        # Check stock tickers
        if config.STOCK_TICKERS:
            print(f"✓ Stock tickers configured: {', '.join(config.STOCK_TICKERS[:3])}...")
        else:
            print("⚠ No stock tickers configured")
            print("  Add stock tickers to config.STOCK_TICKERS")
        
        # Check other settings
        print(f"✓ Database path: {config.DATABASE_PATH}")
        print(f"✓ Initial capital: ${config.INITIAL_CAPITAL:,}")
        print(f"✓ Historical days: {config.HISTORICAL_DAYS}")
        
        return True
        
    except ImportError:
        print("✗ config.py not found")
        return False
    except Exception as e:
        print(f"✗ Error loading config: {str(e)}")
        return False


def test_database_creation():
    """Test if database can be created"""
    print("\n" + "=" * 70)
    print("TESTING DATABASE CREATION")
    print("=" * 70)
    
    try:
        import sqlite3
        import os
        
        # Try to create a test database
        test_db = "test_stock_data.db"
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                test_data TEXT
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (test_data) VALUES (?)", ("test",))
        conn.commit()
        
        # Query test data
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        conn.close()
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)
        
        if result:
            print("✓ SQLite database operations working correctly")
            return True
        else:
            print("✗ Database query failed")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        return False


def test_polygon_connection():
    """Test connection to Polygon.io API"""
    print("\n" + "=" * 70)
    print("TESTING POLYGON.IO API CONNECTION")
    print("=" * 70)
    
    try:
        import config
        from polygon import RESTClient
        
        if config.POLYGON_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠ Skipping API test - API key not configured")
            return None
        
        # Try to connect to Polygon.io
        client = RESTClient(config.POLYGON_API_KEY)
        
        # Try to get ticker details (doesn't count against rate limit)
        print("Testing API connection with ticker 'AAPL'...")
        
        try:
            ticker_details = client.get_ticker_details("AAPL")
            print(f"✓ API connection successful!")
            print(f"  Company: {ticker_details.name if hasattr(ticker_details, 'name') else 'N/A'}")
            print(f"  Market: {ticker_details.market if hasattr(ticker_details, 'market') else 'N/A'}")
            return True
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                print("✗ API key is invalid")
                print("  Please check your Polygon.io API key")
            elif "429" in str(e):
                print("⚠ Rate limit reached (this is normal)")
                print("  API key is valid but you've hit the rate limit")
            else:
                print(f"✗ API error: {str(e)}")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")
        return False


def test_stock_data_collector():
    """Test if StockDataCollector class works"""
    print("\n" + "=" * 70)
    print("TESTING STOCK DATA COLLECTOR CLASS")
    print("=" * 70)
    
    try:
        from stock_data_collector import StockDataCollector
        import config
        import os
        
        # Create test database
        test_db = "test_collector.db"
        
        # Initialize collector
        collector = StockDataCollector(
            api_key=config.POLYGON_API_KEY,
            db_path=test_db
        )
        
        print("✓ StockDataCollector initialized successfully")
        
        # Test database creation
        if os.path.exists(test_db):
            print("✓ Database file created successfully")
        
        # Check tables
        cursor = collector.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['stock_prices', 'portfolio', 'transactions']
        if all(table in tables for table in expected_tables):
            print(f"✓ All required tables created: {', '.join(expected_tables)}")
        else:
            print(f"⚠ Some tables missing. Found: {', '.join(tables)}")
        
        # Close and cleanup
        collector.close()
        
        if os.path.exists(test_db):
            os.remove(test_db)
        
        return True
        
    except Exception as e:
        print(f"✗ StockDataCollector test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DSCI-560 LAB 4 - SETUP TEST" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {}
    
    # Run tests
    results['packages'] = test_imports()
    results['config'] = test_config()
    results['database'] = test_database_creation()
    results['polygon_api'] = test_polygon_connection()
    results['collector'] = test_stock_data_collector()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len([r for r in results.values() if r is not None])
    passed_tests = sum([1 for r in results.values() if r is True])
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else ("⚠ SKIP" if result is None else "✗ FAIL")
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")
    
    print("\n" + "-" * 70)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! You're ready to start collecting data!")
        print("\nNext steps:")
        print("  1. Review config.py and adjust settings if needed")
        print("  2. Run: python stock_data_collector.py")
        print("  3. Or run: python example_usage.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("  • Install missing packages: pip install -r requirements.txt")
        print("  • Set API key in config.py")
        print("  • Verify internet connection for API tests")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_all_tests()
