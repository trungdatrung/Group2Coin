
import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:5001/api"

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
        # Return None on error but print it to see why
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_all():
    # 1. Setup
    print("[Setup] Creating Wallet & Mining...")
    alice = request("/wallet/create", "POST")
    if not alice: return
    request("/mine", "POST", {"miner_address": alice['address']})
    print(f"Alice: {alice['address']}")

    # ---------------------------------------------------------
    # TEST 1: ESCROW
    # ---------------------------------------------------------
    print("\n[TEST 1] ESCROW Contract")
    # Goal: Require approval from Alice.
    
    cid_escrow = f"escrow_{int(time.time())}"
    data_escrow = {
        "contract_id": cid_escrow,
        "creator": alice['address'],
        "contract_type": "ESCROW",
        "participants": [alice['address']],
        "amount": 10,
        "conditions": {
            "required_approvals": [alice['address']],  # Should wait for Alice
            "received_approvals": []
        }
    }
    
    request("/contracts/create", "POST", data_escrow)
    
    # Try execute (Should Fail)
    print(" - Attempting execution before approval...")
    res = request(f"/contracts/{cid_escrow}/execute", "POST")
    if res is None or not res.get('execution_result', {}).get('success'):
        print("   -> Success (Correctly failed execution)")
    else:
        print(f"   -> FAILURE (Executed prematurely!) {res}")

    # Approve
    print(" - Alice approving...")
    request(f"/contracts/{cid_escrow}/approve", "POST", {"approver": alice['address']})
    
    # Try execute (Should Success)
    print(" - Attempting execution after approval...")
    res = request(f"/contracts/{cid_escrow}/execute", "POST")
    if res and res.get('execution_result', {}).get('success'):
        print("   -> Success (Executed correctly)")
    else:
        print(f"   -> FAILURE (Did not execute) {res}")


    # ---------------------------------------------------------
    # TEST 2: RECURRING
    # ---------------------------------------------------------
    print("\n[TEST 2] RECURRING Contract")
    
    cid_recurring = f"recurring_{int(time.time())}"
    data_recurring = {
        "contract_id": cid_recurring,
        "creator": alice['address'],
        "contract_type": "RECURRING",
        "participants": [alice['address']],
        "amount": 5,
        "conditions": {
            "interval": 1,        # 1 second
            "max_payments": 2,
            "recipient": alice['address']
        }
    }
    
    request("/contracts/create", "POST", data_recurring)
    
    # Sleep to let interval pass
    time.sleep(2)
    
    print(" - Attempting execution (Payment 1)...")
    res = request(f"/contracts/{cid_recurring}/execute", "POST")
    if res and res.get('execution_result', {}).get('success'):
        print("   -> Success (Payment 1 executed)")
    else:
        print(f"   -> FAILURE (Payment 1 failed) {res}")


    # ---------------------------------------------------------
    # TEST 3: CONDITIONAL (Balance)
    # ---------------------------------------------------------
    print("\n[TEST 3] CONDITIONAL Contract (Balance)")
    
    cid_cond = f"cond_{int(time.time())}"
    data_cond = {
        "contract_id": cid_cond,
        "creator": alice['address'],
        "contract_type": "CONDITIONAL",
        "participants": [alice['address']],
        "amount": 5,
        "conditions": {
            "condition_type": "balance_threshold",
            "target_address": alice['address'],
            "threshold": 1000000, # Impossible amount
            "recipient": alice['address']
        }
    }
    
    request("/contracts/create", "POST", data_cond)
    
    print(" - Attempting execution (Should Fail due to low balance)...")
    res = request(f"/contracts/{cid_cond}/execute", "POST")
    if res is None or not res.get('execution_result', {}).get('success'):
        print("   -> Success (Correctly failed)")
    else:
        print(f"   -> FAILURE (Executed prematurely!) {res}")

if __name__ == "__main__":
    test_all()
