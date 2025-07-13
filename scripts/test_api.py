#!/usr/bin/env python3
"""
Simple test script for the sloptimize API
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"

def test_api():
    """Test the API endpoints"""
    
    print("Testing sloptimize API...")
    
    # Test health check
    print("\n1. Testing health check...")
    response = requests.get(f"{API_BASE}/")
    print(f"Health check: {response.status_code} - {response.json()}")
    
    # Submit a test repository
    print("\n2. Submitting test repository...")
    test_repo = {
        "repo_url": "https://github.com/octocat/Hello-World.git"
    }
    
    response = requests.post(f"{API_BASE}/process-repository", json=test_repo)
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"Job submitted: {job_id}")
        
        # Monitor job progress
        print("\n3. Monitoring job progress...")
        for i in range(30):  # Wait up to 5 minutes
            response = requests.get(f"{API_BASE}/jobs/{job_id}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"Status: {status['status']} - Progress: {status['progress_percent']:.1f}%")
                
                if status['status'] in ['completed', 'failed']:
                    break
                    
            time.sleep(10)
        
        # Get results
        print("\n4. Getting results...")
        response = requests.get(f"{API_BASE}/jobs/{job_id}/results?limit=5")
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} optimization results")
            for result in results[:3]:  # Show top 3
                print(f"  - {result['file_path']}: score {result['score']}")
        
    else:
        print(f"Failed to submit job: {response.status_code} - {response.text}")
    
    # Test job listing
    print("\n5. Testing job listing...")
    response = requests.get(f"{API_BASE}/jobs")
    if response.status_code == 200:
        jobs = response.json()
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"  - {job['job_id']}: {job['status']}")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")