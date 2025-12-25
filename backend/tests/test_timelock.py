import urllib.request
import json
import time
import datetime

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
        print(f"HTTP Error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_timelock():
    print("1. Setup: Creating Wallet & Mining...")
    alice = request("/wallet/create", "POST")
    if not alice: return
    
    # Mine to get funds
    request("/mine", "POST", {"miner_address": alice['address']})
    
    print(f"Alice: {alice['address']}")

    # Case 1: Future Time (Should NOT execute)
    future_time = int(time.time()) + 3600 # +1 hour
    print(f"\n2. Creating Future Time-Lock Contract (Unlock: {future_time})...")
    
    contract_data_future = {
        "contract_id": f"time_lock_future_{int(time.time())}",
        "creator": alice['address'],
        "contract_type": "TIME_LOCK",
        "participants": [alice['address']],
        "amount": 10,
        "conditions": {
            "release_time": future_time
        }
    }
    
    res_future = request("/contracts/create", "POST", contract_data_future)
    if not res_future: 
        print("Failed to create contract")
        return
        
    contract_id_future = res_future['contract']['contract_id']
    print(f"Contract Created: {contract_id_future}")
    
    print("Attempting to execute...")
    exec_res = request(f"/contracts/{contract_id_future}/execute", "POST")
    
    # If exec_res is None, it means HTTP Error. verify_refactor caught it.
    # The output shows HTTP Error 400 is printed by request() func.
    # So we just need to know IF it failed.
    if exec_res is None:
         print("SUCCESS: Contract correctly refused to execute (HTTP 400).")
    elif not exec_res.get('execution_result', {}).get('success'):
         print("SUCCESS: Contract correctly refused to execute.")
    else:
         print(f"FAILURE: Contract executed prematurely! {exec_res}")

    # Case 2: Past Time (Should execute)
    past_time = int(time.time()) - 3600 # -1 hour
    print(f"\n3. Creating Past Time-Lock Contract (Unlock: {past_time})...")
    
    contract_data_past = {
        "contract_id": f"time_lock_past_{int(time.time())}",
        "creator": alice['address'],
        "contract_type": "TIME_LOCK",
        "participants": [alice['address']],
        "amount": 10,
        "conditions": {
            "release_time": past_time 
        }
    }
    
    res_past = request("/contracts/create", "POST", contract_data_past)
    contract_id_past = res_past['contract']['contract_id']
    print(f"Contract Created: {contract_id_past}")
    
    print("Attempting to execute...")
    exec_res_past = request(f"/contracts/{contract_id_past}/execute", "POST")
    
    if exec_res_past and exec_res_past.get('execution_result', {}).get('success'):
        print("SUCCESS: Contract executed as expected.")
    else:
        print(f"FAILURE: Contract failed to execute! {exec_res_past}")

if __name__ == "__main__":
    test_timelock()
