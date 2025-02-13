import requests
import os
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
DATA_DIR = "C:\\Users\\DELL\\TDS\\prj1\\data"  # or "C:\\Users\\DELL\\TDS\\prj1\\data" for Windows

def test_endpoint(description, endpoint, method="GET", data=None, expected_status=200):
    print(f"\nTesting: {description}")
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}/{endpoint}")
        else:
            response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
        
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code} (Expected: {expected_status})")
        print(f"Duration: {duration:.2f} seconds")
        
        if duration > 20:
            print("⚠️ WARNING: Response took longer than 20 seconds!")
            
        if response.status_code == expected_status:
            print("✅ Test passed")
            return True
        else:
            print("❌ Test failed")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def run_tests():
    successful_tests = 0
    total_tests = 0
    
    print("🚀 Starting API Tests\n")
    
    # Test Phase A Tasks
    tests = [
        {
            "description": "A1: Generate Data",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Install uv and run the datagen script"},
            "expected_status": 200
        },
        {
            "description": "A2: Format Markdown",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Format /data/format.md using prettier"},
            "expected_status": 200
        },
        {
            "description": "A3: Count Wednesdays",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Count how many Wednesdays are in /data/dates.txt"},
            "expected_status": 200
        },
        {
            "description": "A4: Sort Contacts",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Sort the contacts in /data/contacts.json by last name"},
            "expected_status": 200
        },
        {
            "description": "A5: Recent Logs",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Get first line of 10 most recent log files"},
            "expected_status": 200
        },
        {
            "description": "A6: Extract Markdown Titles",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Create index of markdown titles from /data/docs/"},
            "expected_status": 200
        },
        {
            "description": "A7: Extract Email Sender",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Extract sender's email from /data/email.txt"},
            "expected_status": 200
        },
        {
            "description": "A8: Extract Credit Card",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Get the credit card number from /data/credit-card.png"},
            "expected_status": 200
        },
        {
            "description": "A9: Find Similar Comments",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Find most similar comments in /data/comments.txt"},
            "expected_status": 200
        },
        {
            "description": "A10: Calculate Gold Ticket Sales",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Calculate total sales for Gold tickets"},
            "expected_status": 200
        }
    ]
    
    # Add Phase B Tests
    phase_b_tests = [
        {
            "description": "B3: Fetch API Data",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Fetch data from https://api.example.com/data"},
            "expected_status": 200
        },
        {
            "description": "B4: Clone Git Repo",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Clone https://github.com/example/repo"},
            "expected_status": 200
        },
        {
            "description": "B5: Run SQL Query",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Run SELECT * FROM users on database.db"},
            "expected_status": 200
        },
        {
            "description": "B6: Scrape Website",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Extract data from https://example.com"},
            "expected_status": 200
        },
        {
            "description": "B7: Compress Image",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Compress image.jpg to 800x600"},
            "expected_status": 200
        },
        {
            "description": "B8: Transcribe Audio",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Transcribe audio.mp3 to text"},
            "expected_status": 200
        },
        {
            "description": "B9: Convert Markdown",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Convert README.md to HTML"},
            "expected_status": 200
        },
        {
            "description": "B10: Filter CSV",
            "endpoint": "filter-csv?column=status&value=active",
            "method": "GET",
            "expected_status": 200
        }
    ]
    
    tests.extend(phase_b_tests)
    
    # Security Tests
    security_tests = [
        {
            "description": "Security: Block Access Outside /data",
            "endpoint": "read?path=../sensitive.txt",
            "method": "GET",
            "expected_status": 403
        },
        {
            "description": "Security: Prevent File Deletion",
            "endpoint": "run",
            "method": "POST",
            "data": {"task": "Delete /data/test.txt"},
            "expected_status": 403
        }
    ]
    
    tests.extend(security_tests)
    
    # Run all tests
    for test in tests:
        total_tests += 1
        if test_endpoint(**test):
            successful_tests += 1
            
    # Print summary
    print(f"\n📊 Test Summary")
    print(f"Passed: {successful_tests}/{total_tests} tests")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    run_tests()