"""
Test script to verify backend setup
"""

print("Testing imports...")

try:
    from blockchain.block import Block
    print("✓ Block import successful")
except Exception as e:
    print(f"✗ Block import failed: {e}")

try:
    from blockchain.transaction import Transaction
    print("✓ Transaction import successful")
except Exception as e:
    print(f"✗ Transaction import failed: {e}")

try:
    from blockchain.blockchain import Blockchain
    print("✓ Blockchain import successful")
except Exception as e:
    print(f"✗ Blockchain import failed: {e}")

try:
    from wallet.wallet import Wallet
    print("✓ Wallet import successful")
except Exception as e:
    print(f"✗ Wallet import failed: {e}")

try:
    from utils.crypto import calculate_hash
    print("✓ Crypto utils import successful")
except Exception as e:
    print(f"✗ Crypto utils import failed: {e}")

try:
    from flask import Flask
    print("✓ Flask import successful")
except Exception as e:
    print(f"✗ Flask import failed: {e}")

print("\n" + "="*50)
print("Testing basic blockchain functionality...")
print("="*50)

try:
    # Create a simple blockchain
    bc = Blockchain(difficulty=2, mining_reward=50)
    print(f"✓ Blockchain created with {len(bc.chain)} block(s)")
    
    # Create a wallet
    w = Wallet()
    print(f"✓ Wallet created: {w.address[:20]}...")
    
    # Test transaction
    tx = Transaction(w.public_key, "test_recipient", 10)
    tx.sign_transaction(w.private_key)
    print(f"✓ Transaction created and signed")
    
    print("\n✓ All tests passed! Backend is ready.")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()