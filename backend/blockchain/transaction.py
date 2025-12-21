"""
Transaction class for handling cryptocurrency transactions
"""
import time
import uuid
from utils.crypto import calculate_hash, sign_data, verify_signature


class Transaction:
    """
    Represents a transaction in the blockchain
    """
    
    def __init__(self, sender_address, recipient, amount, public_key=None, signature=None, timestamp=None, nonce=None):
        """
        Initialize a transaction
        Args:
            sender_address: Wallet address of sender (or 'MINING_REWARD')
            recipient: Wallet address of recipient
            amount: Amount to transfer
            public_key: Public key of sender (required for verification)
            signature: Digital signature
            timestamp: Transaction timestamp
            nonce: Unique identifier to prevent replay attacks
        """
        self.sender = sender_address
        self.recipient = recipient
        self.amount = amount
        self.public_key = public_key
        self.signature = signature
        self.timestamp = timestamp or time.time()
        self.nonce = nonce or str(uuid.uuid4())
    
    def to_dict(self):
        """
        Convert transaction to dictionary
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'nonce': self.nonce
        }
    
    def calculate_hash(self):
        """
        Calculate hash of transaction (excluding signature)
        """
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return calculate_hash(transaction_data)
    
    def sign_transaction(self, private_key):
        """
        Sign the transaction with private key
        """
        if self.sender == 'MINING_REWARD':
            return
        
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        
        self.signature = sign_data(private_key, transaction_data)
    
    def is_valid(self):
        """
        Verify transaction signature and validity
        """
        if self.sender == 'MINING_REWARD':
            return True
        
        if not self.signature or not self.public_key:
            return False
        
        # Verify that the provided public key actually matches the sender address
        # This prevents someone from using their own valid keys to sign a tx for someone else's address
        # Assuming address is the first 40 chars of hash of public key (standard in this app)
        calculated_address = calculate_hash(self.public_key)[:40]
        if calculated_address != self.sender:
            return False

        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        
        return verify_signature(self.public_key, transaction_data, self.signature)
