"""
Flask API Testing Script
Make sure the Flask server is running before executing this script
"""

import json

import requests


def test_blockchain_api():
    """Test all blockchain Flask API endpoints"""

    base_url = "http://localhost:5000"

    print("=" * 60)
    print("Blockchain Flask API Test Results")
    print("=" * 60)

    # Test 1: Get entire blockchain
    print("\n1. GET /blockchain")
    try:
        response = requests.get(f"{base_url}/blockchain")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Blockchain length: {data['length']}")
            print(f"   Block name: {data['block_name']}")
            print(f"   Valid: {data['is_valid']}")
            print(f"   Number of blocks: {len(data['chain'])}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Get specific block
    print("\n2. GET /block/0")
    try:
        response = requests.get(f"{base_url}/block/0")
        if response.status_code == 200:
            block = response.json()
            print(f"   ✓ Success! Block #{block['index']}")
            print(f"   Hash: {block['hash'][:32]}...")
            print(f"   Data: {block['data']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Validate blockchain
    print("\n3. GET /validate")
    try:
        response = requests.get(f"{base_url}/validate")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! {data['message']}")
            print(f"   Blockchain is {'VALID' if data['is_valid'] else 'INVALID'}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Get pending data
    print("\n4. GET /pending")
    try:
        response = requests.get(f"{base_url}/pending")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Pending data:")
            print(f"   {data['pending_data']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 5: Get full blockchain details
    print("\n5. Complete blockchain data")
    try:
        response = requests.get(f"{base_url}/blockchain")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Complete blockchain retrieved")
            print(f"\n   Blockchain Details:")
            for i, block in enumerate(data["chain"]):
                print(f"\n   Block #{i}:")
                print(f"     Hash: {block['hash'][:32]}...")
                print(
                    f"     Previous Hash: {block['previous_hash'][:32]}..."
                    if len(block["previous_hash"]) > 10
                    else f"     Previous Hash: {block['previous_hash']}"
                )
                print(f"     Nonce: {block['nonce']}")
                print(f"     Data: {block['data']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    print("\nEnsure Flask server is running before testing")
    print("Uncomment 'run CryptoChain' in Program_Test.txt and run: python Main.py\n")

    input("Press Enter to start tests... ")
    test_blockchain_api()
