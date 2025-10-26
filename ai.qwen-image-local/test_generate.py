#!/usr/bin/env python3
"""
Simple test script for the Qwen Image API
"""
import requests
import json

# API endpoint
url = "http://localhost:8000/generate"

# Simple test with minimal parameters
print("Testing with minimal parameters...")
data = {
    "prompt": "a beautiful sunset over mountains"
}

try:
    response = requests.post(url, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")

    if response.status_code == 422:
        print("\n422 Validation Error Details:")
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 200:
        # Save the image
        with open("test_output.png", "wb") as f:
            f.write(response.content)
        print("\n✓ Success! Image saved to test_output.png")
    else:
        print(f"\nUnexpected response:")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
