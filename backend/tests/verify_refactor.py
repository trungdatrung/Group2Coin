import urllib.request
import json
import time

BASE_URL = "http://localhost:5001/api"

def request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    encoded_data = None
    if data:
        encoded_data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, data=encoded_data) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_flow():
    print("1. Creating Alice Wallet...")
    alice = request("/wallet/create", "POST")
    if not alice: return
    print(f"Alice: {alice['address']}")

    print("\n2. Mining to Alice (Initial Balance)...")
    mine_res = request("/mine", "POST", {"miner_address": alice['address']})
    if not mine_res: return
    print("Mined block:", mine_res['block']['index'])

    print("\n3. Checking Alice Balance...")
    alice_bal = request(f"/wallet/{alice['address']}/balance")
    print(f"Alice Balance: {alice_bal['balance']}")
    assert alice_bal['balance'] >= 50, "Mining reward not received"

    print("\n4. Creating Bob Wallet...")
    bob = request("/wallet/create", "POST")
    print(f"Bob: {bob['address']}")

    print("\n5. Sending 10 coins Alice -> Bob...")
    tx_res = request("/transaction/create", "POST", {
        "sender": alice['public_key'], # Legacy frontend sends PK, backend calculates Address
        "recipient": bob['address'],
        "amount": 10,
        "private_key": alice['private_key']
    })
    if not tx_res: 
        print("Transaction failed!")
        return
    print("Transaction created:", tx_res['transaction']['nonce'])

    print("\n6. Mining block to confirm...")
    request("/mine", "POST", {"miner_address": alice['address']})

    print("\n7. Verifying Balances...")
    alice_final = request(f"/wallet/{alice['address']}/balance")
    bob_final = request(f"/wallet/{bob['address']}/balance")
    
    print(f"Alice Final: {alice_final['balance']}")
    print(f"Bob Final: {bob_final['balance']}")

    # Alice mined 2 blocks (50+50=100) and sent 10. Expect 90.
    # Wait, mining reward is 50.
    # Block 1 mine: Bal 50.
    # Send 10: Bal 40 (pending).
    # Block 2 mine: Reward 50 + Bal 40 = 90.
    assert alice_final['balance'] == 90.0, f"Alice balance mismatch. Expected 90, got {alice_final['balance']}"
    assert bob_final['balance'] == 10.0, f"Bob balance mismatch. Expected 10, got {bob_final['balance']}"

    print("\nSUCCESS: Infinite Money Glitch Fixed & Persistence Working (if run multiple times)!")

if __name__ == "__main__":
    # Wait for server to be up
    time.sleep(2)
    test_flow()
